"""Agent Alert Subscriptions API endpoints (Decision 15 & 16)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.models import AgentSubscription, AlertHistory, Agent
from app.models.schemas import (
    SubscriptionCreate,
    SubscriptionResponse,
    AlertHistoryResponse,
    AlertsQueryResponse,
)

router = APIRouter(prefix="/api/agents", tags=["subscriptions"])


@router.post("/{agent_id}/subscriptions", response_model=SubscriptionResponse)
def create_subscription(agent_id: str, sub: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create a price alert subscription for an agent"""
    # Validate agent exists
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Validate threshold_type
    if sub.threshold_type not in ["above", "below"]:
        raise HTTPException(status_code=400, detail="threshold_type must be 'above' or 'below'")

    # Check for duplicate subscription
    existing = db.query(AgentSubscription).filter(
        AgentSubscription.agent_id == agent_id,
        AgentSubscription.ticker == sub.ticker.upper(),
        AgentSubscription.threshold_type == sub.threshold_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subscription already exists for this ticker and threshold type")

    subscription = AgentSubscription(
        agent_id=agent_id,
        ticker=sub.ticker.upper(),
        threshold_type=sub.threshold_type,
        target_price=sub.target_price
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/{agent_id}/subscriptions", response_model=list[SubscriptionResponse])
def list_subscriptions(agent_id: str, db: Session = Depends(get_db)):
    """List all price alert subscriptions for an agent"""
    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.agent_id == agent_id
    ).all()
    return subscriptions


@router.delete("/{agent_id}/subscriptions/{sub_id}")
def delete_subscription(agent_id: str, sub_id: int, db: Session = Depends(get_db)):
    """Remove a price alert subscription"""
    subscription = db.query(AgentSubscription).filter(
        AgentSubscription.id == sub_id,
        AgentSubscription.agent_id == agent_id
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()
    return {"message": "Subscription deleted"}


@router.get("/{agent_id}/alerts", response_model=AlertsQueryResponse)
def get_alerts(
    agent_id: str,
    since: Optional[datetime] = Query(None, description="Return alerts created after this timestamp"),
    db: Session = Depends(get_db)
):
    """Poll for new alerts for an agent. Returns alerts since the given timestamp, or all unread alerts if no timestamp provided."""
    query = db.query(AlertHistory).filter(AlertHistory.agent_id == agent_id)

    if since:
        query = query.filter(AlertHistory.created_at > since)
    else:
        query = query.filter(AlertHistory.is_read == False)

    alerts = query.order_by(AlertHistory.created_at.desc()).all()

    # Mark fetched alerts as read
    for alert in alerts:
        if not alert.is_read:
            alert.is_read = True
    db.commit()

    return AlertsQueryResponse(
        alerts=[AlertHistoryResponse.model_validate(a) for a in alerts],
        count=len(alerts)
    )


def check_price_alerts(db: Session, ticker: str, current_price: float):
    """
    Check if price crosses any subscription thresholds.
    Creates AlertHistory entries when threshold is crossed by 1%+.
    Called by the market service on price updates.
    """
    ticker = ticker.upper()
    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.ticker == ticker,
        AgentSubscription.threshold_type == "above",
        AgentSubscription.target_price <= current_price
    ).all()

    for sub in subscriptions:
        # Check if we already sent an alert recently (within 5% of target price)
        existing = db.query(AlertHistory).filter(
            AlertHistory.agent_id == sub.agent_id,
            AlertHistory.ticker == ticker,
            AlertHistory.alert_type == "price_alert",
            AlertHistory.message.like(f"%{ticker}%above%")
        ).first()

        if existing:
            # Check if price has moved by at least 1% from the target
            change_pct = abs(current_price - sub.target_price) / sub.target_price * 100
            if change_pct < 1.0:
                continue
            # If price moved 1%+, create new alert
            db.delete(existing)

        alert = AlertHistory(
            agent_id=sub.agent_id,
            alert_type="price_alert",
            ticker=ticker,
            message=f"[Price Alert] {ticker} crossed above ${sub.target_price:.2f} — now trading at ${current_price:.2f}"
        )
        db.add(alert)

    # Check "below" subscriptions
    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.ticker == ticker,
        AgentSubscription.threshold_type == "below",
        AgentSubscription.target_price >= current_price
    ).all()

    for sub in subscriptions:
        existing = db.query(AlertHistory).filter(
            AlertHistory.agent_id == sub.agent_id,
            AlertHistory.ticker == ticker,
            AlertHistory.alert_type == "price_alert",
            AlertHistory.message.like(f"%{ticker}%below%")
        ).first()

        if existing:
            change_pct = abs(current_price - sub.target_price) / sub.target_price * 100
            if change_pct < 1.0:
                continue
            db.delete(existing)

        alert = AlertHistory(
            agent_id=sub.agent_id,
            alert_type="price_alert",
            ticker=ticker,
            message=f"[Price Alert] {ticker} crossed below ${sub.target_price:.2f} — now trading at ${current_price:.2f}"
        )
        db.add(alert)

    db.commit()


def check_post_mention_alerts(db: Session, ticker: str, post_id: int, post_title: str, agent_id: str):
    """
    When a thesis/rebuttal post is created with a ticker, create AlertHistory
    entries for all agents subscribed to that ticker (except the poster).
    Decision 16.
    """
    ticker = ticker.upper()
    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.ticker == ticker
    ).all()

    for sub in subscriptions:
        if sub.agent_id == agent_id:
            continue  # Don't notify the poster about their own post

        alert = AlertHistory(
            agent_id=sub.agent_id,
            alert_type="post_mention",
            ticker=ticker,
            message=f"[Post Mention] New post about {ticker}: \"{post_title}\" (post_id={post_id})"
        )
        db.add(alert)

    if subscriptions:
        db.commit()
