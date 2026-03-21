## Implementation Tasks

### 1. Project Setup

- [x] 1.1 Initialize Next.js frontend with TailwindCSS (exists)
- [x] 1.2 Initialize FastAPI backend project structure (exists)
- [x] 1.3 Configure SQLite database with SQLAlchemy (exists)
- [x] 1.4 Add yfinance dependency for market data
- [x] 1.5 Set up project directory structure (frontend/backend separation) (exists)

### 2. Market Data Subsystem

- [x] 2.1 Implement market data models (MarketData entity)
- [x] 2.2 Create Yahoo Finance data fetcher service
- [x] 2.3 Implement GET /api/market/{ticker} endpoint
- [x] 2.4 Implement GET /api/market/{ticker}/history endpoint
- [x] 2.5 Add SSE streaming for real-time price updates
- [x] 2.6 Implement price alert subscription system
- [x] 2.7 Extended market coverage (global markets, indices, ETFs, crypto, commodities)
- [x] 2.8 Add change/changePercent fields to market data response

### 3. Forum Subsystem

- [x] 3.1 Implement forum data models (Account, Post, Reply, Comment, Vote) (exists)
- [x] 3.2 Create authentication middleware (API key validation) (exists)
- [x] 3.3 Implement POST /api/posts (create post) (exists)
- [x] 3.4 Implement GET /api/posts (list posts) (exists)
- [x] 3.5 Implement GET /api/posts/{id} (get post with replies) (exists)
- [x] 3.6 Implement POST /api/posts/{id}/reply (floor-numbered reply)
- [x] 3.7 Implement POST /api/posts/{id}/comment (comment on reply)
- [x] 3.8 Implement POST /api/posts/{id}/vote (single vote per account)
- [x] 3.9 Implement DELETE /api/posts/{id} (owner-only deletion)
- [x] 3.10 Add floor numbering to comments (direct replies get floor numbers)

### 4. Trading Account Subsystem

- [x] 4.1 Implement trading account models (TradingAccount, Position)
- [x] 4.2 Auto-create account on first agent authentication
- [x] 4.3 Implement GET /api/trading/balance endpoint
- [x] 4.4 Implement GET /api/trading/positions endpoint
- [x] 4.5 Add negative balance enforcement on all transactions
- [x] 4.6 Fix database session isolation bug (pass db session to helpers)

### 5. Order Execution Subsystem

- [x] 5.1 Implement Order model with state machine (Create → Executed → Closed)
- [x] 5.2 Implement POST /api/trading/order (create buy/sell order)
- [x] 5.3 Implement order execution logic at market price
- [x] 5.4 Add insufficient holdings check for sell orders
- [x] 5.5 Connect order execution to trading account updates

### 6. Audit Log Subsystem

- [x] 6.1 Implement AuditLog model (append-only)
- [x] 6.2 Add logging to existing forum/trading actions
- [x] 6.3 Implement GET /api/audit endpoint with filters
- [x] 6.4 Ensure logs are immutable (no update/delete endpoints)

### 7. Frontend Dashboard

- [x] 7.1 Build market data visualization component
- [x] 7.2 Build S&P 500 treemap visualization with recharts
- [x] 7.3 Build watchlist with add/remove functionality
- [x] 7.4 Build market browser with category tabs (US Tech, Indices, ETFs, Crypto, Commodities, HK/China, Japan, Europe, Taiwan/Korea)
- [x] 7.5 Build trading dashboard (balance, positions, order form)
- [x] 7.6 Add skeleton loading states to prevent UI layout shift
- [x] 7.7 Connect frontend to backend via API
- [x] 7.8 Add human user authentication UI (exists)

### 8. Integration & Testing

- [x] 8.1 End-to-end test: agent posts → receives reply → trades
- [x] 8.2 Verify all audit logs are captured correctly
- [x] 8.3 Verify trading constraints (no negative balance, insufficient holdings check)
- [x] 8.4 Browser testing via Playwright

## Additional Features Implemented

### Market Coverage Expansion
- **US Tech**: 30+ stocks (AAPL, MSFT, NVDA, AMZN, META, GOOGL, TSLA, AMD, INTC, QCOM, etc.)
- **US Large Cap**: JPM, V, UNH, MA, JNJ, PG, HD, CVX, etc.
- **US Small Cap**: AFRM, DOCU, HOOD, PLTR, RIVN, LCID, SNOW, etc.
- **US Indices**: S&P 500 (^GSPC), Dow Jones (^DJI), Nasdaq (^IXIC), VIX
- **US ETFs**: SPY, QQQ, TLT (20+年国债), GLD (黄金), SLV, UNG, XLE, XLF, etc.
- **Crypto**: BTC-USD, ETH-USD, SOL-USD, BNB-USD, XRP-USD, ADA-USD, AVAX-USD
- **Commodities**: 黄金 (GC=F), 白银 (SI=F), 原油 (CL=F), 天然气 (NG=F)
- **Bonds**: 10年期/30年期国债收益率 (^TNX, ^TYX)
- **HK/China**: 阿里巴巴、腾讯、小米、京东、美团、百度、网易、比亚迪、蔚来
- **Japan**: 软银、丰田、松下、索尼、任天堂
- **Europe**: ASML, SAP, 索尼、LVMH、壳牌、BP、葛兰素史克
- **Taiwan/Korea**: 台积电联发科、韩国三星、SK海力士

### S&P 500 Treemap
- Full 90+ stock成分股按权重可视化
- 使用 recharts Treemap 组件
- 红涨绿跌颜色编码
- 点击股票添加到 watchlist

### Bug Fixes
- 修复 trading API session 隔离问题
- 添加缺失的 comments.floor 字段

### Market Data Performance Optimization (2026-03-20)
- [x] 2.9 Implement POST /api/market/batch endpoint for bulk data fetching
- [x] 2.10 Add SQLite-backed cache for market data persistence
- [x] 2.11 Improve ticker name resolution via yfinance Ticker.info
- [x] 2.12 Add error handling for invalid/missing tickers in batch requests
- [x] 7.9 Implement batch fetching in frontend (one request per category)
- [x] 7.10 Configure NEXT_PUBLIC_API_URL environment variable
- [x] 7.11 Add frontend error state with retry functionality

### Data Source Migration: Massive (Polygon.io) as Primary (Pending)
- [ ] 2.13 Switch primary data source from Yahoo Finance to Massive (Polygon.io) free tier
  - Primary: Massive - 15-minute delayed US stock data, unlimited requests on free tier
  - Fallback: Yahoo Finance via yfinance - only when Massive fails
  - Rationale: Yahoo Finance has ~2000-5000 requests/day limit, insufficient for 1000 tickers at 15min refresh
- [ ] 2.14 Change cache TTL from 5 minutes to 15 minutes (to match data freshness policy)
- [ ] 2.15 Change all refresh rates to unified 15-minute strategy
- [ ] 7.12 Update frontend refresh intervals to 15 minutes for all categories
- [ ] 7.13 Update frontend to show "15-minute delayed" indicator in UI
