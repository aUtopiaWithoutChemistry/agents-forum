"""Background job scheduler for NAV snapshots at US market close (4:05 PM ET)"""
import logging
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.services.snapshots import snapshot_service
from app.services.market_refresh import run_market_refresh_job, run_initial_market_seed

logger = logging.getLogger(__name__)

# US Eastern Time timezone
US_EAST = timezone("America/New_York")


def is_weekday():
    """Check if today is a weekday (Monday=0, Sunday=6)"""
    return date.today().weekday() < 5


def run_nav_snapshot_job():
    """Job to store NAV snapshots at US market close."""
    if not is_weekday():
        logger.info("Skipping NAV snapshot - not a weekday")
        return

    try:
        logger.info("Running scheduled NAV snapshot job...")
        result = snapshot_service.store_nav_snapshots()
        logger.info(f"NAV snapshot job completed: stored={result.get('stored')}, skipped={result.get('skipped')}")
    except Exception as e:
        logger.error(f"NAV snapshot job failed: {e}")


def run_position_snapshot_job():
    """Job to store position snapshots at US market close."""
    if not is_weekday():
        logger.info("Skipping position snapshot - not a weekday")
        return

    try:
        logger.info("Running scheduled position snapshot job...")
        result = snapshot_service.store_position_snapshots()
        logger.info(f"Position snapshot job completed: stored={result.get('stored')}, skipped={result.get('skipped')}")
    except Exception as e:
        logger.error(f"Position snapshot job failed: {e}")


def start_scheduler():
    """Start the background scheduler for market close snapshots."""
    scheduler = BackgroundScheduler(timezone=US_EAST)

    # Run at 4:05 PM ET on weekdays (US market close)
    # Markets close at 4:00 PM ET, we wait 5 minutes for final prices
    scheduler.add_job(
        run_nav_snapshot_job,
        CronTrigger(hour=16, minute=5, day_of_week="mon-fri", timezone=US_EAST),
        id="nav_snapshot_job",
        name="NAV Snapshot at Market Close",
        replace_existing=True,
    )

    # Also run position snapshots at the same time
    scheduler.add_job(
        run_position_snapshot_job,
        CronTrigger(hour=16, minute=5, day_of_week="mon-fri", timezone=US_EAST),
        id="position_snapshot_job",
        name="Position Snapshot at Market Close",
        replace_existing=True,
    )

    # Market data refresh every 15 minutes during the day
    # This keeps DB warm so user-facing requests are fast
    scheduler.add_job(
        run_market_refresh_job,
        CronTrigger(minute="*/15", timezone=US_EAST),
        id="market_refresh_job",
        name="Market Data Refresh (every 15 min)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Background scheduler started - NAV/Position snapshots at 4:05 PM ET on weekdays, Market refresh every 15 min")

    return scheduler


def seed_market_data_on_startup():
    """Called on app startup to seed market data."""
    logger.info("Starting initial market data seed on app startup...")
    try:
        result = run_initial_market_seed()
        logger.info(f"Initial market data seed completed: {result}")
    except Exception as e:
        logger.error(f"Initial market data seed failed: {e}")
