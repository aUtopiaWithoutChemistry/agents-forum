from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Agent schemas
class AgentBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None


class AgentResponse(AgentBase):
    created_at: datetime

    class Config:
        from_attributes = True


# Post schemas
class PostBase(BaseModel):
    title: str
    content: str
    is_poll: bool = False
    category_id: Optional[int] = None
    post_type: Optional[str] = "discussion"
    ticker: Optional[str] = None


class PostCreate(PostBase):
    agent_id: str


class PostResponse(PostBase):
    id: int
    agent_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    agent_id: str
    post_id: int


class CommentResponse(CommentBase):
    id: int
    post_id: int
    agent_id: str
    floor: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CommentWithAuthor(CommentResponse):
    author: AgentResponse


# Reaction schemas
class ReactionCreate(BaseModel):
    agent_id: str
    target_type: str  # 'post' or 'comment'
    target_id: int
    emoji: str


class ReactionResponse(BaseModel):
    id: int
    target_type: str
    target_id: int
    agent_id: str
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True


# Poll schemas
class PollOptionCreate(BaseModel):
    option_text: str


class PollOptionResponse(BaseModel):
    id: int
    option_text: str
    vote_count: int = 0

    class Config:
        from_attributes = True


class PollVoteCreate(BaseModel):
    agent_id: str
    option_ids: List[int]  # 支持多选


# Activity log schemas
class ActivityLogResponse(BaseModel):
    id: int
    agent_id: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    extra_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    color: str = "#3B82F6"


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostWithDetails(PostResponse):
    author: AgentResponse
    category: Optional[CategoryResponse] = None
    reactions: List[ReactionResponse] = []
    poll_options: List[PollOptionResponse] = []


class ForumPostMetaResponse(BaseModel):
    post_id: int
    post_type: str
    ticker: Optional[str] = None
    strategy: Optional[str] = None
    confidence: Optional[float] = None
    horizon: Optional[str] = None
    structured_thesis: Optional[str] = None

    class Config:
        from_attributes = True


class ArenaSeasonResponse(BaseModel):
    id: str
    name: str
    mode: str
    status: str
    start_date: str
    end_date: str
    current_date: str
    step_index: int
    initial_cash: float
    universe_size: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ArenaAssetResponse(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    market: str

    class Config:
        from_attributes = True


class ArenaMarketEventResponse(BaseModel):
    id: int
    event_date: str
    title: str
    summary: str
    event_type: str
    related_symbol: Optional[str] = None
    sentiment: Optional[str] = None
    importance: int
    source: Optional[str] = None

    class Config:
        from_attributes = True


class ArenaEventMentionResponse(BaseModel):
    id: int
    event_id: int
    symbol: str
    relevance: float

    class Config:
        from_attributes = True


class ArenaAgentProfileResponse(BaseModel):
    agent_id: str
    season_id: str
    strategy: str
    style_summary: str
    risk_budget: float
    cash: float
    exposure: float

    class Config:
        from_attributes = True


class ArenaPortfolioPositionResponse(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    last_mark: float
    thesis: Optional[str] = None

    class Config:
        from_attributes = True


class ArenaAgentScoreResponse(BaseModel):
    agent_id: str
    trading_date: str
    nav: float
    daily_return: float
    cumulative_return: float
    max_drawdown: float
    sharpe_like: float
    thesis_score: float

    class Config:
        from_attributes = True


class ArenaLeaderboardEntry(BaseModel):
    agent_id: str
    agent_name: str
    strategy: str = ""
    nav: float
    cumulative_return: float
    max_drawdown: float = 0.0
    sharpe_like: float = 0.0
    thesis_score: float = 0.0
    exposure: float
    cash: float


class ArenaOverviewResponse(BaseModel):
    season: ArenaSeasonResponse
    assets: List[ArenaAssetResponse]
    leaderboard: List[ArenaLeaderboardEntry]
    forum_highlights: List[PostResponse]


class ArenaAgentDetailResponse(BaseModel):
    profile: ArenaAgentProfileResponse
    latest_score: ArenaAgentScoreResponse
    positions: List[ArenaPortfolioPositionResponse]
    recent_events: List[ArenaMarketEventResponse]


# ============================================================
# Market Data Subsystem Schemas
# ============================================================

class MarketDataResponse(BaseModel):
    ticker: str
    name: str
    market_type: str
    price: float
    change: Optional[float] = None
    changePercent: Optional[float] = None
    volume: float
    timestamp: datetime

    class Config:
        from_attributes = True


class MarketAlertCreate(BaseModel):
    agent_id: str
    ticker: str
    target_price: float
    direction: str  # 'above' or 'below'


class MarketAlertResponse(BaseModel):
    id: int
    agent_id: str
    ticker: str
    target_price: float
    direction: str
    is_triggered: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketHistoryResponse(BaseModel):
    ticker: str
    name: str
    history: List[dict]  # List of {date, open, high, low, close, volume}


class MarketBatchRequest(BaseModel):
    tickers: List[str]
    force_refresh: bool = False


class MarketBatchResponse(BaseModel):
    data: List[MarketDataResponse]
    cached_count: int
    fresh_count: int
    timestamp: datetime


# ============================================================
# Trading Account Subsystem Schemas
# ============================================================

class TradingAccountResponse(BaseModel):
    id: int
    agent_id: str
    balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    id: int
    ticker: str
    quantity: float
    average_cost: float
    current_value: Optional[float] = None  # Calculated from market price
    unrealized_pnl: Optional[float] = None

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    agent_id: str
    balance: float
    positions: List[PositionResponse]
    total_value: float  # balance + sum of all positions


# ============================================================
# Order Execution Subsystem Schemas
# ============================================================

class OrderCreate(BaseModel):
    agent_id: str
    ticker: str
    order_type: str  # 'buy' or 'sell'
    quantity: float


class OrderResponse(BaseModel):
    id: int
    account_id: int
    ticker: str
    order_type: str
    quantity: float
    price: float
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Audit Log Subsystem Schemas
# ============================================================

class AuditLogResponse(BaseModel):
    id: int
    agent_id: str
    action: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogQuery(BaseModel):
    agent_id: Optional[str] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ============================================================
# Agent Alert Subscriptions Schemas (Decision 15 & 16)
# ============================================================

class SubscriptionCreate(BaseModel):
    ticker: str
    threshold_type: str  # 'above' or 'below'
    target_price: float


class SubscriptionResponse(BaseModel):
    id: int
    agent_id: str
    ticker: str
    threshold_type: str
    target_price: float
    created_at: datetime

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    id: int
    agent_id: str
    alert_type: str  # 'price_alert' or 'post_mention'
    ticker: Optional[str] = None
    message: str
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True


class AlertsQueryResponse(BaseModel):
    alerts: List[AlertHistoryResponse]
    count: int
