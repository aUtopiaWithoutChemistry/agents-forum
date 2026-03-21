"""Market data service - Yahoo Finance primary with caching"""
import os
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from threading import Lock
import logging

logger = logging.getLogger(__name__)

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")


class MarketDataService:
    """Service for fetching market data from Yahoo Finance with caching"""

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_lock = Lock()
        self._last_refresh: datetime = datetime.min
        self._refresh_interval = 300  # 5 minutes

    def get_quote(self, ticker: str, force_refresh: bool = False) -> Optional[dict]:
        """Get current quote for a ticker, using cache if available"""
        with self._cache_lock:
            if not force_refresh and ticker in self._cache:
                cached = self._cache[ticker]
                # Use cache if fresh (less than refresh interval)
                if (datetime.now() - cached.get("timestamp", datetime.min)).total_seconds() < self._refresh_interval:
                    return cached

        # Fetch fresh data
        fresh = self._fetch_quote(ticker)
        if fresh:
            with self._cache_lock:
                self._cache[ticker] = fresh
        return fresh

    def _fetch_quote(self, ticker: str) -> Optional[dict]:
        """Fetch fresh quote from Yahoo Finance"""
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

            return {
                "ticker": ticker,
                "name": info.get("shortName", info.get("longName", self._get_name(ticker))),
                "market_type": self._get_market_type(ticker, info),
                "price": price,
                "change": change,
                "changePercent": change_percent,
                "volume": volume,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    def get_batch(self, tickers: List[str], force_refresh: bool = False) -> List[dict]:
        """Get quotes for multiple tickers efficiently using yfinance batch"""
        results = []
        failed = []

        # First pass: collect cached data
        with self._cache_lock:
            for ticker in tickers:
                if ticker in self._cache and not force_refresh:
                    cached = self._cache[ticker]
                    age = (datetime.now() - cached.get("timestamp", datetime.min)).total_seconds()
                    if age < self._refresh_interval:
                        results.append(cached)
                        continue
                failed.append(ticker)

        # Batch fetch failed/missing tickers using yfinance
        if failed:
            try:
                # yfinance supports batch fetching
                tickers_str = " ".join(failed)
                data = yf.download(tickers_str, period="1d", group_by="ticker", progress=False)

                # Also try to get info (names) via Ticker.info for each failed ticker
                # We fetch names by calling info on each ticker in a mini-batch to avoid
                # rate limiting while still getting proper names
                ticker_names = {}
                for ticker in failed:
                    ticker_names[ticker] = self._get_name(ticker)  # fallback

                # Try to get names from fast_info or info (more reliable than batch download)
                for ticker in failed:
                    try:
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        name = info.get("shortName") or info.get("longName")
                        if name:
                            ticker_names[ticker] = name
                    except Exception:
                        pass  # Keep fallback name

                for ticker in failed:
                    try:
                        if len(failed) == 1:
                            row = data
                        else:
                            try:
                                row = data[ticker]
                            except KeyError:
                                # Ticker not in batch response (delisted or invalid)
                                logger.warning(f"Ticker {ticker} not found in batch response, skipping")
                                continue

                        if row.empty:
                            continue

                        if "Close" not in row:
                            logger.warning(f"No Close data for ticker {ticker}, skipping")
                            continue

                        price_val = row["Close"].iloc[-1]
                        if price_val is None or (isinstance(price_val, float) and not (price_val > 0 or price_val < 0)):
                            logger.warning(f"No valid price for ticker {ticker}, skipping")
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
                            "timestamp": datetime.now()
                        }

                        with self._cache_lock:
                            self._cache[ticker] = quote
                        results.append(quote)
                    except Exception as e:
                        logger.error(f"Error parsing batch data for {ticker}: {e}")
                        # Fallback to individual fetch
                        fresh = self._fetch_quote(ticker)
                        if fresh:
                            with self._cache_lock:
                                self._cache[ticker] = fresh
                            results.append(fresh)
            except Exception as e:
                logger.error(f"Batch fetch failed, falling back to individual: {e}")
                # Fallback: fetch individually
                for ticker in failed:
                    fresh = self._fetch_quote(ticker)
                    if fresh:
                        with self._cache_lock:
                            self._cache[ticker] = fresh
                        results.append(fresh)

        return results

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

    def _get_market_type(self, ticker: str, info: dict) -> str:
        """Determine market type"""
        if ticker.startswith("^"):
            return "index"
        if "crypto" in ticker.lower() or "-USD" in ticker:
            return "crypto"
        if ticker.endswith(".HK") or ".SS" in ticker or ".T" in ticker:
            return "international"
        quote_type = info.get("quoteType", "").lower()
        if quote_type:
            return quote_type
        return "stock"

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


# Singleton instance
market_service = MarketDataService()
