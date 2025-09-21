#!/usr/bin/env python3
"""Test harness for bridge validation."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx


async def run_golden_tests() -> None:
    golden_dir = Path("tests/golden/mcp_to_aip")

    results = []
    async with httpx.AsyncClient(base_url="http://localhost:8090") as client:
        for test_file in golden_dir.glob("*.json"):
            with open(test_file, "r", encoding="utf-8") as f:
                test = json.load(f)

            response = await client.post("/mcp", json=test["input"])
            actual = response.json()

            expected = test["expected"]
            match = compare_messages(actual, expected)

            results.append(
                {
                    "test": test_file.name,
                    "passed": match,
                    "actual": actual if not match else None,
                }
            )

    passed = sum(1 for r in results if r["passed"])
    print(f"Golden Tests: {passed}/{len(results)} passed")

    for r in results:
        if not r["passed"]:
            print(f"  ❌ {r['test']}")
            print(f"     Actual: {json.dumps(r['actual'], indent=2)}")


def compare_messages(actual: dict, expected: dict) -> bool:
    for field in ["msg_id", "ts", "thread_id"]:
        actual.pop(field, None)
        expected.pop(field, None)

    if "trust" in expected and "signature" in expected["trust"]:
        if expected["trust"]["signature"] == "_COMPUTED_":
            if "trust" not in actual or "signature" not in actual["trust"]:
                return False
            expected["trust"]["signature"] = actual["trust"]["signature"]

    return actual == expected


if __name__ == "__main__":
    asyncio.run(run_golden_tests())
