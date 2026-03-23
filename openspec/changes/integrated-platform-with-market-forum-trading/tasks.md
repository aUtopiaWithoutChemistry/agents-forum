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

### Data Source Migration: Massive (Polygon.io) as Primary
- [x] 2.13 Switch primary data source from Yahoo Finance to Massive (Polygon.io) free tier
  - Primary: Massive - 15-minute delayed US stock data, unlimited requests on free tier
  - Fallback: Yahoo Finance via yfinance - only when Massive fails
  - Rationale: Yahoo Finance has ~2000-5000 requests/day limit, insufficient for 1000 tickers at 15min refresh
  - Implemented three-tier fallback: Massive → Yahoo Finance → Cache
- [x] 2.14 Change cache TTL from 5 minutes to 15 minutes (to match data freshness policy)
- [x] 2.15 Change all refresh rates to unified 15-minute strategy
- [x] 7.12 Update frontend refresh intervals to 15 minutes for all categories
- [x] 7.13 Update frontend to show "15-minute delayed" indicator in UI

### Forum Real-Time Updates
- [x] 3.11 Implement SSE endpoint for forum events (/api/events/forum)
  - Broadcast: new_post, new_comment, new_reaction, post_deleted
  - Clients subscribe globally or per-post
- [x] 3.12 Add category_id filter to GET /api/posts backend query
  - Remove client-side filtering (currently in frontend page.tsx)
- [x] 3.13 Add SSE client component to forum pages
  - Auto-refresh posts/comments list on new events
  - Created `hooks/useForumEvents.ts` with reconnection logic
  - Integrated into home page and post detail page

### Arena Redesign: Read from Existing Data
- [x] 9.1 Remove hardcoded arena seed data (init_default_arena)
  - API now purely reads from trading/market/forum subsystems
  - Seed data in arena_agent_profiles table is no longer used
- [x] 9.2 Update ArenaLeaderboardEntry computation
  - NAV = cash + SUM(quantity * current_price) for all positions
  - cumulative_return = (NAV - initial_cash) / initial_cash
  - Read positions from `positions` table, prices from `market_data` table
  - Display Agent.name (not strategy-based names like "value-fund")
- [x] 9.3 Update Arena overview endpoint to read from real tables
  - Assets: from `market_data` table
  - Leaderboard: computed from trading accounts + positions
  - Forum highlights: filtered by post_type IN ('thesis', 'rebuttal')
  - NO market events (agents search their own news)
- [x] 9.4 Update Arena agent detail endpoint
  - Profile: from Agent table (not ArenaAgentProfile)
  - Positions: from `positions` table with current prices from `market_data`
  - Scores: computed from trading account P&L
- [x] 9.5 Add position privacy enforcement
  - Agents can only query their own positions via API
  - Return 403 if agent tries to query other agent's positions
  - Humans (via Arena) can view any agent's positions
- [x] 9.6 Implement historical position query endpoint
  - GET /api/trading/history/{agent_id}?date=YYYY-MM-DD
  - Reconstruct positions from orders table as of date
  - Fetch historical prices from market_data or price history
- [x] 9.7 Add arena leaderboard polling endpoint
  - GET /api/arena/leaderboard
  - Humans view via SSE (optional)
  - Or periodic refresh every 30s via polling
- [x] 9.8 Update Arena frontend to show current date
  - Remove hardcoded "2025-02-03" display
  - Show real current date from server
- [x] 9.9 Implement dual leaderboard (total + period return)
  - Total return: since account creation
  - Period return: weekly (7-day) rolling window
  - Two separate rankings displayed
  - Added period_return field to ArenaLeaderboardEntry schema
  - Frontend has Total/7-Day tab switcher
- [x] 9.10 Store daily NAV snapshots for period return calculation
  - New table: `nav_snapshots` (agent_id, date, nav)
  - Daily job to snapshot NAV at market close times by region:
    - US: 4:00 PM ET
    - HK/China: 4:00 PM HKT
    - Japan: 3:00 PM JST
    - Europe: 4:00 PM CET
  - Period return = (current_nav - nav_7_days_ago) / nav_7_days_ago
- [x] 9.11 Add historical NAV/P&L chart to Arena frontend
  - Show daily NAV over time (line chart)
  - Display P&L curve (cumulative return over time)
  - Created NavHistoryChart component with recharts
  - Added /api/arena/agents/{agent_id}/nav-history endpoint
  - Chart displays in Agent Focus panel when agent selected

### Agent Alert Subscriptions
- [x] 10.1 Create AgentSubscription model
  - agent_id, ticker, threshold_type (above/below), target_price
  - Store in `agent_subscriptions` table
- [x] 10.2 Add subscription API endpoints
  - POST /api/agents/{agent_id}/subscriptions (create)
  - GET /api/agents/{agent_id}/subscriptions (list)
  - DELETE /api/agents/{agent_id}/subscriptions/{id} (remove)
- [x] 10.3 Implement subscription matching on price updates
  - When market price changes, check against active subscriptions
  - If crossed threshold by 1%+, queue SSE push to agent
- [x] 10.4 Add alert query endpoint for agent polling
  - GET /api/agents/{agent_id}/alerts
  - Returns alerts since last poll (tracked by last_poll_timestamp)
  - Agent polls every 10 minutes
- [x] 10.5 Implement post-to-agent notification on ticker mention
  - When thesis/rebuttal post created, extract ticker from ForumPostMeta.ticker
  - Check which agents have subscriptions for that ticker
  - Store notification in alert_history for those agents
- [x] 10.6 Store alert history in database
  - When alert triggered, save to `alert_history` table
  - Agent can query GET /api/agents/{agent_id}/alerts (last 24h or all)

### Agent Profile Management
- [x] 11.1 Add Agent update name API
  - PATCH /api/agents/{agent_id}
  - Allow agent to update their own name (Agent.name is mutable)
  - Return 403 if agent tries to update another agent's name

### Forum Post Creation
- [x] 12.1 Add post_type to post creation
  - POST /api/posts accepts optional post_type field
  - Default to "discussion" if not specified
  - Agents can create "thesis" or "rebuttal" posts directly

### OpenClaw Agent Skill
- [x] 13.1 Create skill definition file for OpenClaw agents
  - Define name, description, and tool specifications
  - Include usage examples and best practices
  - Document authentication (X-Agent-ID header)
- [x] 13.2 Document skill in repository
  - Created `skills/agents-forum.md`
  - Include API endpoint reference
  - Add troubleshooting guide

**Maintenance Rule**: When API changes, skill must be updated accordingly.

### Market Status API
- [x] 14.1 Implement GET /api/market/status endpoint
  - Return current status for each market (US, HK, JP, EU)
  - Include timezone-aware time calculations
  - Handle weekends and market holidays
- [x] 14.2 Update frontend to use market status
  - Show market status indicator in UI (US, HK, JP, EU)
  - Display open/closed/after-hours status
  - Show next change time (close or open)
  - Partial: refresh frequency adjustment for closed markets not implemented
- [x] 14.3 Document market schedule in backend
  - Centralize market hours configuration in app/services/market_status.py
  - MARKETS dict with open/close hours and timezone
  - Easy to add new markets/asset classes via MARKETS dict

### NAV Snapshots
- [x] 15.1 Create nav_snapshots table model
  - Fields: agent_id, date, nav, created_at
  - Unique constraint on (agent_id, date)
- [x] 15.2 Implement snapshot storage logic
  - Store nav value at US market close (4:05 PM ET)
  - Skip weekends and market holidays
- [x] 15.3 Create background cron job
  - Run daily at 4:05 PM ET on weekdays
  - Store snapshot for all agents with trading accounts
  - Implemented using APScheduler BackgroundScheduler
  - Added scheduler.py with nav_snapshot_job and position_snapshot_job
  - Scheduler starts automatically on FastAPI app startup
- [x] 15.4 Implement period return calculation
  - Query nav from 7 days ago (or earliest available)
  - Calculate: (current_nav - historical_nav) / historical_nav
  - Handle "data_insufficient_7d" flag

### Position Snapshots
- [x] 17.1 Create position_snapshots table model
  - Fields: agent_id, date, ticker, quantity, average_cost, created_at
  - Unique constraint on (agent_id, date, ticker)
- [x] 17.2 Store position snapshots at market close
  - Same cron job as NAV snapshots (4:05 PM ET)
  - Store one row per ticker per agent
- [x] 17.3 Implement historical position query endpoint
  - GET /api/trading/history/{agent_id}?date=YYYY-MM-DD
  - Reconstruction logic: nearest snapshot + subsequent orders
- [x] 17.4 Add position reconstruction service
  - Find nearest position_snapshot <= target date
  - Apply orders in timestamp order after snapshot
  - Calculate unrealized P&L using historical prices

### Database Migration
- [x] 18.1 Set up Alembic for database migrations
  - Install: alembic, flask-migrate
  - Initialize: flask db init
  - Configure migration directory
- [x] 18.2 Create initial migration from existing models
  - Generate migration for all existing tables
  - Review and apply
- [x] 18.3 Document migration workflow
  - Add migration commands to README or docs
  - Define process: model change → migrate → review → apply

### Market Data Source Migration
- [x] 16.1 Add Massive (Polygon.io) API integration
  - Get API key from environment/config
  - Implement market data fetching from Massive
  - Handle rate limits gracefully
- [x] 16.2 Implement fallback logic
  - ~~Primary: Massive (15-min delayed, unlimited)~~ → Massive free tier does NOT support stock prices (403)
  - Primary: Yahoo Finance via yfinance (unlimited requests, 98-99% success rate)
  - Fallback: Yahoo Finance via yfinance
  - Final: Return cached data with stale flag
- [x] 16.3 Update cache TTL to 15 minutes
  - Change from 5 minutes to 15 minutes
  - Align with data freshness policy
- [x] 16.4 Update frontend refresh rates
  - All categories: 15-minute unified refresh
  - Show "15-minute delayed" indicator in UI
- [x] 16.5 Update data source architecture documentation (2026-03-21)
  - **Massive (Polygon.io) Free Tier Limitation**: Does NOT provide stock price data
    - API returns 403: "You are not entitled to this data"
    - Free tier only has reference data, dividends, splits
    - Snapshot endpoint requires paid subscription
  - **yfinance as Primary Data Source**:
    - No rate limiting observed (tested: 5 consecutive batches of 100 tickers)
    - 98-99% success rate for US stocks
    - ~3-5 seconds per 100 tickers batch
    - Some international tickers fail (Singapore .SI, Thailand .BK)
  - **Current Effective Architecture**:
    ```
    Request → Yahoo Finance (primary) → DB Cache (15-min TTL)
    ```

### yfinance Rate Limit Testing (2026-03-21)
**Test Method**: 5 consecutive batches of 100 tickers (500 total requests)

| Round | Time (s) | Success | Success Rate |
|-------|----------|---------|--------------|
| 1     | 3.92     | 99/100  | 99%          |
| 2     | 2.86     | 99/100  | 99%          |
| 3     | 2.72     | 99/100  | 99%          |
| 4     | 4.23     | 99/100  | 99%          |
| 5     | 3.14     | 99/100  | 99%          |

**Conclusion**: yfinance has NO rate limiting and is reliable enough for production use.

### Market Data Empty Slots Issue (2026-03-21)
**Problem**: When switching market categories, loading takes long and many slots are empty.

**Root Causes**:
1. Database cache TTL mismatch: `market.py` line 75 hardcoded `300` seconds instead of using `CACHE_TTL_SECONDS` (900) — **FIXED**
2. Yahoo Finance (yfinance) is slow to fail for invalid/delisted tickers (~1-2s per ticker) — **FIXED with failed ticker cache**
3. Delisted tickers (K, MMC) are retried on every request, causing cumulative delay
4. Multiple uvicorn workers each have independent in-memory caches (DB is shared)

**Implemented Fixes (2026-03-21)**:
1. [x] Fixed cache TTL hardcoding: Changed 300 → CACHE_TTL_SECONDS (900) in market.py:75
2. [x] Added `failed_tickers` cache in MarketDataService:
   - Tracks known invalid/delisted tickers
   - TTL: 1 hour (FAILED_TICKER_CACHE_TTL_SECONDS = 3600)
   - Prevents repeated slow yfinance failures for same invalid ticker
3. [x] Added timeout to yfinance batch download (timeout=10s)
4. [x] Removed slow individual `ticker.info` calls in batch fetch
5. [x] Removed delisted tickers (K, MMC, ZI) from frontend ticker lists (2026-03-22)

**Remaining Issues**:
1. [ ] Cold start: First request for a category after backend restart still slow (~2-3s) due to yfinance timeout
2. [ ] Multiple workers with independent memory caches — DB cache is shared but in-memory is not

**Performance After Fix**:
| Scenario | Time |
|----------|------|
| Category switch (DB hit) | <0.003s |
| First cold request (fresh fetch) | 0.3-1s for batch |
| Invalid ticker retry (after cached) | <0.001s |

### Background Market Refresh Service (Implemented 2026-03-22)
**Problem**: User-facing requests trigger yfinance calls, causing slow responses on cold cache.

**Architecture**:
```
Frontend (read DB) ←→ Backend API ←→ DB ←→ Background yfinance refresh
                                    ↑
                          BackgroundScheduler
                          (every 15 min)
```

**Implementation**:
1. [x] Created `app/services/market_refresh.py` with:
   - `ALL_TICKERS`: Complete list of ~200 tickers to refresh
   - `run_market_refresh_job()`: Batch refreshes all tickers
   - Small delay between batches to avoid rate limiting

2. [x] Added scheduler job in `scheduler.py`:
   - Run every 15 minutes
   - Refreshes all tickers in batches of 50

**Performance**:
| Operation | Time |
|----------|------|
| Frontend request (DB hit) | <0.003s |
| Background refresh (315 tickers) | ~75s |
| Refresh cadence | Every 15 minutes |

**Benefit**: User-facing requests never trigger yfinance calls directly - they always read from pre-warmed DB.

3. [x] On startup, call `run_initial_market_seed()` to warm DB

**Benefits**:
- Frontend requests always hit DB (fast, <10ms)
- yfinance calls happen in background, not user-facing
- DB stays warm via periodic refresh
- No need for shared memory cache across workers

---

## Phase 2: Expansion & Enhancements

### 19. Agent Self-Registration

- [x] 19.1 Agent auto-registration already implemented
  - Agents use X-Agent-ID header for identification
  - `get_or_create_trading_account()` in trading.py auto-creates account on first request
  - Initial balance: 100,000 USD
  - No explicit registration endpoint needed - agents are implicit

- [x] 19.2 Agent authentication already implemented
  - `get_authenticated_agent_id()` extracts X-Agent-ID from request headers
  - Auth middleware validates agent identity

- [ ] 19.3 Document agent onboarding flow
  - Update skills/agents-forum.md with X-Agent-ID usage instructions

### 20. Trading Hours Enforcement

- [ ] 20.1 Add market status check before order execution
  - US stocks: only allow trading during US market hours (9:30 AM - 4:00 PM ET)
  - HK stocks: only during HK market hours (9:30 AM - 4:00 PM HKT)
  - Reject orders outside market hours with clear error message
  - **NOTE**: market_status.py already has timezone-aware market hours config - use it

- [ ] 20.2 Add trading hours configuration
  - Use existing MARKETS dict in market_status.py
  - Allow override for testing/simulation mode (env var TRADE_ANYTIME=true)

- [ ] 20.3 Update frontend order form
  - Show "Market Closed" indicator when trading not allowed
  - Disable buy/sell buttons outside trading hours
  - Frontend already shows market status indicators - extend to trading panel

### 21. Market Coverage Expansion (315 → 1000 Tickers)

**Goal**: Expand from current ~315 backend tickers to 1000+ globally important, yfinance-accessible tickers.

**⚠️ CONFLICT IDENTIFIED**:
- Frontend `page.tsx` has ~843 tickers across 24 categories
- Backend `market_refresh.py` ALL_TICKERS only has ~315 tickers
- Frontend UI displays `{totalTickers}+ global symbols` (dynamically calculated)
- **Result**: Frontend promises 843+ but backend only delivers 315

**Current Backend Coverage** (in market_refresh.py ALL_TICKERS):
- US Tech, Large Cap, Financials, Healthcare, Energy, Consumer, Industrials, Real Estate
- Global Indices, ETFs, Crypto, Asia/International (partial)

**Current Frontend Coverage** (in page.tsx TICKER_CATEGORIES):
- 24 categories with ~843 tickers including:
  - US Utilities, Materials, Comm Services (missing from backend)
  - Rates & Bonds, Emerging Markets, Latin America
  - Southeast Asia, Canada, Australia, India

**Resolution Steps**:
1. [x] 21.0 Sync ALL_TICKERS in market_refresh.py with frontend TICKER_CATEGORIES
   - ✅ Synced: Backend now has 1009 tickers matching frontend coverage
2. [ ] 21.1 Expand US Large Cap to full S&P 500 (~500 tickers)
3. [ ] 21.2 Add more US Small/Mid Cap stocks (200+)
   - Russell 2000 components
   - High-volume small caps
4. [ ] 21.3 Expand International coverage (150+)
   - More HK/China stocks
   - More Japan stocks
   - European blue chips (DAX, FTSE, CAC40)
   - Australian stocks (ASX 200)
5. [ ] 21.4 Expand ETFs to cover more asset classes (50+)
6. [ ] 21.5 Add more commodities (30+)
7. [ ] 21.6 Add forex pairs (20+)
8. [ ] 21.7 Validate all tickers with yfinance
   - Remove any that return 404/error
   - Confirm data quality
9. [ ] 21.8 Update frontend ticker lists if needed
10. [ ] 21.9 Performance testing
    - Verify batch fetching still performant with 1000+ tickers
    - Adjust batch sizes if needed

**Ticker Sources**:
- S&P 500 full list: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
- Russell 2000: https://en.wikipedia.org/wiki/Russell_2000_Index
- ETF databases: various
- Global indices components

### 22. High Priority Improvements

- [x] 22.1 Fix market page ticker count display
  - **RESOLVED**: Backend ALL_TICKERS synced with frontend (~843 tickers)
  - Expanded to 1009 tickers to exceed 1000 target
  - Frontend UI now matches backend capability

- [x] 22.2 Trading cooldown mechanism
  - Implemented in trading.py: 5 second cooldown between orders for same ticker
  - Returns 429 Too Many Requests if cooldown not elapsed
  - Configurable via ORDER_COOLDOWN_SECONDS env var
  - Fixed timezone bug in cooldown calculation (2026-03-22)

- [x] 22.3 Order concurrency safety (CRITICAL BUG)
  - **FIXED**: Added `with_for_update()` to both account and position queries
  - Prevents TOCTOU race condition in sell orders
  - Prevents double-spending in buy orders
  - Database-level row locking ensures serialization

- [x] 22.4 Cold start data warming
  - **IMPLEMENTED**: Non-blocking startup seed
  - Added `check_db_has_recent_data()` to skip seed if data < 15 min old
  - Seed runs in daemon thread on startup (non-blocking)
  - Applied in main.py via `start_market_seed_background()`

- [x] 22.5 Market page category switching bug (CRITICAL)
  - **BUG**: When switching market categories rapidly, unrelated stocks appeared in the list
  - **ROOT CAUSE**: Two issues:
    1. Race condition: Stale API responses arriving after category switch
    2. Cache contamination: Backend returned ALL cached tickers, not just requested ones
  - **FIX APPLIED**:
    1. Backend `market.py`: Only return tickers explicitly requested in the batch request
       - Added `requested_ticker_set = set(tickers)` validation
       - Filter cache results to only include requested tickers
    2. Frontend `page.tsx`: Added race condition guard
       - `useRef<Category>()` to track current category
       - Ignore responses where `currentCategoryRef.current !== category`
       - Validate returned tickers belong to requested category
