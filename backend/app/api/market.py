"""Market Data API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import MarketData, MarketAlert
from app.models.schemas import (
    MarketDataResponse,
    MarketAlertCreate,
    MarketAlertResponse,
    MarketHistoryResponse,
    MarketBatchRequest,
    MarketBatchResponse
)
from app.services.market import market_service, CACHE_TTL_SECONDS
from app.services.market_status import get_all_market_statuses
from app.api.subscriptions import check_price_alerts

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/status")
def get_market_status():
    """Get current status of all markets"""
    return get_all_market_statuses()


@router.get("/{ticker}", response_model=MarketDataResponse)
def get_market_data(ticker: str):
    """Get current market data for a ticker"""
    ticker = ticker.upper()

    # Try to fetch fresh data
    quote = market_service.get_quote(ticker)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    # Store in database for caching/audit
    db = next(get_db())
    try:
        market_data = MarketData(
            ticker=quote["ticker"],
            name=quote["name"],
            market_type=quote["market_type"],
            price=quote["price"],
            volume=quote["volume"],
            timestamp=quote["timestamp"]
        )
        db.merge(market_data)  # Upsert
        db.commit()
    finally:
        db.close()

    return quote


@router.post("/batch", response_model=MarketBatchResponse)
def get_market_batch(request: MarketBatchRequest):
    """Get market data for multiple tickers in one request"""
    # Uppercase all tickers
    tickers = [t.upper().strip() for t in request.tickers]

    # DB-backed caching: load from DB first, populate in-memory cache
    db_loaded = set()
    if not request.force_refresh:
        db = next(get_db())
        try:
            db_records = db.query(MarketData).filter(MarketData.ticker.in_(tickers)).all()
            now = datetime.now()
            for record in db_records:
                # Only use DB record if fresh (within refresh interval)
                age = (now - record.timestamp).total_seconds() if record.timestamp else 999999
                if age < CACHE_TTL_SECONDS:
                    with market_service._cache_lock:
                        market_service._cache[record.ticker] = {
                            "ticker": record.ticker,
                            "name": record.name,
                            "market_type": record.market_type,
                            "price": record.price,
                            "volume": record.volume,
                            "timestamp": record.timestamp,
                            "change": None,
                            "changePercent": None,
                        }
                    db_loaded.add(record.ticker)
        finally:
            db.close()

    # Only call get_batch for tickers NOT already loaded from DB
    missing_tickers = [t for t in tickers if t not in db_loaded]
    fresh_quotes = []
    if missing_tickers:
        fresh_quotes = market_service.get_batch(missing_tickers, force_refresh=request.force_refresh)

    # Persist fresh results back to DB for durability
    if fresh_quotes:
        db = next(get_db())
        try:
            for quote in fresh_quotes:
                market_data = MarketData(
                    ticker=quote["ticker"],
                    name=quote["name"],
                    market_type=quote["market_type"],
                    price=quote["price"],
                    volume=quote["volume"],
                    timestamp=quote["timestamp"]
                )
                db.merge(market_data)
                # Check price alert subscriptions for this ticker
                check_price_alerts(db, quote["ticker"], quote["price"])
            db.commit()
        finally:
            db.close()

    # Return all: DB-loaded (from cache) + freshly fetched
    # CRITICAL: Only return data for the requested tickers (prevent cross-contamination)
    requested_ticker_set = set(tickers)
    all_quotes = []
    for ticker in tickers:
        with market_service._cache_lock:
            if ticker in market_service._cache:
                all_quotes.append(market_service._cache[ticker].copy())

    return MarketBatchResponse(
        data=all_quotes,
        cached_count=len(db_loaded),
        fresh_count=len(fresh_quotes),
        timestamp=datetime.now()
    )


@router.get("/{ticker}/history", response_model=MarketHistoryResponse)
def get_market_history(
    ticker: str,
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD")
):
    """Get historical market data for a ticker"""
    ticker = ticker.upper()

    history = market_service.get_history(ticker, start, end)
    if not history:
        raise HTTPException(status_code=404, detail=f"History not found for {ticker}")

    return history


@router.post("/alerts", response_model=MarketAlertResponse)
def create_price_alert(alert: MarketAlertCreate, agent_id: str):
    """Create a price alert for a ticker"""
    if alert.direction not in ["above", "below"]:
        raise HTTPException(status_code=400, detail="Direction must be 'above' or 'below'")

    db = next(get_db())
    try:
        existing = db.query(MarketAlert).filter(
            MarketAlert.agent_id == alert.agent_id,
            MarketAlert.ticker == alert.ticker.upper(),
            MarketAlert.direction == alert.direction
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Alert already exists for this ticker and direction")

        market_alert = MarketAlert(
            agent_id=alert.agent_id,
            ticker=alert.ticker.upper(),
            target_price=alert.target_price,
            direction=alert.direction
        )
        db.add(market_alert)
        db.commit()
        db.refresh(market_alert)
        return market_alert
    finally:
        db.close()


@router.get("/alerts", response_model=list[MarketAlertResponse])
def get_alerts(agent_id: str):
    """Get all price alerts for an agent"""
    db = next(get_db())
    try:
        alerts = db.query(MarketAlert).filter(
            MarketAlert.agent_id == agent_id,
            MarketAlert.is_triggered == False
        ).all()
        return alerts
    finally:
        db.close()


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, agent_id: str):
    """Delete a price alert"""
    db = next(get_db())
    try:
        alert = db.query(MarketAlert).filter(
            MarketAlert.id == alert_id,
            MarketAlert.agent_id == agent_id
        ).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        db.delete(alert)
        db.commit()
        return {"message": "Alert deleted"}
    finally:
        db.close()


@router.get("/alerts/check")
def check_alerts():
    """Check and trigger any price alerts (called periodically)"""
    db = next(get_db())
    try:
        # Get all untriggered alerts
        alerts = db.query(MarketAlert).filter(
            MarketAlert.is_triggered == False
        ).all()

        triggered = []
        for alert in alerts:
            quote = market_service.get_quote(alert.ticker)
            if not quote:
                continue

            price = quote["price"]
            if alert.direction == "above" and price >= alert.target_price:
                alert.is_triggered = True
                alert.triggered_at = quote["timestamp"]
                triggered.append(alert)
            elif alert.direction == "below" and price <= alert.target_price:
                alert.is_triggered = True
                alert.triggered_at = quote["timestamp"]
                triggered.append(alert)

        if triggered:
            db.commit()

        return {"triggered": len(triggered), "alerts": triggered}
    finally:
        db.close()
