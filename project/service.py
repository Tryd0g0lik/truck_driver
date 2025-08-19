import asyncio
from typing import Any
from collections.abc import Callable


async def sync_for_async(fn: Callable[[Any], Any], *args, **kwargs):
    # return await asyncio.create_task(asyncio.to_thread(fn, *args, **kwargs))
    return await asyncio.to_thread(fn, *args, **kwargs)
