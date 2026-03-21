'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { marketApi } from '@/lib/api';
import MarketDataCard from '@/components/MarketDataCard';
import StockTreemap from '@/components/StockTreemap';
import TradingDashboard from '@/components/TradingDashboard';

// Comprehensive global market data - ~1000 symbols
// fastRefresh: true = 15s refresh (indices, ETFs), false = 5min refresh (individual stocks)
const TICKER_CATEGORIES: Record<string, { title: string; description: string; tickers: string[]; fastRefresh?: boolean }> = {
  // ===== GLOBAL INDICES =====
  'Global Indices': {
    title: 'Global Indices',
    description: '世界主要大盘指数',
    fastRefresh: true,
    tickers: [
      '^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX',  // US
      '^N225', '^AXJO', '^BSESN',  // Asia
      '000001.SS', '399001.SZ', '^HSI',  // China/HK
      '^GDAXI', '^FCHI', '^FTSE', '^STOXX50E',  // Europe
    ],
  },

  // ===== US TECHNOLOGY =====
  'US Technology': {
    title: 'US Technology',
    description: '美国科技股',
    tickers: [
      'AAPL', 'MSFT', 'NVDA', 'AMZN', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AMD', 'INTC', 'QCOM',
      'TXN', 'ADI', 'AVGO', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS', 'PANW', 'CRWD',
      'NET', 'ZS', 'OKTA', 'DDOG', 'MDB', 'COIN', 'RBLX', 'UBER', 'LYFT', 'SNOW',
      'NET', 'VEEV', 'TWLO', 'ZI', 'PATH', 'UPST', 'GPRO', 'AR', 'APP', 'DLO',
    ],
  },

  // ===== US LARGE CAP =====
  'US Large Cap': {
    title: 'US Large Cap',
    description: '美国大盘蓝筹',
    tickers: [
      'JPM', 'V', 'UNH', 'MA', 'JNJ', 'PG', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY', 'PEP', 'KO',
      'COST', 'ADBE', 'MCD', 'TMO', 'CSCO', 'ACN', 'ABT', 'DHR', 'WMT', 'NEE', 'NKE',
      'ORCL', 'UPS', 'MS', 'LOW', 'BA', 'IBM', 'CAT', 'HON', 'SPGI', 'INTU', 'AXP',
      'GS', 'BLK', 'DE', 'MDT', 'AMGN', 'GILD', 'ISRG', 'SCHW', 'BKNG', 'VRTX', 'REGN',
      'ZTS', 'PLD', 'MMC', 'TJX', 'EL', 'CL', 'MDLZ', 'KMB', 'GIS', 'K', 'HSY',
    ],
  },

  // ===== US FINANCIALS =====
  'US Financials': {
    title: 'US Financials',
    description: '美国金融股',
    tickers: [
      'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'SCHW', 'USB',
      'PNC', 'TFC', 'COF', 'DFS', 'MET', 'PRU', 'AFL', 'TRV', 'ALL', 'TRV',
      'AIG', 'PRU', 'HIG', 'BRO', 'WRB', 'RF', 'HBAN', 'KEY', 'STT', 'SPGI',
      'ICE', 'CME', 'MCO', 'NDAQ', 'FIS', 'FISV', 'PAYX', 'ADP', 'CINF', 'L',
    ],
  },

  // ===== US HEALTHCARE =====
  'US Healthcare': {
    title: 'US Healthcare',
    description: '美国医疗健康',
    tickers: [
      'UNH', 'JNJ', 'MRK', 'ABBV', 'LLY', 'PFE', 'ABT', 'DHR', 'TMO', 'AMGN',
      'GILD', 'ISRG', 'VRTX', 'REGN', 'ZTS', 'BMY', 'MDT', 'SYK', 'BSX', 'EW',
      'IQV', 'IDXX', 'LH', 'DGX', 'ABC', 'CAH', 'MCK', 'ESRX', 'CVS', 'CI',
      'HUM', 'CNC', 'MOH', 'ELV', 'HCA', 'UHS', 'THC', 'DVH', 'XHE', 'VTR',
    ],
  },

  // ===== US ENERGY =====
  'US Energy': {
    title: 'US Energy',
    description: '美国能源股',
    tickers: [
      'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'HAL', 'OXY',
      'DVN', 'FANG', 'BKR', 'KMI', 'WMB', 'OKE', 'TRGP', 'WMB', 'ET', 'ENB',
      'PBA', 'LNG', 'D', 'ES', 'AEP', 'EXC', 'NEE', 'SRE', 'PCG', 'ED',
    ],
  },

  // ===== US CONSUMER DISCRETIONARY =====
  'US Consumer': {
    title: 'US Consumer',
    description: '美国消费股',
    tickers: [
      'AMZN', 'TSLA', 'HD', 'NKE', 'MCD', 'SBUX', 'BKNG', 'GM', 'F', 'ROST',
      'DLTR', 'DG', 'BBY', 'ORLY', 'AZO', 'YUM', 'CMG', 'RIVN', 'LCID', 'GRMN',
      'HLT', 'MAR', 'VAC', 'RCL', 'CCL', 'NCLH', 'WYNN', 'MGM', 'CZR', 'WYNN',
      'LVS', 'MHK', 'BWH', 'WHR', 'DRI', 'TXRH', 'WING', 'CULP', 'LOCM', 'SCSC',
    ],
  },

  // ===== US INDUSTRIALS =====
  'US Industrials': {
    title: 'US Industrials',
    description: '美国工业股',
    tickers: [
      'CAT', 'DE', 'BA', 'HON', 'UPS', 'RTX', 'LMT', 'NOC', 'GD', 'APH',
      'EMR', 'ROK', 'ITW', 'ETN', 'CMI', 'AME', 'IR', 'PNR', 'XYL', 'CARR',
      'OTIS', 'GE', 'MMM', 'FDX', 'CSX', 'NSC', 'UNP', 'KSU', 'DAL', 'UAL',
      'AAL', 'LUV', 'ALK', 'CHRW', 'CPRT', 'FDX', 'EXPD', 'JBHT',
    ],
  },

  // ===== US REAL ESTATE =====
  'US Real Estate': {
    title: 'US Real Estate',
    description: '美国房地产',
    tickers: [
      'PLD', 'AMT', 'CCI', 'EQIX', 'SPG', 'O', 'PSA', 'DLR', 'AVB', 'EQR',
      'WELL', 'VTR', 'SBAC', 'ARE', 'MAA', 'UDR', 'ESS', 'REG', 'CPT', 'KIM',
      'HST', 'RHP', 'SUI', 'ELS', 'AIV', 'CRE', 'SRC', 'LXFR', 'SBRA', 'RESI',
    ],
  },

  // ===== US UTILITIES =====
  'US Utilities': {
    title: 'US Utilities',
    description: '美国公用事业',
    tickers: [
      'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PCG', 'ED',
      'PEG', 'ETR', 'AEE', 'ES', 'EIX', 'AWK', 'WEC', 'DTE', 'DUK', 'GWI',
      'NI', 'EVRG', 'AEP', 'CNP', 'BKH', 'ATO', 'CMS', 'D', 'AWK',
    ],
  },

  // ===== US MATERIALS =====
  'US Materials': {
    title: 'US Materials',
    description: '美国材料股',
    tickers: [
      'APD', 'SHW', 'FCX', 'NEM', 'NUE', 'STLD', 'RS', 'PPG', 'ALB', 'CE',
      'EMN', 'MOS', 'FMC', 'CTVA', 'DOW', 'LYB', 'IP', 'PKG',
      'AVY', 'BALL', 'CCK', 'SLGN', 'SW', 'MLM', 'VMC', 'DD', 'IFF',
    ],
  },

  // ===== US COMMUNICATION =====
  'US Comm Services': {
    title: 'US Comm Services',
    description: '美国通信服务',
    tickers: [
      'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS', 'CHTR', 'WBD',
      'PARA', 'FOX', 'NWSA', 'CBS', 'WBD', 'IPG', 'OMC', 'MTCH', 'DBX',
      'YELP', 'GRPN', 'CARR', 'ATVI', 'EA', 'TTWO', 'NTDOY', 'SOHU',
    ],
  },

  // ===== US ETFs =====
  'US ETFs': {
    title: 'US ETFs',
    description: '美国ETF',
    fastRefresh: true,
    tickers: [
      'SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'TLT', 'GLD', 'SLV', 'UNG', 'XLE', 'XLF',
      'XLV', 'XLY', 'XLK', 'XLC', 'XLRE', 'ARKK', 'VO', 'VB', 'VTI', 'VEA', 'VWO',
      'BND', 'AGG', 'SCHD', 'VYM', 'HDV', 'DIA', 'IVV', 'VOO', 'VGT', 'VCR',
      'VDC', 'VFH', 'VHT', 'VIS', 'VAW', 'VNQ', 'VOX', 'VPU', 'VA', 'VLUE',
    ],
  },

  // ===== CRYPTO =====
  'Crypto': {
    title: 'Crypto',
    description: '加密货币',
    tickers: [
      'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'AVAX-USD',
      'DOGE-USD', 'DOT-USD', 'LINK-USD', 'MATIC-USD', 'UNI-USD', 'ATOM-USD', 'LTC-USD',
      'BCH-USD', 'NEAR-USD', 'APT-USD', 'ARB-USD', 'OP-USD', 'FIL-USD', 'AAVE-USD',
      'MKR-USD', 'SNX-USD', 'CRV-USD', 'LDO-USD', 'SAND-USD', 'MANA-USD', 'AXS-USD',
    ],
  },

  // ===== COMMODITIES =====
  'Commodities': {
    title: 'Commodities',
    description: '大宗商品期货',
    tickers: [
      'GC=F', 'SI=F', 'CL=F', 'NG=F', 'HG=F', 'ZC=F', 'ZS=F', 'ZW=F', 'ZL=F', 'ZO=F',
      'KC=F', 'CT=F', 'SB=F', 'RC=F', 'PL=F', 'PA=F', 'CO=F', 'LH=F', 'LE=F',
    ],
  },

  // ===== RATES & BONDS =====
  'Rates & Bonds': {
    title: 'Rates & Bonds',
    description: '利率与国债',
    fastRefresh: true,
    tickers: [
      '^TNX', '^TYX', '^FVX', '^IRX', 'TLT', 'IEF', 'SHY', 'DXY',
      'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X',
    ],
  },

  // ===== CHINA/HK/Taiwan =====
  'China/HK/Taiwan': {
    title: 'China/HK/Taiwan',
    description: '中国香港台湾',
    tickers: [
      // HK Tech
      '9988.HK', '0700.HK', '9618.HK', '3690.HK', '1810.HK', '7200.HK', '9868.HK',
      '2319.HK', '1044.HK', '2020.HK', '6690.HK', '2382.HK', '2611.HK', '2628.HK',
      // China A-Share
      '600519.SS', '600036.SS', '601318.SS', '600276.SS', '300750.SZ', '002594.SZ', '000858.SZ',
      '600009.SS', '600030.SS', '601012.SS', '601166.SS', '600900.SS', '600016.SS', '600028.SS',
      // Taiwan
      '2330.TW', '2454.TW', '2382.TW', '2303.TW', '3711.TW', '2308.TW', '6409.TW',
      '2395.TW', '2492.TW', '2451.TW', '2471.TW', '6669.TW', '2313.TW', '4938.TW',
    ],
  },

  // ===== JAPAN =====
  'Japan': {
    title: 'Japan',
    description: '日本股市',
    tickers: [
      '9984.T', '7203.T', '6752.T', '9432.T', '9434.T', '8306.T', '8316.T', '8604.T',
      '8021.T', '8035.T', '8058.T', '6098.T', '4452.T', '4901.T', '7733.T', '6902.T',
      '6501.T', '6503.T', '6841.T', '6971.T', '7951.T', '9675.T', '6971.T', '6367.T',
      '4004.T', '5214.T', '5332.T', '5334.T', '6103.T', '6271.T', '6326.T', '7751.T',
    ],
  },

  // ===== EUROPE =====
  'Europe': {
    title: 'Europe',
    description: '欧洲股市',
    tickers: [
      // Netherlands
      'ASML.AS', 'ADYEN.AS', 'URW.AS', 'PHIA.AS', 'HEIA.AS',
      // Germany
      'SAP.DE', 'SIE.DE', 'ALV.DE', 'DPW.DE', 'DHL.DE', 'BMW.DE', 'VOW3.DE', 'DTE.DE',
      'ENR.DE', 'MRK.DE', 'BAYN.DE', 'LIN.DE', 'CON.DE', 'FRE.DE', 'MTX.DE', 'QIA.DE',
      // UK
      'HSBC', 'SHELL.L', 'BP.L', 'GSK.L', 'AZN.L', 'REL.L', 'BHP.L', 'RIO.L', 'VOD.L',
      'ULVR.L', 'HSBA.L', 'GSK.L', 'DGE.L', 'NG.L', 'BP.L', 'SHEL.L', 'BATS.L', 'IMB.L',
      // France
      'OR.PA', 'TTE.PA', 'AIR.PA', 'SAN.PA', 'LVMH.PA', 'RMS.PA', 'MC.PA', 'BNP.PA',
      'GLE.PA', 'ORA.PA', 'ENGI.PA', 'VIV.PA', 'CAP.PA', 'AC.PA', 'EL.PA',
      // Switzerland
      'NESN.SW', 'NOVN.SW', 'ROG.SW', 'UBSG.SW', 'ABBN.SW', 'SLHN.SW', 'ZURN.SW',
      // Scandinavia
      'VOLV-B.ST', 'NVO', 'VWS.CO', 'CARL-B.CO', 'COLO-B.CO', 'SAMPO.HE', 'STERV.HE',
      // Italy/Spain/Belgium
      'ISP.MI', 'ENEL.MI', 'INI.MI', 'UCG.MI', 'TRI.MI', 'BBVA.MC', 'SAN.MC', 'TEF.MC',
    ],
  },

  // ===== KOREA =====
  'Korea': {
    title: 'Korea',
    description: '韩国股市',
    tickers: [
      '0050.KS', '0051.KS', '068270.KS', '000660.KS', '051910.KS', '207940.KS',
      '005380.KS', '012330.KS', '035420.KS', '035720.KS', '096770.KS', '066570.KS',
      '000270.KS', '096530.KS', '003670.KS', '018260.KS', '034730.KS', '055550.KS',
    ],
  },

  // ===== INDIA =====
  'India': {
    title: 'India',
    description: '印度股市',
    tickers: [
      'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDB.NS', 'BHARTIARTL.NS', 'ITC.NS',
      'KMB.NS', 'LT.NS', 'HINDUNILVR.NS', 'MARUTI.NS', 'TATAMOTORS.NS', 'WIPRO.NS',
      'AXISBANK.NS', 'KOTAKBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'BAJFINANCE.NS',
      'HDFCBANK.NS', 'SUNPHARMA.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS', 'POWERGRID.NS',
    ],
  },

  // ===== CANADA =====
  'Canada': {
    title: 'Canada',
    description: '加拿大股市',
    tickers: [
      'RY', 'TD', 'BMO', 'CNQ', 'SU', 'ENB', 'TRP', 'EOG', 'MFC', 'SLF',
      'BNS', 'CM', 'NA', 'LB', 'GWO', 'POW', 'IFC', 'TA', 'X', 'AC',
      'BAM', 'CX', 'NWC', 'ACCDY', 'LSPD', 'REAL', 'MTL', 'TSLA', 'FCR', 'RNW',
    ],
  },

  // ===== AUSTRALIA =====
  'Australia': {
    title: 'Australia',
    description: '澳大利亚股市',
    tickers: [
      'BHP.AX', 'RIO.AX', 'CBA.AX', 'WES.AX', 'TLS.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX',
      'CSL.AX', 'FMG.AX', 'WOW.AX', 'COL.AX', 'JBH.AX', 'ALL.AX', 'SUN.AX', 'AMP.AX',
      'BEN.AX', 'PTM.AX', 'QBE.AX', 'AIA.AX', 'ARG.AX', 'IPL.AX', 'STO.AX', 'OSH.AX',
    ],
  },

  // ===== SOUTHEAST ASIA =====
  'SE Asia': {
    title: 'SE Asia',
    description: '东南亚股市',
    tickers: [
      // Singapore
      'D05.SI', 'U11.SI', 'C6L.SI', 'Z74.SI', 'S63.SI', 'OCBC.SI', 'DBS.SI', 'STI.SI',
      // Thailand
      'PTT.BK', 'AOT.BK', 'CPALL.BK', 'KBANK.BK', 'SCB.BK', 'BDMS.BK', 'TRUE.BK', 'EGCO.BK',
      // Indonesia
      'BBCA.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'HMSP.JK', 'PGAS.JK', 'PTBA.JK', 'ANTM.JK',
      // Malaysia
      'MAYBANK.MY', 'PETRONAS.MY', 'CIMB.MY', 'TENAGA.MY', 'MAXIS.MY', 'DIGI.MY',
      // Philippines
      'SMPC', 'PLDT', 'BDO', 'JFC', 'ALCO', 'RRHI',
    ],
  },

  // ===== LATIN AMERICA =====
  'Latin America': {
    title: 'Latin America',
    description: '拉丁美洲股市',
    tickers: [
      // Brazil
      'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'BBD4.SA', 'ABEV3.SA', 'JBSS3.SA', 'RAIA3.SA',
      'RENT3.SA', 'HAPV3.SA', 'LWSA3.SA', 'MGLU3.SA', 'PETR3.SA', 'VVAR3.SA',
      // Mexico
      'AMXL.MX', 'TV', 'FEMSAU.MX', 'GMEXICOB.MX', 'KOFUBL.MX', 'CEMEXCPO.MX', 'GAPB.MX',
      // Chile
      'SQM', 'CENCOSUD', 'COPEC', 'SACO', 'LAFARGEHOLCIM', 'CCU', 'ENTEL',
    ],
  },

  // ===== EMERGING MARKETS =====
  'Emerging Markets': {
    title: 'Emerg Markets',
    description: '新兴市场ETF',
    tickers: [
      'EWZ', 'EWY', 'EWT', 'INDA', 'EWC', 'EWW', 'RSX', 'THD', 'IDX', 'MYE',
      'PHP', 'VNQ', 'TUR', 'EGY', 'KENYA', 'EPOL', 'EEMA', 'IEMG', 'SPEM', 'SCHE',
    ],
  },
};

type Category = keyof typeof TICKER_CATEGORIES;

type MarketDataRecord = {
  ticker: string;
  name: string;
  price: number;
  change?: number;
  changePercent?: number;
  volume: number;
  timestamp: string;
};

export default function MarketPage() {
  const { isLoggedIn, username } = useAuth();
  const [activeCategory, setActiveCategory] = useState<Category>('Global Indices');
  const [watchlist, setWatchlist] = useState<string[]>([
    '^GSPC', '^DJI', '^IXIC', 'BTC-USD', 'ETH-USD', 'GC=F', 'CL=F'
  ]);
  const [inputTicker, setInputTicker] = useState('');
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [showTrading, setShowTrading] = useState(false);
  const [showTreemap, setShowTreemap] = useState(false);

  // Batch market data state
  const [categoryData, setCategoryData] = useState<Record<string, MarketDataRecord>>({});
  const [watchlistData, setWatchlistData] = useState<Record<string, MarketDataRecord>>({});
  const [categoryError, setCategoryError] = useState<string | null>(null);
  const [watchlistError, setWatchlistError] = useState<string | null>(null);

  // Fetch batch data when category changes
  const fetchCategoryData = useCallback(async (category: Category) => {
    const tickers = TICKER_CATEGORIES[category]?.tickers || [];
    if (tickers.length === 0) return;
    setCategoryError(null);

    try {
      const result = await marketApi.getBatch(tickers);
      const dataMap: Record<string, MarketDataRecord> = {};
      result.data.forEach((item: MarketDataRecord) => {
        dataMap[item.ticker] = item;
      });
      setCategoryData(dataMap);
    } catch (err) {
      console.error('Failed to fetch category data:', err);
      setCategoryError(err instanceof Error ? err.message : 'Failed to load market data');
    }
  }, []);

  // Fetch watchlist data
  const fetchWatchlistData = useCallback(async (tickers: string[]) => {
    if (tickers.length === 0) return;
    setWatchlistError(null);

    try {
      const result = await marketApi.getBatch(tickers);
      const dataMap: Record<string, MarketDataRecord> = {};
      result.data.forEach((item: MarketDataRecord) => {
        dataMap[item.ticker] = item;
      });
      setWatchlistData(dataMap);
    } catch (err) {
      console.error('Failed to fetch watchlist data:', err);
      setWatchlistError(err instanceof Error ? err.message : 'Failed to load watchlist');
    }
  }, []);

  useEffect(() => {
    fetchCategoryData(activeCategory);
    fetchWatchlistData(watchlist);
  }, [activeCategory, watchlist, fetchCategoryData, fetchWatchlistData]);

  // Periodic refresh for fastRefresh categories
  useEffect(() => {
    const category = TICKER_CATEGORIES[activeCategory];
    if (!category?.fastRefresh) return;

    const interval = setInterval(() => {
      fetchCategoryData(activeCategory);
    }, 15000);

    return () => clearInterval(interval);
  }, [activeCategory, fetchCategoryData]);

  // Periodic refresh for watchlist (always 15s since it's small)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchWatchlistData(watchlist);
    }, 15000);

    return () => clearInterval(interval);
  }, [watchlist, fetchWatchlistData]);

  const handleAddTicker = (e: React.FormEvent) => {
    e.preventDefault();
    const ticker = inputTicker.toUpperCase().trim();
    if (ticker && !watchlist.includes(ticker)) {
      setWatchlist([...watchlist, ticker]);
      setInputTicker('');
    }
  };

  const handleRemoveTicker = (ticker: string) => {
    setWatchlist(watchlist.filter(t => t !== ticker));
    if (selectedTicker === ticker) setSelectedTicker(null);
  };

  const handleAddToWatchlist = (ticker: string) => {
    if (!watchlist.includes(ticker)) {
      setWatchlist([...watchlist, ticker]);
    }
  };

  // Count total tickers
  const totalTickers = Object.values(TICKER_CATEGORIES).reduce((sum, cat) => sum + cat.tickers.length, 0);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Data & Trading</h1>
          <p className="text-muted-foreground mt-2">
            {totalTickers}+ global symbols · Indices/ETFs: 15s · Stocks: 5min
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowTreemap(!showTreemap)}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              showTreemap
                ? 'bg-blue-100 text-blue-700 border border-blue-300'
                : 'bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200'
            }`}
          >
            {showTreemap ? 'Hide' : 'Show'} S&P 500 Treemap
          </button>
          <Link
            href="/"
            className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Back to Forum
          </Link>
        </div>
      </header>

      {/* S&P 500 Treemap */}
      {showTreemap && (
        <section className="mb-8">
          <StockTreemap onSelect={(ticker) => {
            setSelectedTicker(ticker);
            if (!watchlist.includes(ticker)) {
              setWatchlist([...watchlist, ticker]);
            }
          }} />
        </section>
      )}

      {/* My Watchlist */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">My Watchlist</h2>
          <form onSubmit={handleAddTicker} className="flex gap-2">
            <input
              type="text"
              value={inputTicker}
              onChange={(e) => setInputTicker(e.target.value.toUpperCase())}
              placeholder="Add ticker..."
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-32"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90"
            >
              Add
            </button>
          </form>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {watchlist.map((ticker) => (
            <div key={ticker} className="relative group">
              <MarketDataCard
                ticker={ticker}
                data={watchlistData[ticker]}
                onSelect={(t) => setSelectedTicker(t)}
                compact
              />
              <button
                onClick={() => handleRemoveTicker(ticker)}
                className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Browse by Category */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Browse Markets</h2>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(TICKER_CATEGORIES).map(([key, category]) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key as Category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                activeCategory === key
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.title} ({category.tickers.length})
            </button>
          ))}
        </div>

        {/* Category Description */}
        <p className="text-sm text-gray-500 mb-4">
          {TICKER_CATEGORIES[activeCategory].description} · {TICKER_CATEGORIES[activeCategory].tickers.length} symbols
        </p>

        {/* Error Banner */}
        {categoryError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
            <span className="text-red-700 text-sm">{categoryError}</span>
            <button
              onClick={() => fetchCategoryData(activeCategory)}
              className="text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Retry
            </button>
          </div>
        )}

        {/* Ticker Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {TICKER_CATEGORIES[activeCategory].tickers.map((ticker) => (
            <div key={ticker} className="relative group">
              <MarketDataCard
                ticker={ticker}
                data={categoryData[ticker]}
                onSelect={(t) => setSelectedTicker(t)}
                compact
              />
              {!watchlist.includes(ticker) && (
                <button
                  onClick={() => handleAddToWatchlist(ticker)}
                  className="absolute top-1 right-1 w-5 h-5 bg-green-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                  +
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Selected Ticker Detail */}
      {selectedTicker && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4">Detail: {selectedTicker}</h2>
          <div className="max-w-md">
            <MarketDataCard ticker={selectedTicker} data={categoryData[selectedTicker]} />
          </div>
        </section>
      )}

      {/* Trading Dashboard */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Trading</h2>
          {isLoggedIn && username && (
            <button
              onClick={() => setShowTrading(!showTrading)}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90"
            >
              {showTrading ? 'Hide Trading' : 'Show Trading'}
            </button>
          )}
        </div>

        {!isLoggedIn ? (
          <div className="bg-gray-100 rounded-lg p-6 text-center">
            <p className="text-gray-600 mb-4">Please login to access trading features</p>
            <Link
              href="/login"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90"
            >
              Login
            </Link>
          </div>
        ) : showTrading ? (
          <TradingDashboard agentId={username!} />
        ) : (
          <div className="bg-gray-100 rounded-lg p-6 text-center">
            <p className="text-gray-600">Click &quot;Show Trading&quot; to view your trading dashboard</p>
          </div>
        )}
      </section>
    </div>
  );
}
