#!/usr/bin/env python3
"""Simple load testing harness for the bridge."""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from typing import Any, Dict

import httpx


async def send_request(client: httpx.AsyncClient, payload: Dict[str, Any]) -> None:
    await client.post("/mcp", json=payload)


async def run_load_test(rate: int, duration: int) -> None:
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/http/fetch",
        "params": {"url": "https://example.com", "response": {"status": 200}},
        "id": "load-test",
    }
    interval = 1 / rate if rate > 0 else 0

    async with httpx.AsyncClient(base_url="http://localhost:8090") as client:
        start = time.time()
        sent = 0
        while time.time() - start < duration:
            await send_request(client, {**payload, "id": f"load-{sent}"})
            sent += 1
            await asyncio.sleep(interval)
        print(json.dumps({"sent": sent, "duration": duration}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Bridge load testing tool")
    parser.add_argument("--rate", type=int, default=100, help="Requests per second")
    parser.add_argument("--duration", type=int, default=60, help="Test duration seconds")
    args = parser.parse_args()

    asyncio.run(run_load_test(args.rate, args.duration))


if __name__ == "__main__":
    main()
