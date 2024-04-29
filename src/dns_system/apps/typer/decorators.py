import asyncio
from functools import wraps

from dns_system.apps.domains.selectors import dns_log


def log_dns_actions(func):
    """
    Decorator for logging DNS actions
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        task = kwargs.get("task")
        queue_id = kwargs.get("queue_id")
        obj = await func(self, *args, **kwargs)
        response_text = await obj.text()

        create_data: dict = {
            "task": task,
            "response": response_text,
            "response_http_code": obj.status,
            "queue_id": queue_id
        }
        await dns_log.create(data=create_data)

        return obj

    return wrapper


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
