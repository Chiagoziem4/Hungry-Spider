from __future__ import annotations

import asyncio
import random
import time


async def human_delay(min_sec: float = 0.5, max_sec: float = 2.0) -> None:
    await asyncio.sleep(random.uniform(min_sec, max_sec))



def sync_human_delay(min_sec: float = 0.5, max_sec: float = 2.0) -> None:
    time.sleep(random.uniform(min_sec, max_sec))



def compute_delay(base_delay: float, randomise: bool = True) -> float:
    if not randomise:
        return max(base_delay, 0.0)
    jitter = random.uniform(0.1, 0.8)
    return max(base_delay + jitter, 0.0)


async def simulate_scroll(page, scrolls: int = 3) -> None:
    viewport_height = await page.evaluate("window.innerHeight")
    for _ in range(scrolls):
        await page.mouse.wheel(0, random.randint(max(200, viewport_height // 3), viewport_height))
        await human_delay(0.4, 1.2)
    if random.random() < 0.3:
        await page.mouse.wheel(0, -random.randint(200, 500))
        await human_delay(0.2, 0.6)


async def simulate_mouse_move(page) -> None:
    await page.mouse.move(random.randint(120, 1200), random.randint(120, 800))
    await human_delay(0.1, 0.4)
