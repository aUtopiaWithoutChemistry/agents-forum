"""Snapshot service - stores NAV and position snapshots at US market close (4:05 PM ET)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.models import NavSnapshot, PositionSnapshot, TradingAccount, Position, Agent
from app.services.market import market_service


class SnapshotService:
    """Service for capturing daily NAV and position snapshots"""

    def store_nav_snapshots(self, snapshot_date: date = None) -> Dict[str, int]:
        """Store NAV snapshots for all agents at market close time.

        Returns dict with 'stored' and 'skipped' counts.
        """
        if snapshot_date is None:
            snapshot_date = date.today()

        db = SessionLocal()
        stored = 0
        skipped = 0

        try:
            # Get all trading accounts
            accounts = db.query(TradingAccount).all()

            for account in accounts:
                # Calculate total portfolio value (balance + positions at current market price)
                total_value = account.balance

                positions = db.query(Position).filter(
                    Position.account_id == account.id
                ).all()

                for pos in positions:
                    quote = market_service.get_quote(pos.ticker)
                    if quote:
                        total_value += pos.quantity * quote["price"]
                    else:
                        total_value += pos.quantity * pos.average_cost

                # Upsert nav snapshot
                try:
                    existing = db.query(NavSnapshot).filter(
                        NavSnapshot.agent_id == account.agent_id,
                        NavSnapshot.date == snapshot_date
                    ).first()

                    if existing:
                        existing.nav = total_value
                    else:
                        snapshot = NavSnapshot(
                            agent_id=account.agent_id,
                            date=snapshot_date,
                            nav=total_value
                        )
                        db.add(snapshot)

                    db.commit()
                    stored += 1
                except IntegrityError:
                    db.rollback()
                    skipped += 1

            return {"stored": stored, "skipped": skipped}
        finally:
            db.close()

    def store_position_snapshots(self, snapshot_date: date = None) -> Dict[str, int]:
        """Store position snapshots for all agents at market close time.

        Returns dict with 'stored' and 'skipped' counts.
        """
        if snapshot_date is None:
            snapshot_date = date.today()

        db = SessionLocal()
        stored = 0
        skipped = 0

        try:
            accounts = db.query(TradingAccount).all()

            for account in accounts:
                positions = db.query(Position).filter(
                    Position.account_id == account.id
                ).all()

                for pos in positions:
                    try:
                        existing = db.query(PositionSnapshot).filter(
                            PositionSnapshot.agent_id == account.agent_id,
                            PositionSnapshot.date == snapshot_date,
                            PositionSnapshot.ticker == pos.ticker
                        ).first()

                        if existing:
                            existing.quantity = pos.quantity
                            existing.average_cost = pos.average_cost
                        else:
                            snapshot = PositionSnapshot(
                                agent_id=account.agent_id,
                                date=snapshot_date,
                                ticker=pos.ticker,
                                quantity=pos.quantity,
                                average_cost=pos.average_cost
                            )
                            db.add(snapshot)

                        db.commit()
                        stored += 1
                    except IntegrityError:
                        db.rollback()
                        skipped += 1

            return {"stored": stored, "skipped": skipped}
        finally:
            db.close()

    def calculate_period_return(self, agent_id: str, days: int = 7) -> Tuple[Optional[float], bool]:
        """Calculate return over the past N days.

        Returns (return_pct, data_insufficient_7d).
        Returns (None, True) if less than 7 days of data available.
        """
        db = SessionLocal()

        try:
            today = date.today()
            start_date = today - timedelta(days=days)

            # Get current NAV (latest snapshot or current balance)
            current_snapshot = db.query(NavSnapshot).filter(
                NavSnapshot.agent_id == agent_id
            ).order_by(NavSnapshot.date.desc()).first()

            if current_snapshot:
                current_nav = current_snapshot.nav
                snapshot_date = current_snapshot.date
            else:
                # Fall back to current balance
                account = db.query(TradingAccount).filter(
                    TradingAccount.agent_id == agent_id
                ).first()
                if not account:
                    return None, True

                total_value = account.balance
                positions = db.query(Position).filter(
                    Position.account_id == account.id
                ).all()
                for pos in positions:
                    quote = market_service.get_quote(pos.ticker)
                    if quote:
                        total_value += pos.quantity * quote["price"]
                    else:
                        total_value += pos.quantity * pos.average_cost
                current_nav = total_value
                snapshot_date = today

            # Get NAV from N days ago
            past_snapshot = db.query(NavSnapshot).filter(
                NavSnapshot.agent_id == agent_id,
                NavSnapshot.date <= snapshot_date - timedelta(days=days)
            ).order_by(NavSnapshot.date.desc()).first()

            if not past_snapshot:
                return None, True

            if past_snapshot.nav == 0:
                return None, True

            period_return = ((current_nav - past_snapshot.nav) / past_snapshot.nav) * 100
            return round(period_return, 4), False
        finally:
            db.close()

    def get_nav_history(self, agent_id: str, days: int = 30) -> List[NavSnapshot]:
        """Get NAV history for an agent over the past N days."""
        db = SessionLocal()
        try:
            start_date = date.today() - timedelta(days=days)
            return db.query(NavSnapshot).filter(
                NavSnapshot.agent_id == agent_id,
                NavSnapshot.date >= start_date
            ).order_by(NavSnapshot.date.asc()).all()
        finally:
            db.close()

    def get_position_snapshots(self, agent_id: str, snapshot_date: date) -> List[PositionSnapshot]:
        """Get all position snapshots for an agent on a specific date."""
        db = SessionLocal()
        try:
            return db.query(PositionSnapshot).filter(
                PositionSnapshot.agent_id == agent_id,
                PositionSnapshot.date == snapshot_date
            ).all()
        finally:
            db.close()

    def get_latest_position_snapshot_date(self, agent_id: str) -> Optional[date]:
        """Get the most recent snapshot date for an agent."""
        db = SessionLocal()
        try:
            latest = db.query(PositionSnapshot).filter(
                PositionSnapshot.agent_id == agent_id
            ).order_by(PositionSnapshot.date.desc()).first()
            return latest.date if latest else None
        finally:
            db.close()

    def get_orders_since(self, agent_id: str, since_date: date, db: Session) -> List:
        """Get all orders for an agent since a given date (for historical reconstruction)."""
        from app.models.models import TradingAccount, Order

        account = db.query(TradingAccount).filter(
            TradingAccount.agent_id == agent_id
        ).first()

        if not account:
            return []

        return db.query(Order).filter(
            Order.account_id == account.id,
            Order.executed_at >= datetime.combine(since_date, datetime.min.time())
        ).order_by(Order.executed_at.asc()).all()


# Singleton instance
snapshot_service = SnapshotService()
