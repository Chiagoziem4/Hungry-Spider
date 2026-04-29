from __future__ import annotations

import heapq
from itertools import count


class QueueManager:
    """Priority queue with URL de-duplication for crawl scheduling."""

    def __init__(self):
        self._queue: list[tuple[int, int, str, int]] = []
        self._counter = count()
        self._seen: set[str] = set()

    def add(self, url: str, *, depth: int, priority: int = 100) -> bool:
        if url in self._seen:
            return False
        self._seen.add(url)
        heapq.heappush(self._queue, (priority, next(self._counter), url, depth))
        return True

    def pop(self) -> tuple[str, int]:
        _, _, url, depth = heapq.heappop(self._queue)
        return url, depth

    def __bool__(self) -> bool:
        return bool(self._queue)

    def __len__(self) -> int:
        return len(self._queue)
