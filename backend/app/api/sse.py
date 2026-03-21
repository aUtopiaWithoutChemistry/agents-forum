"""Server-Sent Events for real-time updates"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

from app.services.market import market_service
from app.services.forum_events import forum_event_manager

router = APIRouter(prefix="/api", tags=["sse"])


async def market_event_generator(tickers: list, interval: float = 5.0):
    """Generator that yields market data updates every interval seconds"""
    while True:
        for ticker in tickers:
            try:
                quote = market_service.get_quote(ticker)
                if quote:
                    yield f"data: {json.dumps(quote, default=str)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'ticker': ticker})}\n\n"

        await asyncio.sleep(interval)


@router.get("/sse/market/{tickers}")
async def stream_market_data(tickers: str, interval: float = 5.0):
    """
    Stream real-time market data for comma-separated tickers.
    Example: GET /api/sse/market/AAPL,GOOGL,MSFT

    Returns SSE stream with market data updates every `interval` seconds.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    return StreamingResponse(
        market_event_generator(ticker_list, interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/sse/ping")
async def sse_ping():
    """Simple ping endpoint to keep connection alive"""
    async def ping_generator():
        while True:
            yield f"data: {json.dumps({'ping': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        ping_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/events/forum")
async def stream_forum_events():
    """
    Stream real-time forum events via Server-Sent Events.
    Events broadcast: new_post, new_comment, new_reaction, post_deleted

    Clients receive notifications for new posts, comments, reactions, and post deletions.
    A keepalive ping is sent every 30 seconds to keep the connection alive.
    """
    queue = forum_event_manager.connect()
    try:
        return StreamingResponse(
            forum_event_manager.generate_sse(queue),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    finally:
        forum_event_manager.disconnect(queue)
