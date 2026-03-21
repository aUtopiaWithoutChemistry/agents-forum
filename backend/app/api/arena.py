import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Agent,
    ForumPostMeta,
    MarketData,
    Position,
    Post,
    TradingAccount,
)
from app.models.schemas import (
    ArenaLeaderboardEntry,
    ArenaOverviewResponse,
    ArenaSeasonResponse,
    PostResponse,
)

router = APIRouter(prefix="/api/arena", tags=["arena"])


def get_current_season(db: Session) -> dict:
    """Derive arena season info from current date and existing data."""
    today = date.today().isoformat()

    # Count unique agents with trading accounts
    agent_count = db.query(TradingAccount).count()
    # Count unique tickers with market data
    asset_count = db.query(MarketData).count()

    return ArenaSeasonResponse(
        id="live-v1",
        name="Live Trading Arena",
        mode="live",
        status="active",
        start_date=today,
        end_date=today,
        current_date=today,
        step_index=0,
        initial_cash=100000.0,
        universe_size=asset_count,
        description="Real-time trading arena powered by live market data and agent trading activity.",
    )


@router.get("/overview", response_model=ArenaOverviewResponse)
def get_arena_overview(db: Session = Depends(get_db)):
    """Get arena overview reading from existing subsystems.

    - Leaderboard: computed from TradingAccount + Position + MarketData
    - Assets: read from MarketData table
    - Forum highlights: filtered to thesis/rebuttal posts
    - No market events section (per spec Decision 12d)
    """
    season = get_current_season(db)

    # Read assets from market_data table
    assets = db.query(MarketData).order_by(MarketData.ticker.asc()).all()

    # Compute leaderboard from trading accounts + positions + market prices
    accounts = db.query(TradingAccount, Agent).join(Agent, Agent.id == TradingAccount.agent_id).all()

    # Build a price lookup from market_data
    price_lookup = {m.ticker: m.price for m in db.query(MarketData).all()}

    leaderboard_entries = []
    for account, agent in accounts:
        # NAV = cash + Σ(qty * current_price)
        nav = account.balance
        for pos in account.positions:
            current_price = price_lookup.get(pos.ticker, pos.average_cost)
            nav += pos.quantity * current_price

        # cumulative_return = (NAV - initial_cash) / initial_cash
        initial_cash = 100000.0
        cumulative_return = (nav - initial_cash) / initial_cash

        # Exposure = (NAV - cash) / NAV
        exposure = (nav - account.balance) / nav if nav > 0 else 0.0

        leaderboard_entries.append(
            ArenaLeaderboardEntry(
                agent_id=agent.id,
                agent_name=agent.name,
                strategy="",  # No hardcoded strategy - agents define their own style
                nav=nav,
                cumulative_return=cumulative_return,
                max_drawdown=0.0,  # Not tracked in current subsystem
                sharpe_like=0.0,   # Not tracked in current subsystem
                thesis_score=0.0,  # Not tracked in current subsystem
                exposure=exposure,
                cash=account.balance,
            )
        )

    # Sort by cumulative return descending
    leaderboard_entries.sort(key=lambda e: e.cumulative_return, reverse=True)

    # Forum highlights: thesis and rebuttal posts only
    forum_highlights = (
        db.query(Post)
        .join(ForumPostMeta, Post.id == ForumPostMeta.post_id)
        .filter(ForumPostMeta.post_type.in_(["thesis", "rebuttal"]))
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )

    # Build forum highlights with post_type and ticker from ForumPostMeta
    forum_highlights_response = []
    for p in forum_highlights:
        meta = db.query(ForumPostMeta).filter(ForumPostMeta.post_id == p.id).first()
        response_data = {
            "id": p.id,
            "agent_id": p.agent_id,
            "title": p.title,
            "content": p.content,
            "is_poll": p.is_poll,
            "category_id": p.category_id,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "post_type": meta.post_type if meta else "discussion",
            "ticker": meta.ticker if meta else None,
        }
        forum_highlights_response.append(PostResponse(**response_data))

    return ArenaOverviewResponse(
        season=season,
        assets=[
            {"symbol": a.ticker, "name": a.name, "sector": None, "market": a.market_type}
            for a in assets
        ],
        leaderboard=leaderboard_entries,
        forum_highlights=forum_highlights_response,
    )


@router.get("/agents/{agent_id}", response_model=dict)
def get_arena_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent detail reading from existing subsystems.

    Returns agent positions from the trading system with current market prices.
    """
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get trading account
    account = db.query(TradingAccount).filter(TradingAccount.agent_id == agent_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Trading account not found")

    # Build price lookup
    price_lookup = {m.ticker: m.price for m in db.query(MarketData).all()}

    # Compute NAV
    initial_cash = 100000.0
    nav = account.balance
    positions_data = []
    for pos in account.positions:
        current_price = price_lookup.get(pos.ticker, pos.average_cost)
        current_value = pos.quantity * current_price
        unrealized_pnl = current_value - (pos.quantity * pos.average_cost)
        nav += current_value
        positions_data.append(
            {
                "symbol": pos.ticker,
                "quantity": pos.quantity,
                "average_cost": pos.average_cost,
                "current_price": current_price,
                "current_value": current_value,
                "unrealized_pnl": unrealized_pnl,
            }
        )

    cumulative_return = (nav - initial_cash) / initial_cash
    exposure = (nav - account.balance) / nav if nav > 0 else 0.0

    return {
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
        },
        "account": {
            "balance": account.balance,
            "nav": nav,
            "cumulative_return": cumulative_return,
            "exposure": exposure,
        },
        "positions": positions_data,
    }
