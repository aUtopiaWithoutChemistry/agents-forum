"""Forum SSE event manager for broadcasting real-time events to connected clients."""
import asyncio
import json
from typing import Dict, List
from fastapi.responses import StreamingResponse


class ForumEventManager:
    """Manages SSE connections for forum events."""

    def __init__(self):
        self._connections: List[asyncio.Queue] = []

    def connect(self) -> asyncio.Queue:
        """Register a new SSE connection and return its event queue."""
        queue = asyncio.Queue(maxsize=100)
        self._connections.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue):
        """Remove an SSE connection."""
        if queue in self._connections:
            self._connections.remove(queue)

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients."""
        event = json.dumps({"type": event_type, "data": data}, default=str)
        message = f"data: {event}\n\n"

        # Remove disconnected queues
        disconnected = []
        for queue in self._connections:
            try:
                await asyncio.wait_for(queue.put(message), timeout=1.0)
            except asyncio.TimeoutError:
                disconnected.append(queue)
            except Exception:
                disconnected.append(queue)

        for q in disconnected:
            self.disconnect(q)

    async def generate_sse(self, queue: asyncio.Queue):
        """Generate SSE stream from a queue, with keepalive pings."""
        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except asyncio.CancelledError:
            pass


# Global singleton
forum_event_manager = ForumEventManager()


async def broadcast_forum_event(event_type: str, data: dict):
    """Helper to broadcast a forum event."""
    await forum_event_manager.broadcast(event_type, data)
