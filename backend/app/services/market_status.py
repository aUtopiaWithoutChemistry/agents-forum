"""Market Status Service - US, HK, JP, EU market hours"""
from datetime import datetime, time
import pytz
from typing import Dict

MARKETS = {
    "US": {
        "name": "US",
        "open_hour": 9,
        "open_minute": 30,
        "close_hour": 16,
        "close_minute": 0,
        "tz": "America/New_York",
    },
    "HK": {
        "name": "Hong Kong",
        "open_hour": 9,
        "open_minute": 30,
        "close_hour": 16,
        "close_minute": 0,
        "tz": "Asia/Hong_Kong",
    },
    "JP": {
        "name": "Japan",
        "open_hour": 9,
        "open_minute": 0,
        "close_hour": 15,
        "close_minute": 0,
        "tz": "Asia/Tokyo",
    },
    "EU": {
        "name": "Europe",
        "open_hour": 8,
        "open_minute": 0,
        "close_hour": 16,
        "close_minute": 30,
        "tz": "Europe/Berlin",
    },
}


def get_market_status(market_code: str) -> dict:
    """Return status for a market: open, closed, weekend, pre_open, after_hours"""
    if market_code not in MARKETS:
        return {"error": f"Unknown market: {market_code}"}

    market = MARKETS[market_code]
    tz = pytz.timezone(market["tz"])

    # Get current time in market's timezone
    now = datetime.now(pytz.UTC).astimezone(tz)
    current_time = now.time()

    # Check if it's weekend (Saturday or Sunday in market's timezone)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return {
            "status": "weekend",
            "current_time": current_time.strftime("%H:%M %Z"),
            "next_open": f"{market['open_hour']:02d}:{market['open_minute']:02d} {market['tz'].split('/')[-1]}",
        }

    # Define open and close times
    open_time = time(market["open_hour"], market["open_minute"])
    close_time = time(market["close_hour"], market["close_minute"])

    # Determine status
    if current_time < open_time:
        status = "pre_open"
        next_change = f"{market['open_hour']:02d}:{market['open_minute']:02d} {market['tz'].split('/')[-1]}"
    elif current_time >= open_time and current_time < close_time:
        status = "open"
        next_change = f"{market['close_hour']:02d}:{market['close_minute']:02d} {market['tz'].split('/')[-1]}"
    else:
        status = "after_hours"
        # Next open is tomorrow (or Monday if Sunday)
        next_open_hour = market['open_hour']
        next_open_minute = market['open_minute']
        next_change = f"{next_open_hour:02d}:{next_open_minute:02d} {market['tz'].split('/')[-1]}"

    result = {
        "status": status,
        "current_time": current_time.strftime("%H:%M %Z"),
    }

    if status == "open":
        result["closes_at"] = next_change
    elif status == "after_hours":
        result["next_open"] = next_change
    elif status == "pre_open":
        result["opens_at"] = next_change

    return result


def is_market_open(market_code: str = "US") -> bool:
    """Check if a specific market is currently open.

    Args:
        market_code: Market code (US, HK, JP, EU)

    Returns:
        True if market is currently open for trading
    """
    status = get_market_status(market_code)
    return status.get("status") == "open"


def get_all_market_statuses() -> dict:
    """Get status for all markets"""
    markets = {}
    global_refresh_needed = False
    next_change = None
    next_change_time = None

    for code in MARKETS:
        status_info = get_market_status(code)
        markets[code] = status_info

        # Track next change time
        if status_info["status"] not in ["weekend"]:
            if "closes_at" in status_info:
                change_str = status_info["closes_at"]
            elif "opens_at" in status_info:
                change_str = status_info["opens_at"]
            elif "next_open" in status_info:
                change_str = status_info["next_open"]
            else:
                change_str = None

            if change_str:
                # For simplicity, use the change string as-is
                if next_change is None or status_info["status"] == "open":
                    next_change = change_str
                    if status_info["status"] == "open":
                        global_refresh_needed = True

    return {
        "timestamp": datetime.now(pytz.UTC).isoformat(),
        "markets": markets,
        "global_refresh_needed": global_refresh_needed,
        "next_change": next_change,
    }
