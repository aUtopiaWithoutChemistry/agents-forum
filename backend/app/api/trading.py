"""Trading Account API endpoints"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app.models.models import TradingAccount, Position, Order, AuditLog
from app.models.schemas import (
    TradingAccountResponse,
    PositionResponse,
    BalanceResponse,
    OrderCreate,
    OrderResponse
)
from app.services.market import market_service


def get_authenticated_agent_id(request: Request) -> Optional[str]:
    """Extract agent_id from request headers (for agent auth)."""
    return request.headers.get("X-Agent-ID")

router = APIRouter(prefix="/api/trading", tags=["trading"])


def get_or_create_trading_account(db: Session, agent_id: str) -> TradingAccount:
    """Get or create a trading account for an agent"""
    account = db.query(TradingAccount).filter(
        TradingAccount.agent_id == agent_id
    ).first()

    if not account:
        account = TradingAccount(
            agent_id=agent_id,
            balance=100000.0  # Initial simulated balance
        )
        db.add(account)
        db.commit()
        db.refresh(account)

        # Log account creation
        audit = AuditLog(
            agent_id=agent_id,
            action="account_create",
            target_type="trading_account",
            target_id=account.id,
            details='{"initial_balance": 100000.0}'
        )
        db.add(audit)
        db.commit()

    return account


def log_audit(db: Session, agent_id: str, action: str, target_type: str,
              target_id: int, details: dict = None):
    """Helper to create audit log entries"""
    audit = AuditLog(
        agent_id=agent_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=json.dumps(details) if details else None
    )
    db.add(audit)


@router.get("/account", response_model=TradingAccountResponse)
def get_account(agent_id: str):
    """Get trading account for agent (creates if not exists)"""
    db = next(get_db())
    try:
        return get_or_create_trading_account(db, agent_id)
    finally:
        db.close()


@router.get("/balance", response_model=BalanceResponse)
def get_balance(agent_id: str):
    """Get balance and positions with current market values"""
    db = next(get_db())
    try:
        account = get_or_create_trading_account(db, agent_id)

        positions = db.query(Position).filter(
            Position.account_id == account.id
        ).all()

        position_responses = []
        total_position_value = 0.0

        for pos in positions:
            # Get current market price
            quote = market_service.get_quote(pos.ticker)
            current_price = quote["price"] if quote else pos.average_cost

            current_value = pos.quantity * current_price
            unrealized_pnl = current_value - (pos.quantity * pos.average_cost)

            total_position_value += current_value

            position_responses.append(PositionResponse(
                id=pos.id,
                ticker=pos.ticker,
                quantity=pos.quantity,
                average_cost=pos.average_cost,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl
            ))

        total_value = account.balance + total_position_value

        return BalanceResponse(
            agent_id=agent_id,
            balance=account.balance,
            positions=position_responses,
            total_value=total_value
        )
    finally:
        db.close()


@router.get("/positions", response_model=list[PositionResponse])
def get_positions(agent_id: str, request: Request):
    """Get all positions for an agent.

    Position privacy: agents can only see their own positions.
    Humans (authenticated via API key) can view any agent's positions.
    """
    db = next(get_db())
    try:
        # Enforce position privacy: agents cannot view other agents' positions
        requesting_agent_id = get_authenticated_agent_id(request)
        auth_type = getattr(request.state, 'auth_type', None)

        # If authenticated as an agent (not a human user), enforce privacy
        if auth_type == 'agent' and requesting_agent_id and requesting_agent_id != agent_id:
            raise HTTPException(
                status_code=403,
                detail="Agents can only view their own positions"
            )

        account = get_or_create_trading_account(db, agent_id)

        positions = db.query(Position).filter(
            Position.account_id == account.id
        ).all()

        result = []
        for pos in positions:
            quote = market_service.get_quote(pos.ticker)
            current_price = quote["price"] if quote else pos.average_cost
            current_value = pos.quantity * current_price
            unrealized_pnl = current_value - (pos.quantity * pos.average_cost)

            result.append(PositionResponse(
                id=pos.id,
                ticker=pos.ticker,
                quantity=pos.quantity,
                average_cost=pos.average_cost,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl
            ))

        return result
    finally:
        db.close()


@router.post("/order", response_model=OrderResponse)
def create_order(order: OrderCreate):
    """Create and execute a buy/sell order at current market price"""
    if order.order_type not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="order_type must be 'buy' or 'sell'")
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be positive")

    # Get current market price
    quote = market_service.get_quote(order.ticker)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Ticker {order.ticker} not found")

    current_price = quote["price"]

    db = next(get_db())
    try:
        account = get_or_create_trading_account(db, order.agent_id)

        if order.order_type == "buy":
            total_cost = order.quantity * current_price

            # Check balance
            if account.balance < total_cost:
                raise HTTPException(status_code=400, detail="Insufficient funds")

            # Deduct from balance
            account.balance -= total_cost

            # Update or create position
            position = db.query(Position).filter(
                Position.account_id == account.id,
                Position.ticker == order.ticker
            ).first()

            if position:
                # Update average cost
                total_shares = position.quantity + order.quantity
                position.average_cost = (
                    (position.quantity * position.average_cost + order.quantity * current_price) / total_shares
                )
                position.quantity = total_shares
            else:
                position = Position(
                    account_id=account.id,
                    ticker=order.ticker,
                    quantity=order.quantity,
                    average_cost=current_price
                )
                db.add(position)

            # Create order
            db_order = Order(
                account_id=account.id,
                ticker=order.ticker,
                order_type="buy",
                quantity=order.quantity,
                price=current_price,
                status="executed",
                executed_at=datetime.now()
            )
            db.add(db_order)

            log_audit(db, order.agent_id, "order_execute", "order", db_order.id, {
                "ticker": order.ticker,
                "type": "buy",
                "quantity": order.quantity,
                "price": current_price
            })

        else:  # sell
            # Check holdings
            position = db.query(Position).filter(
                Position.account_id == account.id,
                Position.ticker == order.ticker
            ).first()

            if not position or position.quantity < order.quantity:
                raise HTTPException(status_code=400, detail="Insufficient holdings")

            # Update position
            position.quantity -= order.quantity
            if position.quantity == 0:
                db.delete(position)

            # Add to balance
            proceeds = order.quantity * current_price
            account.balance += proceeds

            # Create order
            db_order = Order(
                account_id=account.id,
                ticker=order.ticker,
                order_type="sell",
                quantity=order.quantity,
                price=current_price,
                status="executed",
                executed_at=datetime.now()
            )
            db.add(db_order)

            log_audit(db, order.agent_id, "order_execute", "order", db_order.id, {
                "ticker": order.ticker,
                "type": "sell",
                "quantity": order.quantity,
                "price": current_price
            })

        db.commit()
        db.refresh(db_order)

        return db_order

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(agent_id: str, status: Optional[str] = None):
    """Get all orders for an agent"""
    db = next(get_db())
    try:
        account = get_or_create_trading_account(db, agent_id)

        query = db.query(Order).filter(Order.account_id == account.id)
        if status:
            query = query.filter(Order.status == status)

        orders = query.order_by(Order.created_at.desc()).all()
        return orders
    finally:
        db.close()
