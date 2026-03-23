/**
 * Market Data Blacklist
 *
 * These tickers return no data from Yahoo Finance and should not be added to categories.
 * Updated: 2026-03-22
 *
 * Reasons:
 * - Delisted or suspended
 * - Market closed / no trading
 * - Ticker format not recognized by Yahoo Finance
 */
export const MARKET_TICKER_BLACKLIST: string[] = [
  // US Stocks
  'DFS',   // Discover Financial Services - delisted
  'ABC',   // AmerisourceBergen - requires different ticker format
  'ESRX',  // Express Scripts - acquired
  'DVH',   // Herschend Family Entertainment - private/closed
  'BWH',   // Beaver Gaming - no public data
  'KSU',   // Kansas City Southern - acquired by Canadian Pacific
  'SRC',   // Spirit Realty Capital - merged
  'GWI',   // GWI Holdings - no public data
  'IPG',   // Interpublic Group - requires verification
  'DISH',  // DISH Network - requires verification

  // Japan
  '8021.T', // No price data
  '9675.T', // No price data
  '6271.T', // No price data

  // Europe
  'URW.AS',  // Unibail-Rodamco-Westfield - requires different format
  'DPW.DE',  // Deutsche Post - no price data
  'SHELL.L', // Shell - conflicts with SHEL.L
  'LVMH.PA', // LVMH - requires verification
  'INI.MI',  // Nothing found for this ticker
  'TRI.MI',  // Terna - no data

  // SE Asia / Singapore
  'D1A.SI',  // No data
  'GFIN.SI', // No data
  'P39.SI',  // No data
  'J2ND.SI', // No data

  // Latin America
  'BBA',    // Banco do Brasil - requires different format
  'BBASE',  // No data
  'PETR',   // Petrobras - requires specific Brazilian ticker
  'CPO',    // No data
  'MEGA',   // No data
  'TLEO',   // No data
];

/**
 * Check if a ticker is blacklisted
 */
export function isBlacklisted(ticker: string): boolean {
  return MARKET_TICKER_BLACKLIST.includes(ticker);
}
