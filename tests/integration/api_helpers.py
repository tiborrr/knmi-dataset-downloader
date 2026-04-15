from __future__ import annotations

import unittest
from collections.abc import Awaitable, Callable, Coroutine

from kiota_abstractions.api_error import APIError

_RATE_LIMIT_SKIP_MSG = (
    "KNMI open-data API returned HTTP 429 (rate limited). "
    "Wait about one hour before re-running integration tests."
)

type RunKnmiApiCall[T] = Callable[
    [Callable[[], Awaitable[T]]],
    Coroutine[None, None, T],
]


async def run_or_skip_on_429[T](coro_factory: Callable[[], Awaitable[T]]) -> T:
    """Run *coro_factory*; on HTTP 429 skip the test (KNMI cooldown ~1 hour)."""
    try:
        return await coro_factory()
    except APIError as exc:
        if exc.response_status_code == 429:
            raise unittest.SkipTest(_RATE_LIMIT_SKIP_MSG) from exc
        raise
