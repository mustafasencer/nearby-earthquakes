import asyncio
import json
from typing import Any, Dict

import pytest


@pytest.fixture
async def mock_response(monkeypatch):
    async def mock_fn() -> Dict[str, Any]:
        with open("test_data/test_response.json") as f:
            response = json.load(f)
        return response

    monkeypatch.setattr("main.fetch_earthquakes", mock_fn)


# @pytest.fixture(scope="session")
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()
