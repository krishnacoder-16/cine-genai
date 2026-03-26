import asyncio
import json
from typing import AsyncGenerator


# In-memory store: job_id -> asyncio.Queue
_queues: dict[str, asyncio.Queue] = {}


def create_job(job_id: str) -> asyncio.Queue:
    """Create a new progress queue for a job."""
    q = asyncio.Queue()
    _queues[job_id] = q
    return q


def get_queue(job_id: str) -> asyncio.Queue | None:
    return _queues.get(job_id)


def remove_job(job_id: str):
    _queues.pop(job_id, None)


async def send_event(job_id: str, event_type: str, data: dict):
    """Push an SSE event onto the job's queue."""
    q = _queues.get(job_id)
    if q:
        await q.put({"event": event_type, "data": data})


async def event_stream(job_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted strings.
    The FastAPI endpoint iterates this and streams it to the client.
    """
    q = _queues.get(job_id)
    if not q:
        yield _format_event("error", {"message": "Job not found"})
        return

    while True:
        try:
            # Wait up to 30 s for the next event before sending a keepalive
            item = await asyncio.wait_for(q.get(), timeout=30)
        except asyncio.TimeoutError:
            yield ": keepalive\n\n"
            continue

        yield _format_event(item["event"], item["data"])

        # Sentinel: generation finished or errored — close the stream
        if item["event"] in ("complete", "error"):
            remove_job(job_id)
            break


def _format_event(event_type: str, data: dict) -> str:
    """Format a dict as an SSE message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
