import json
from typing import Optional, Any
from redis import Redis

AUDIT_QUEUE_KEY = "audit_queue"

redis_client = Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True
)


def enqueue_audit(job: Any) -> None:
    """
    Push a new audit job onto the queue.
    """
    payload = json.dumps(job)
    redis_client.rpush(AUDIT_QUEUE_KEY, payload)


def dequeue_audit(block: bool = False, timeout: int = 0) -> Optional[Any]:
    """
    Dequeue one audit job from Redis.

    Args:
        block: If True, wait for a job using BLPOP
        timeout: Seconds to wait (only applies if block=True)

    Returns:
        Parsed job or None
    """
    if block:
        result = redis_client.blpop(AUDIT_QUEUE_KEY, timeout=timeout)
        if result is None:
            return None
        _, payload = result
    else:
        payload = redis_client.lpop(AUDIT_QUEUE_KEY)
        if payload is None:
            return None

    try:
        return json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return payload