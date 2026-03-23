"""Market data service - Massive (Polygon.io) primary with Yahoo Finance fallback and caching"""
import os
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from threading import Lock
import logging

logger = logging.getLogger(__name__)

# Massive (Polygon.io) API configuration
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "")
MASSIVE_BASE_URL = "https://api.polygon.io/v2"

# Cache TTL: 15 minutes (matches data freshness policy for 15-min delayed data)
CACHE_TTL_SECONDS = 900  # 15 minutes

# Failed ticker cache TTL: 1 hour (skip known invalid/delisted tickers for 1 hour)
FAILED_TICKER_CACHE_TTL_SECONDS = 3600  # 1 hour


class MarketDataService:
    """Service for fetching market data with three-tier fallback:
    1. Massive (Polygon.io) - primary, unlimited requests
    2. Yahoo Finance (yfinance) - fallback
    3. Cached data with stale flag - ultimate fallback
    """

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_lock = Lock()
        self._last_refresh: datetime = datetime.min
        self._refresh_interval = CACHE_TTL_SECONDS
        self._last_source_failure: Dict[str, datetime] = {}  # Track source failures for alerting
        self._failed_tickers: Dict[str, datetime] = {}  # Track known invalid/delisted tickers

    def get_quote(self, ticker: str, force_refresh: bool = False) -> Optional[dict]:
        """Get current quote for a ticker with three-tier fallback"""
        with self._cache_lock:
            if not force_refresh and ticker in self._cache:
                cached = self._cache[ticker]
                # Use cache if fresh (less than refresh interval)
                if (datetime.now() - cached.get("timestamp", datetime.min)).total_seconds() < self._refresh_interval:
                    return cached

        # Try three-tier fallback: Massive → Yahoo Finance → Cache
        fresh = self._fetch_quote_with_fallback(ticker)
        if fresh:
            with self._cache_lock:
                self._cache[ticker] = fresh
        return fresh

    def _fetch_quote_with_fallback(self, ticker: str) -> Optional[dict]:
        """Try data sources in order: Massive → Yahoo Finance → cached"""
        # Tier 1: Try Massive (Polygon.io)
        result = self._fetch_from_massive(ticker)
        if result:
            result["data_source"] = "massive"
            return result

        # Tier 2: Try Yahoo Finance
        result = self._fetch_from_yahoo(ticker)
        if result:
            result["data_source"] = "yahoo"
            return result

        # Tier 3: Return stale cached data if available
        with self._cache_lock:
            if ticker in self._cache:
                cached = self._cache[ticker].copy()
                cached["data_source"] = "cache_stale"
                cached["is_stale"] = True
                return cached

        return None

    def _fetch_from_massive(self, ticker: str) -> Optional[dict]:
        """Fetch quote from Massive (Polygon.io) API"""
        if not MASSIVE_API_KEY:
            logger.debug("Massive API key not configured, skipping")
            return None

        try:
            # Convert ticker format for Massive (e.g., AAPL -> AAPL, BTC-USD -> X:BTCUSD)
            massive_ticker = self._convert_ticker_for_massive(ticker)

            url = f"{MASSIVE_BASE_URL}/snapshot/locale/us/markets/stocks/tickers/{massive_ticker}"
            params = {"apiKey": MASSIVE_API_KEY}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK" and "ticker" in data:
                    ticker_data = data["ticker"]
                    day = ticker_data.get("day", {})
                    prev_close = ticker_data.get("prevDay", {})

                    price = day.get("c")
                    prev_close_price = prev_close.get("c")

                    if price:
                        change = price - prev_close_price if prev_close_price else None
                        change_percent = (change / prev_close_price * 100) if prev_close_price and change else None

                        return {
                            "ticker": ticker,
                            "name": ticker_data.get("name", self._get_name(ticker)),
                            "market_type": self._get_market_type_for_ticker(ticker),
                            "price": price,
                            "change": change,
                            "changePercent": change_percent,
                            "volume": day.get("v", 0),
                            "timestamp": datetime.now()
                        }
            elif response.status_code == 404:
                logger.debug(f"Ticker {ticker} not found in Massive")
            else:
                logger.warning(f"Massive API returned status {response.status_code}")

        except requests.exceptions.Timeout:
            logger.warning(f"Massive API timeout for {ticker}")
            self._record_failure("massive")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Massive API error for {ticker}: {e}")
            self._record_failure("massive")
        except Exception as e:
            logger.error(f"Error fetching from Massive for {ticker}: {e}")

        return None

    def _convert_ticker_for_massive(self, ticker: str) -> str:
        """Convert standard ticker format to Massive format"""
        # For crypto, Massive uses X: prefix
        if "-USD" in ticker:
            symbol = ticker.replace("-USD", "")
            return f"X:{symbol}USD"
        # For US stocks, use as-is
        return ticker

    def _record_failure(self, source: str):
        """Record data source failure for alerting"""
        self._last_source_failure[source] = datetime.now()

    def _is_ticker_failed(self, ticker: str) -> bool:
        """Check if ticker is known to be invalid/delisted (cached as failed)"""
        if ticker in self._failed_tickers:
            failed_at = self._failed_tickers[ticker]
            if (datetime.now() - failed_at).total_seconds() < FAILED_TICKER_CACHE_TTL_SECONDS:
                return True
            # Expired, remove from failed list
            del self._failed_tickers[ticker]
        return False

    def _mark_ticker_failed(self, ticker: str):
        """Mark a ticker as known to be invalid/delisted"""
        self._failed_tickers[ticker] = datetime.now()
        logger.debug(f"Marked ticker {ticker} as failed (will skip for {FAILED_TICKER_CACHE_TTL_SECONDS}s)")

    def _fetch_from_yahoo(self, ticker: str) -> Optional[dict]:
        """Fetch quote from Yahoo Finance (fallback)"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            price = info.get("currentPrice") or info.get("regularMarketPrice")
            change = info.get("regularMarketChange")
            change_percent = info.get("regularMarketChangePercent")
            volume = info.get("volume", 0)

            # For indices without change data, calculate from previous close
            if change is None and price:
                prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
                if prev_close:
                    change = price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close else 0

            if price:
                return {
                    "ticker": ticker,
                    "name": info.get("shortName", info.get("longName", self._get_name(ticker))),
                    "market_type": self._get_market_type_for_ticker(ticker),
                    "price": price,
                    "change": change,
                    "changePercent": change_percent,
                    "volume": volume,
                    "timestamp": datetime.now()
                }
        except Exception as e:
            logger.warning(f"Error fetching from Yahoo for {ticker}: {e}")
            self._record_failure("yahoo")
            # Don't mark as permanently failed on network/timeout errors
            return None

    def get_batch(self, tickers: List[str], force_refresh: bool = False) -> List[dict]:
        """Get quotes for multiple tickers with three-tier fallback"""
        results = []
        failed = []

        # First pass: collect cached data
        with self._cache_lock:
            for ticker in tickers:
                if ticker in self._cache and not force_refresh:
                    cached = self._cache[ticker]
                    age = (datetime.now() - cached.get("timestamp", datetime.min)).total_seconds()
                    if age < self._refresh_interval:
                        results.append(cached.copy())
                        continue
                failed.append(ticker)

        if not failed:
            return results

        # Skip known failed/invalid tickers to avoid slow yfinance failures
        truly_failed = []
        for ticker in failed:
            if self._is_ticker_failed(ticker):
                truly_failed.append(ticker)
                logger.debug(f"Skipping known failed ticker: {ticker}")
        failed = [t for t in failed if t not in truly_failed]

        if not failed:
            return results

        # Try Yahoo Finance batch for failed tickers (most reliable for batch)
        yahoo_results = self._fetch_batch_from_yahoo(failed)
        if yahoo_results:
            for quote in yahoo_results:
                results.append(quote)
                with self._cache_lock:
                    self._cache[quote["ticker"]] = quote
            # Remove successfully fetched tickers from failed list
            successful_tickers = {q["ticker"] for q in yahoo_results}
            failed = [t for t in failed if t not in successful_tickers]

        # For remaining failed tickers, try individual fallback
        for ticker in failed:
            quote = self._fetch_quote_with_fallback(ticker)
            if quote:
                results.append(quote)
                with self._cache_lock:
                    self._cache[ticker] = quote

        return results

    def _fetch_batch_from_yahoo(self, tickers: List[str]) -> List[dict]:
        """Batch fetch from Yahoo Finance"""
        if not tickers:
            return []

        try:
            tickers_str = " ".join(tickers)
            # Add timeout to prevent hanging on invalid/delisted tickers
            data = yf.download(tickers_str, period="1d", group_by="ticker", progress=False, threads=True, timeout=10)

            results = []
            ticker_names = {}

            # Get names from batch data first (fast), skip individual ticker.info calls (slow)
            for ticker in tickers:
                ticker_names[ticker] = self._get_name(ticker)

            for ticker in tickers:
                try:
                    if len(tickers) == 1:
                        row = data
                    else:
                        try:
                            row = data[ticker]
                        except KeyError:
                            logger.warning(f"Ticker {ticker} not in batch response")
                            continue

                    if row.empty or "Close" not in row:
                        continue

                    price_val = row["Close"].iloc[-1]
                    if price_val is None or (isinstance(price_val, float) and not (price_val > 0 or price_val < 0)):
                        continue

                    price = float(price_val)
                    prev_close = float(row["Open"].iloc[0]) if len(row) > 0 else price
                    change = price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close else 0

                    quote = {
                        "ticker": ticker,
                        "name": ticker_names.get(ticker, self._get_name(ticker)),
                        "market_type": self._get_market_type_for_ticker(ticker),
                        "price": price,
                        "change": change,
                        "changePercent": change_percent,
                        "volume": int(row["Volume"].iloc[-1]) if "Volume" in row else 0,
                        "timestamp": datetime.now(),
                        "data_source": "yahoo"
                    }
                    results.append(quote)
                except Exception as e:
                    logger.error(f"Error parsing batch data for {ticker}: {e}")
                    continue

            # Mark tickers that were not found as failed
            successful_tickers = {q["ticker"] for q in results}
            for ticker in tickers:
                if ticker not in successful_tickers:
                    self._mark_ticker_failed(ticker)

            return results
        except Exception as e:
            logger.error(f"Batch fetch from Yahoo failed: {e}")
            return []

    def _get_market_type_for_ticker(self, ticker: str) -> str:
        """Determine market type from ticker symbol"""
        if ticker.startswith("^"):
            return "index"
        if "crypto" in ticker.lower() or "-USD" in ticker:
            return "crypto"
        if any(suffix in ticker for suffix in [".HK", ".SS", ".SZ", ".TW", ".T", ".AX", ".KS", ".NS", ".BK", ".MX", ".SA", ".TO", ".L", ".AS", ".DE", ".PA", ".MI", ".MC", ".ST"]):
            return "international"
        if "=X" in ticker or ticker.startswith("^"):
            return "forex"
        return "stock"

    def get_all_cached(self) -> List[dict]:
        """Get all cached quotes"""
        with self._cache_lock:
            return list(self._cache.values())

    def refresh_all(self, tickers: List[str]) -> None:
        """Force refresh all given tickers"""
        self.get_batch(tickers, force_refresh=True)

    def get_history(self, ticker: str, start_date: str, end_date: str) -> Optional[dict]:
        """Get historical data for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                return None

            history = []
            for date, row in hist.iterrows():
                history.append({
                    "date": date.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })

            return {
                "ticker": ticker,
                "name": self._get_name(ticker),
                "history": history
            }
        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            return None

    def search_tickers(self, query: str) -> list:
        """Search for tickers - uses Yahoo Finance"""
        try:
            # Yahoo Finance doesn't have a direct search API
            # Return empty list - frontend can use autocomplete with known tickers
            return []
        except Exception as e:
            logger.error(f"Error searching tickers: {e}")
            return []

    def get_failure_status(self) -> Dict[str, any]:
        """Get current data source failure status for monitoring"""
        now = datetime.now()
        status = {
            "sources": {},
            "all_healthy": True
        }

        for source, last_failure in self._last_source_failure.items():
            time_since_failure = (now - last_failure).total_seconds()
            is_critical = time_since_failure < 300  # Failed in last 5 minutes

            status["sources"][source] = {
                "last_failure": last_failure.isoformat(),
                "seconds_ago": int(time_since_failure),
                "critical": is_critical
            }

            if is_critical:
                status["all_healthy"] = False

        return status

    def _get_name(self, ticker: str) -> str:
        """Get human-readable name for ticker"""
        names = {
            # US Indices
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "Nasdaq",
            "^VIX": "VIX",
            "^RUT": "Russell 2000",
            # International Indices
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng",
            "^GDAXI": "DAX",
            "^FCHI": "CAC 40",
            "^FTSE": "FTSE 100",
            "^AXJO": "ASX 200",
            "^BSESN": "Sensex",
            "^STOXX50E": "Euro Stoxx 50",
            # Bonds
            "^TNX": "10Y Treasury",
            "^TYX": "30Y Treasury",
            "^FVX": "5Y Treasury",
            # Crypto
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "SOL-USD": "Solana",
            "BNB-USD": "BNB",
            "XRP-USD": "XRP",
            "ADA-USD": "Cardano",
            "AVAX-USD": "Avalanche",
            "DOGE-USD": "Dogecoin",
            "DOT-USD": "Polkadot",
            "LINK-USD": "Chainlink",
            "MATIC-USD": "Polygon",
            "UNI-USD": "Uniswap",
            "ATOM-USD": "Cosmos",
            "LTC-USD": "Litecoin",
            # Commodities
            "GC=F": "Gold",
            "SI=F": "Silver",
            "CL=F": "Crude Oil",
            "NG=F": "Natural Gas",
            "HG=F": "Copper",
            "ZC=F": "Corn",
            "ZS=F": "Soybeans",
            "ZW=F": "Wheat",
            "ZL=F": "Soybean Oil",
            "ZO=F": "Oat",
            # China/HK
            "000001.SS": "Shanghai Composite",
            "399001.SZ": "Shenzhen Composite",
            "9988.HK": "Alibaba",
            "0700.HK": "Tencent",
            "9618.HK": "JD.com",
            "3690.HK": "Meituan",
            "1810.HK": "Xiaomi",
            "7200.HK": "SMIC",
            "9868.HK": "Geely",
            "PDD": "Pinduoduo",
            "BIDU": "Baidu",
            "JD": "JD.com",
            "NTES": "NetEase",
            "NIO": "NIO",
            "XPEV": "Xpeng",
            "LI": "Li Auto",
            # Japan
            "9984.T": "SoftBank",
            "7203.T": "Toyota",
            "6752.T": "Panasonic",
            "9432.T": "NTT",
            "9434.T": "SoftBank Corp",
            "8306.T": "Mitsubishi UFJ",
            "8316.T": "Sumitomo Mitsui",
            "8604.T": "Nomura",
            "8021.T": "Fast Retailing",
            "8035.T": "Tokyo Electron",
            "8058.T": "Mitsubishi Corp",
            # Europe
            "ASML.AS": "ASML",
            "SAP.DE": "SAP",
            "SONY.L": "Sony",
            "NVO": "Novo Nordisk",
            "TM": "Toyota",
            "HSBC": "HSBC",
            "SHELL.L": "Shell",
            "BP.L": "BP",
            "REL.L": "Reliance",
            "BHP.L": "BHP",
            "RIO.L": "Rio Tinto",
            "GSK.L": "GSK",
            "AZN.L": "AstraZeneca",
            "TTE.PA": "TotalEnergies",
            "OR.PA": "L'Oréal",
            "AIR.PA": "Airbus",
            "SIE.DE": "Siemens",
            "ALV.DE": "Allianz",
            "DPW.DE": "Deutsche Post",
            # Taiwan/Korea
            "2330.TW": "TSMC",
            "2454.TW": "MediaTek",
            "2382.TW": "ASE Technology",
            "2303.TW": "UMC",
            "3711.TW": "ASE",
            "2308.TW": "Delta Electronics",
            "6409.TW": "Foxconn",
            "2395.TW": "WPG Holdings",
            "0050.KS": "KOSPI 50",
            "0051.KS": "KOSPI 100",
            "068270.KS": "Samsung Biologics",
            "000660.KS": "SK Hynix",
            "051910.KS": "LG Chem",
            "207940.KS": "Samsung SDI",
        }
        return names.get(ticker, ticker)


# Singleton instance
market_service = MarketDataService()
