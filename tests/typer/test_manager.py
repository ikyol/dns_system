import pytest

from tests.conftest import get_test_payload # noqa
from dns_system.apps.typer.base import manager
from dns_system.apps.commons.constants import CLOUDFLARE_API


@pytest.fixture()
async def post_fixture(get_test_payload):
    """
    Creating zone in Cloudflare
    """
    zone = await manager.post(
        payload=get_test_payload,
        url=CLOUDFLARE_API,
    )
    status_code, response = zone.status, await zone.json()
    return status_code, response


@pytest.mark.parametrize("post_fixture", [post_fixture], indirect=True)
async def test_get(post_fixture):
    """
    Test for getting zone in Cloudflare
    """
    status, fixture = post_fixture
    zone_name = fixture.get("result").get("name")
    get_zone = await manager.get(
        url=CLOUDFLARE_API,
        search_query=zone_name
    )
    assert get_zone.status == 200

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=fixture.get("result").get("id")
    )


@pytest.mark.parametrize("post_fixture", [post_fixture], indirect=True)
async def test_post(post_fixture):
    """
    Test for creating zone in Cloudflare
    """
    status, fixture = post_fixture
    assert status == 200

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=fixture.get("result").get("id")
    )


@pytest.mark.parametrize("post_fixture", [post_fixture], indirect=True)
async def test_delete(post_fixture):
    """
    Test for deleting zone in Cloudflare
    """
    status, fixture = post_fixture

    deleted_zone = await manager.delete(
        url=CLOUDFLARE_API,
        identifier=fixture.get("result").get("id")
    )
    assert deleted_zone.status == 200
