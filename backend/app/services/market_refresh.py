"""Market data background refresh service - keeps DB warm without user-facing delays"""
import logging
import time
from datetime import datetime
from typing import List

from app.services.market import market_service

logger = logging.getLogger(__name__)

# All tickers that need to be refreshed (synced with frontend TICKER_CATEGORIES)
# Total: ~843 tickers across 24 categories
ALL_TICKERS = [
    # ===== GLOBAL INDICES =====
    '^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX', '^N225', '^AXJO', '^BSESN',
    '000001.SS', '399001.SZ', '^HSI', '^GDAXI', '^FCHI', '^FTSE', '^STOXX50E',

    # ===== US TECHNOLOGY =====
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AMD', 'INTC', 'QCOM',
    'TXN', 'ADI', 'AVGO', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS', 'PANW', 'CRWD',
    'NET', 'ZS', 'OKTA', 'DDOG', 'MDB', 'COIN', 'RBLX', 'UBER', 'LYFT', 'SNOW',
    'VEEV', 'TWLO', 'PATH', 'UPST', 'GPRO', 'AR', 'APP', 'DLO',

    # ===== US LARGE CAP (Expanded S&P 500) =====
    'JPM', 'V', 'UNH', 'MA', 'JNJ', 'PG', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY', 'PEP', 'KO',
    'COST', 'ADBE', 'MCD', 'TMO', 'CSCO', 'ACN', 'ABT', 'DHR', 'WMT', 'NEE', 'NKE',
    'ORCL', 'UPS', 'MS', 'LOW', 'BA', 'IBM', 'CAT', 'HON', 'SPGI', 'INTU', 'AXP',
    'GS', 'BLK', 'DE', 'MDT', 'AMGN', 'GILD', 'ISRG', 'SCHW', 'BKNG', 'VRTX', 'REGN',
    'ZTS', 'PLD', 'TJX', 'EL', 'CL', 'MDLZ', 'KMB', 'GIS', 'HSY',
    # Additional S&P 500 stocks
    'AON', 'AMP', 'ARE', 'AVB', 'AXON', 'BALL', 'BRK-B', 'CARR', 'CDW', 'CEG',
    'CF', 'CHD', 'CPRT', 'CTAS', 'CTVA', 'CZR', 'D', 'DAL', 'DECK', 'DHI',
    'DG', 'DLTR', 'DOV', 'DOW', 'DXCM', 'EA', 'EBAY', 'EFX', 'EG', 'EIX',
    'EMR', 'ENPH', 'EPAM', 'ES', 'ESS', 'EQR', 'F', 'FANG', 'FAST', 'FCX',
    'FDS', 'FDX', 'FE', 'FITB', 'FMC', 'FTNT', 'FTV', 'GDDY', 'GEN', 'GILD',
    'GL', 'GLW', 'GM', 'GNRC', 'GT', 'HAL', 'HAS', 'HBAN', 'HCA', 'HES',
    'HII', 'HPE', 'HPQ', 'HUBB', 'HUM', 'HWM', 'ICL', 'IDXX', 'IEX',
    'IFF', 'INVH', 'IP', 'IPG', 'IR', 'IRM', 'JBHT', 'JCI', 'JKHY', 'JNPR',
    'K', 'KBH', 'KHC', 'KIM', 'KLAC', 'KMB', 'KMI', 'KMX', 'KO', 'KR',
    'L', 'LDOS', 'LH', 'LHX', 'LKQ', 'LLY', 'LMT', 'LNC', 'LNT', 'LOW',
    'LRCX', 'LUV', 'LYB', 'LYV', 'MAA', 'MAR', 'MCHP', 'MCK', 'MCO', 'MDLZ',
    'MDR', 'META', 'MKC', 'MKTX', 'MLM', 'MMC', 'MNST', 'MO', 'MPWR', 'MRK',
    'MRNA', 'MRVL', 'MSCI', 'MSFT', 'MTCH', 'MTD', 'MU', 'NCLH', 'NDAQ',
    'NDSN', 'NEE', 'NEM', 'NFLX', 'NHI', 'NI', 'NKE', 'NOC', 'NOV', 'NOC',
    'NUE', 'NVDA', 'NVR', 'ODFL', 'OFLX', 'OGN', 'OKE', 'OMC', 'ON',
    'ORCL', 'ORLY', 'OXY', 'PANW', 'PARA', 'PAYX', 'PCAR', 'PCG', 'PEG',
    'PENN', 'PH', 'PKG', 'PLD', 'PM', 'PNC', 'PNR', 'PNW', 'PODD', 'POOL',
    'PPG', 'PPL', 'PRU', 'PTC', 'PVH', 'PWR', 'PXD', 'QCOM', 'RCL', 'REG',
    'RF', 'RHI', 'RJF', 'RL', 'RMD', 'ROK', 'ROL', 'ROP', 'ROST', 'RSG',
    'RTX', 'RVTY', 'SBAC', 'SBUX', 'SCHW', 'SEDG', 'SHW', 'SIVB', 'SJM',
    'SLB', 'SLM', 'SMAR', 'SNPS', 'SNX', 'SO', 'SPGI', 'SPG', 'STE', 'STT',
    'STZ', 'SWK', 'SWKS', 'SYY', 'T', 'TAP', 'TDG', 'TDY', 'TECH', 'TFC',
    'TFX', 'TGT', 'TJX', 'TMO', 'TMUS', 'TPR', 'TROW', 'TRV', 'TSCO', 'TSLA',
    'TSN', 'TT', 'TTWO', 'TXN', 'TXT', 'TYL', 'UAL', 'UDR', 'UHS', 'ULTA',
    'UNH', 'UNP', 'UPS', 'URI', 'USB', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VTR',
    'VTRS', 'VZ', 'WAB', 'WAT', 'WBA', 'WBD', 'WCG', 'WEC', 'WELL', 'WFC',
    'WHR', 'WMB', 'WMT', 'WRB', 'WST', 'WTW', 'WY', 'WYNN', 'XEL', 'XOM',
    'XYL', 'YUM', 'ZBH', 'ZION', 'ZM', 'ZS',

    # ===== US FINANCIALS =====
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'SCHW', 'USB',
    'PNC', 'TFC', 'COF', 'DFS', 'MET', 'PRU', 'AFL', 'TRV', 'ALL', 'TRV',
    'AIG', 'PRU', 'HIG', 'BRO', 'WRB', 'RF', 'HBAN', 'KEY', 'STT', 'SPGI',
    'ICE', 'CME', 'MCO', 'NDAQ', 'FIS', 'FISV', 'PAYX', 'ADP', 'CINF', 'L',

    # ===== US HEALTHCARE =====
    'UNH', 'JNJ', 'MRK', 'ABBV', 'LLY', 'PFE', 'ABT', 'DHR', 'TMO', 'AMGN',
    'GILD', 'ISRG', 'VRTX', 'REGN', 'ZTS', 'BMY', 'MDT', 'SYK', 'BSX', 'EW',
    'IQV', 'IDXX', 'LH', 'DGX', 'ABC', 'CAH', 'MCK', 'ESRX', 'CVS', 'CI',
    'HUM', 'CNC', 'MOH', 'ELV', 'HCA', 'UHS', 'THC', 'DVH', 'XHE', 'VTR',

    # ===== US ENERGY =====
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'HAL', 'OXY',
    'DVN', 'FANG', 'BKR', 'KMI', 'WMB', 'OKE', 'TRGP', 'WMB', 'ET', 'ENB',
    'PBA', 'LNG', 'D', 'ES', 'AEP', 'EXC', 'NEE', 'SRE', 'PCG', 'ED',

    # ===== US CONSUMER =====
    'AMZN', 'TSLA', 'HD', 'NKE', 'MCD', 'SBUX', 'BKNG', 'GM', 'F', 'ROST',
    'DLTR', 'DG', 'BBY', 'ORLY', 'AZO', 'YUM', 'CMG', 'RIVN', 'LCID', 'GRMN',
    'HLT', 'MAR', 'VAC', 'RCL', 'CCL', 'NCLH', 'WYNN', 'MGM', 'CZR', 'WYNN',
    'LVS', 'MHK', 'BWH', 'WHR', 'DRI', 'TXRH', 'WING', 'CULP', 'LOCM', 'SCSC',

    # ===== US INDUSTRIALS =====
    'CAT', 'DE', 'BA', 'HON', 'UPS', 'RTX', 'LMT', 'NOC', 'GD', 'APH',
    'EMR', 'ROK', 'ITW', 'ETN', 'CMI', 'AME', 'IR', 'PNR', 'XYL', 'CARR',
    'OTIS', 'GE', 'MMM', 'FDX', 'CSX', 'NSC', 'UNP', 'KSU', 'DAL', 'UAL',
    'AAL', 'LUV', 'ALK', 'CHRW', 'CPRT', 'FDX', 'EXPD', 'JBHT',

    # ===== US REAL ESTATE =====
    'PLD', 'AMT', 'CCI', 'EQIX', 'SPG', 'O', 'PSA', 'DLR', 'AVB', 'EQR',
    'WELL', 'VTR', 'SBAC', 'ARE', 'MAA', 'UDR', 'ESS', 'REG', 'CPT', 'KIM',
    'HST', 'RHP', 'SUI', 'ELS', 'AIV', 'CRE', 'SRC', 'LXFR', 'SBRA', 'RESI',

    # ===== US UTILITIES =====
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PCG', 'ED',
    'PEG', 'ETR', 'AEE', 'ES', 'EIX', 'AWK', 'WEC', 'DTE', 'DUK', 'GWI',
    'NI', 'EVRG', 'AEP', 'CNP', 'BKH', 'ATO', 'CMS', 'D', 'AWK',

    # ===== US MATERIALS =====
    'APD', 'SHW', 'FCX', 'NEM', 'NUE', 'STLD', 'RS', 'PPG', 'ALB', 'CE',
    'EMN', 'MOS', 'FMC', 'CTVA', 'DOW', 'LYB', 'IP', 'PKG',
    'AVY', 'BALL', 'CCK', 'SLGN', 'SW', 'MLM', 'VMC', 'DD', 'IFF',

    # ===== US COMMUNICATION SERVICES =====
    'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS', 'CHTR', 'WBD',
    'PARA', 'FOX', 'NWSA', 'CBS', 'WBD', 'IPG', 'OMC', 'MTCH', 'DBX',
    'YELP', 'GRPN', 'CARR', 'ATVI', 'EA', 'TTWO', 'NTDOY', 'SOHU',

    # ===== US ETFs (Expanded) =====
    'SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'TLT', 'GLD', 'SLV', 'UNG', 'XLE', 'XLF',
    'XLV', 'XLY', 'XLK', 'XLC', 'XLRE', 'ARKK', 'VO', 'VB', 'VTI', 'VEA', 'VWO',
    'BND', 'AGG', 'SCHD', 'VYM', 'HDV', 'DIA', 'IVV', 'VOO', 'VGT', 'VCR',
    'VDC', 'VFH', 'VHT', 'VIS', 'VAW', 'VNQ', 'VOX', 'VPU', 'VA', 'VLUE',
    # Additional ETFs for broader coverage
    'QQQM', 'SPYG', 'SPYD', 'SPYV', 'IVW', 'IVE', 'IJK', 'IJJ', 'IJR', 'IJS',
    'SPLV', 'USMV', 'SPHD', 'FDIS', 'FCOM', 'FGRO', 'FTCS', 'FVAL', 'FIDU',
    'GDX', 'GDXJ', 'SMH', 'SOXL', 'TQQQ', 'SQQQ', 'SPXL', 'SPXS', 'UPRO', 'SDP',
    'TMF', 'TYD', 'TYO', 'UST', 'PST', 'DTN', 'DTD', 'DEW', 'DFJ', 'DGAZ',
    'BOIL', 'UNG', 'UCO', 'SCO', 'KOLD', 'CPER', 'UNG', 'USO', 'BNO', 'CORN',
    'WEAT', 'SOYB', 'NIB', 'JJT', 'CO', 'LIT', 'Uranium', 'URA', 'PICK',
    'VIXY', 'VIXM', 'SVIX', 'UVXY', 'VXX', 'VXZ', 'XIV', 'EXIV', 'EEMV',
    'IEMV', 'ACWV', 'ACWI', 'SPGM', 'SPEU', 'SPDW', 'SPEM', 'SPEZ', 'SPCM',
    # More sector ETFs
    'XLB', 'XHB', 'XRT', 'XAR', 'XBI', 'XPH', 'XHS', 'XLV', 'XHW', 'XWEB',
    # Additional diverse assets
    'FTEC', 'FITE', 'FLM', 'FTC', 'FYX', 'GAL', 'GUR', 'GVIP', 'HACK', 'HAKK',
    'IAU', 'IGV', 'IGSB', 'IJR', 'IJH', 'IJJ', 'IJK', 'IYM', 'IYW', 'IYZ',

    # ===== CRYPTO =====
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'AVAX-USD',
    'DOGE-USD', 'DOT-USD', 'LINK-USD', 'MATIC-USD', 'UNI-USD', 'ATOM-USD', 'LTC-USD',
    'BCH-USD', 'NEAR-USD', 'APT-USD', 'ARB-USD', 'OP-USD', 'FIL-USD', 'AAVE-USD',
    'MKR-USD', 'SNX-USD', 'CRV-USD', 'LDO-USD', 'SAND-USD', 'MANA-USD', 'AXS-USD',

    # ===== COMMODITIES =====
    'GC=F', 'SI=F', 'CL=F', 'NG=F', 'HG=F', 'ZC=F', 'ZS=F', 'ZW=F', 'ZL=F', 'ZO=F',
    'KC=F', 'CT=F', 'SB=F', 'RC=F', 'PL=F', 'PA=F', 'CO=F', 'LH=F', 'LE=F',

    # ===== RATES & BONDS =====
    '^TNX', '^TYX', '^FVX', '^IRX', 'TLT', 'IEF', 'SHY', 'DXY',
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X',

    # ===== CHINA/HK/TAIWAN =====
    '9988.HK', '0700.HK', '9618.HK', '3690.HK', '1810.HK', '7200.HK', '9868.HK',
    '2319.HK', '1044.HK', '2020.HK', '6690.HK', '2382.HK', '2611.HK', '2628.HK',
    '600519.SS', '600036.SS', '601318.SS', '600276.SS', '300750.SZ', '002594.SZ', '000858.SZ',
    '600009.SS', '600030.SS', '601012.SS', '601166.SS', '600900.SS', '600016.SS', '600028.SS',
    '2330.TW', '2454.TW', '2382.TW', '2303.TW', '3711.TW', '2308.TW', '6409.TW',
    '2395.TW', '2492.TW', '2451.TW', '2471.TW', '6669.TW', '2313.TW', '4938.TW',

    # ===== JAPAN =====
    '9984.T', '7203.T', '6752.T', '9432.T', '9434.T', '8306.T', '8316.T', '8604.T',
    '8021.T', '8035.T', '8058.T', '6098.T', '4452.T', '4901.T', '7733.T', '6902.T',
    '6501.T', '6503.T', '6841.T', '6971.T', '7951.T', '9675.T', '6971.T', '6367.T',
    '4004.T', '5214.T', '5332.T', '5334.T', '6103.T', '6271.T', '6326.T', '7751.T',

    # ===== EUROPE =====
    'ASML.AS', 'ADYEN.AS', 'URW.AS', 'PHIA.AS', 'HEIA.AS',
    'SAP.DE', 'SIE.DE', 'ALV.DE', 'DPW.DE', 'DHL.DE', 'BMW.DE', 'VOW3.DE', 'DTE.DE',
    'ENR.DE', 'MRK.DE', 'BAYN.DE', 'LIN.DE', 'CON.DE', 'FRE.DE', 'MTX.DE', 'QIA.DE',
    'HSBC', 'SHELL.L', 'BP.L', 'GSK.L', 'AZN.L', 'REL.L', 'BHP.L', 'RIO.L', 'VOD.L',
    'ULVR.L', 'HSBA.L', 'GSK.L', 'DGE.L', 'NG.L', 'BP.L', 'SHEL.L', 'BATS.L', 'IMB.L',
    'OR.PA', 'TTE.PA', 'AIR.PA', 'SAN.PA', 'LVMH.PA', 'RMS.PA', 'MC.PA', 'BNP.PA',
    'GLE.PA', 'ORA.PA', 'ENGI.PA', 'VIV.PA', 'CAP.PA', 'AC.PA', 'EL.PA',
    'NESN.SW', 'NOVN.SW', 'ROG.SW', 'UBSG.SW', 'ABBN.SW', 'SLHN.SW', 'ZURN.SW',
    'VOLV-B.ST', 'NVO', 'VWS.CO', 'CARL-B.CO', 'COLO-B.CO', 'SAMPO.HE', 'STERV.HE',
    'ISP.MI', 'ENEL.MI', 'INI.MI', 'UCG.MI', 'TRI.MI', 'BBVA.MC', 'SAN.MC', 'TEF.MC',

    # ===== KOREA =====
    '0050.KS', '0051.KS', '068270.KS', '000660.KS', '051910.KS', '207940.KS',
    '005380.KS', '012330.KS', '035420.KS', '035720.KS', '096770.KS', '066570.KS',
    '000270.KS', '096530.KS', '003670.KS', '018260.KS', '034730.KS', '055550.KS',

    # ===== INDIA =====
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDB.NS', 'BHARTIARTL.NS', 'ITC.NS',
    'KMB.NS', 'LT.NS', 'HINDUNILVR.NS', 'MARUTI.NS', 'TATAMOTORS.NS', 'WIPRO.NS',
    'AXISBANK.NS', 'KOTAKBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'BAJFINANCE.NS',
    'HDFCBANK.NS', 'SUNPHARMA.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS', 'POWERGRID.NS',

    # ===== CANADA =====
    'RY', 'TD', 'BMO', 'CNQ', 'SU', 'ENB', 'TRP', 'EOG', 'MFC', 'SLF',
    'BNS', 'CM', 'NA', 'LB', 'GWO', 'POW', 'IFC', 'TA', 'X', 'AC',
    'BAM', 'CX', 'NWC', 'ACCDY', 'LSPD', 'REAL', 'MTL', 'TSLA', 'FCR', 'RNW',

    # ===== AUSTRALIA =====
    'BHP.AX', 'RIO.AX', 'CBA.AX', 'WES.AX', 'TLS.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX',
    'CSL.AX', 'FMG.AX', 'WOW.AX', 'COL.AX', 'JBH.AX', 'ALL.AX', 'SUN.AX', 'AMP.AX',
    'BEN.AX', 'PTM.AX', 'QBE.AX', 'AIA.AX', 'ARG.AX', 'IPL.AX', 'STO.AX', 'OSH.AX',

    # ===== SOUTHEAST ASIA =====
    'D05.SI', 'U11.SI', 'C6L.SI', 'Z74.SI', 'S63.SI', 'OCBC.SI', 'DBS.SI', 'STI.SI',
    'PTT.BK', 'AOT.BK', 'CPALL.BK', 'KBANK.BK', 'SCB.BK', 'BDMS.BK', 'TRUE.BK', 'EGCO.BK',
    'BBCA.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'HMSP.JK', 'PGAS.JK', 'PTBA.JK', 'ANTM.JK',
    'MAYBANK.MY', 'PETRONAS.MY', 'CIMB.MY', 'TENAGA.MY', 'MAXIS.MY', 'DIGI.MY',
    'SMPC', 'PLDT', 'BDO', 'JFC', 'ALCO', 'RRHI',

    # ===== LATIN AMERICA =====
    'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'BBD4.SA', 'ABEV3.SA', 'JBSS3.SA', 'RAIA3.SA',
    'RENT3.SA', 'HAPV3.SA', 'LWSA3.SA', 'MGLU3.SA', 'PETR3.SA', 'VVAR3.SA',
    'AMXL.MX', 'TV', 'FEMSAU.MX', 'GMEXICOB.MX', 'KOFUBL.MX', 'CEMEXCPO.MX', 'GAPB.MX',
    'SQM', 'CENCOSUD', 'COPEC', 'SACO', 'LAFARGEHOLCIM', 'CCU', 'ENTEL',

    # ===== EMERGING MARKETS =====
    'EWZ', 'EWY', 'EWT', 'INDA', 'EWC', 'EWW', 'RSX', 'THD', 'IDX', 'MYE',
    'PHP', 'VNQ', 'TUR', 'EGY', 'KENYA', 'EPOL', 'EEMA', 'IEMG', 'SPEM', 'SCHE',
]

# Remove duplicates
ALL_TICKERS = list(set(ALL_TICKERS))


def run_market_refresh_job():
    """Background job to refresh all market data in DB."""
    logger.info(f"Starting market refresh job for {len(ALL_TICKERS)} tickers...")

    start_time = time.time()
    success_count = 0
    fail_count = 0
    batch_size = 50

    # Refresh in batches to avoid overwhelming yfinance
    for i in range(0, len(ALL_TICKERS), batch_size):
        batch = ALL_TICKERS[i:i + batch_size]

        try:
            # Use the existing market service batch fetch (writes to DB)
            results = market_service.get_batch(batch, force_refresh=True)

            # Persist to DB via market.py logic (upsert)
            from app.database import SessionLocal
            from app.models.models import MarketData

            db = SessionLocal()
            try:
                for quote in results:
                    market_data = MarketData(
                        ticker=quote["ticker"],
                        name=quote["name"],
                        market_type=quote["market_type"],
                        price=quote["price"],
                        volume=quote.get("volume", 0),
                        timestamp=quote["timestamp"]
                    )
                    db.merge(market_data)
                db.commit()
                success_count += len(results)
            finally:
                db.close()

            logger.info(f"Refreshed batch {i//batch_size + 1}: {len(results)}/{len(batch)} tickers")

        except Exception as e:
            logger.error(f"Batch refresh error at batch {i//batch_size + 1}: {e}")
            fail_count += len(batch)

        # Small delay between batches to be nice to yfinance
        time.sleep(0.5)

    elapsed = time.time() - start_time
    logger.info(
        f"Market refresh job completed in {elapsed:.1f}s: "
        f"success={success_count}, failed={fail_count}"
    )

    return {
        "total": len(ALL_TICKERS),
        "success": success_count,
        "failed": fail_count,
        "elapsed_seconds": elapsed
    }


def check_db_has_recent_data(max_age_seconds: int = 900) -> bool:
    """Check if DB has market data updated within the last max_age_seconds.

    Args:
        max_age_seconds: Maximum age in seconds (default 900 = 15 minutes)

    Returns:
        True if DB has recent data, False if empty or stale
    """
    from app.database import SessionLocal
    from app.models.models import MarketData
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        latest = db.query(MarketData).order_by(MarketData.timestamp.desc()).first()
        if not latest:
            return False

        age = (datetime.now() - latest.timestamp).total_seconds()
        return age < max_age_seconds
    finally:
        db.close()


def run_initial_market_seed():
    """One-time seed of all market data on startup (non-blocking).

    Skips seed if DB has recent data (within 15 minutes).
    """
    if check_db_has_recent_data(max_age_seconds=900):
        logger.info("DB already has recent market data, skipping initial seed")
        return {"skipped": True, "reason": "recent_data_exists"}

    logger.info("Running initial market data seed on startup...")
    try:
        result = run_market_refresh_job()
        logger.info(f"Initial seed completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Initial seed failed: {e}")
        return {"error": str(e)}
