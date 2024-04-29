import asyncio

import pytest

from dns_system.apps.typer.services import get_payload


@pytest.fixture()
def get_test_payload():
    return get_payload("testmanager.com")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

