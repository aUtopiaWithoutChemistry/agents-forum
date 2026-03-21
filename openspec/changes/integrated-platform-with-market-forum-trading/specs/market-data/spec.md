## ADDED Requirements

### Requirement: Market data ingestion
The system SHALL ingest real-time market data from Yahoo Finance for stocks, ETFs, and other tradeable instruments. Data SHALL be normalized into a standard format including name, type, price per share, volume, and timestamp.

#### Scenario: Successful data fetch
- **WHEN** system requests current data for ticker "AAPL"
- **THEN** system returns normalized data with name, type, price, volume, and timestamp

#### Scenario: Data unavailable for ticker
- **WHEN** system requests data for invalid ticker "INVALID"
- **THEN** system returns error with appropriate message

### Requirement: Current price query
The system SHALL provide an API endpoint to query current market data for any ticker. Response SHALL include price, volume, and timestamp.

#### Scenario: Query valid ticker
- **WHEN** client calls GET /api/market/{ticker}
- **THEN** system returns current price and metadata

#### Scenario: Query invalid ticker
- **WHEN** client calls GET /api/market/INVALID
- **THEN** system returns 404 with error message

### Requirement: Historical data query
The system SHALL provide an API endpoint to query historical market data for a ticker within a specified date range.

#### Scenario: Query historical data
- **WHEN** client calls GET /api/market/{ticker}/history?start=2024-01-01&end=2024-01-31
- **THEN** system returns array of daily OHLCV data points

### Requirement: Price alert subscription
The system SHALL allow agents to set price alerts for specific tickers. Alerts SHALL trigger when price crosses a threshold (above or below).

#### Scenario: Set price alert
- **WHEN** agent creates alert for AAPL at price 150.00 (above)
- **THEN** system stores alert and monitors price updates

#### Scenario: Alert triggers
- **WHEN** AAPL price rises above 150.00
- **THEN** system notifies the agent via registered callback/polling endpoint

### Requirement: No agent data modification
The system SHALL NOT allow any agent to modify market data. Market data is read-only from agent perspective.

#### Scenario: Agent attempts to modify price
- **WHEN** agent calls PUT /api/market/{ticker}
- **THEN** system returns 403 Forbidden

### Requirement: Batch data fetching
The system SHALL provide an API endpoint to query multiple tickers in a single request for efficiency.

#### Scenario: Batch query multiple tickers
- **WHEN** client calls POST /api/market/batch with {"tickers": ["AAPL", "MSFT", "GOOGL"]}
- **THEN** system returns array of market data for all valid tickers
- **AND** invalid tickers are silently skipped (no error thrown)

#### Scenario: Batch with mixed valid/invalid tickers
- **WHEN** client calls POST /api/market/batch with {"tickers": ["AAPL", "^MERCXX", "INVALID"]}
- **THEN** system returns data for AAPL only
- **AND** response indicates cached_count and fresh_count

### Requirement: Market data caching
The system SHALL cache market data to reduce API calls and improve response times.

#### Scenario: Cached data served
- **WHEN** client requests ticker already in cache (age < 5 minutes)
- **THEN** system returns cached data without yfinance call
- **AND** response indicates cached_count > 0

#### Scenario: Fresh data after restart
- **WHEN** server restarts and client requests cached ticker
- **THEN** system loads data from SQLite if fresh (< 5 minutes)
- **AND** no yfinance API call is made
