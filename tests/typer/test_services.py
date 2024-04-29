import pytest

from dns_system.apps.typer import services
from dns_system.apps.db.session import driver
from dns_system.apps.domains import selectors
from dns_system.apps.typer.base import manager
from dns_system.apps.commons.constants import CLOUDFLARE_API
from tests.domains.test_domains_selectors import domain_create
from dns_system.apps.domains import services as domain_services
from dns_system.apps.db.models.domain_models import DomainRecords, Domains


@pytest.mark.asyncio
@pytest.mark.parametrize("domain_name", [("test.com")])
async def test_create_zone(domain_name: str):
    """
    Test for creating zones in Cloudflare with domains in DB
    """
    async with driver.session() as db:
        domain = Domains(domain_name=domain_name, created_at=123123123)
        db.add(domain)
        await db.commit()

    zone = await services.create_zone(domain_name=domain_name)
    zone_id = zone.get("result").get("id")
    zone_name = zone.get("result").get("name")

    assert zone_name == domain.domain_name

    await manager.delete(url=CLOUDFLARE_API, identifier=zone_id)

    async with driver.session() as db:
        await db.delete(domain)
        await db.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain_create", [domain_create], indirect=True)
async def test_create_dns_record(domain_create):
    """
    Test for creating DNS records in Cloudflare with data in DB
    """
    async with driver.session() as db:
        dns_record = DomainRecords(
            domain_id=domain_create.id,
            record_type="A",
            record_content="198.51.100.4",
            record_proxied=1,
            record_ttl=1
        )
        db.add(dns_record)
        await db.commit()

    zone = await services.create_zone(domain_name=domain_create.domain_name)

    zone_id = zone.get("result").get("id")
    zone_name = zone.get("result").get("name")

    cloudflare_dns_record = await services.create_dns_record(
        content=dns_record.record_content,
        proxied=dns_record.record_proxied,
        domain_name=zone_name,
        type_=dns_record.record_type,
        ttl=dns_record.record_ttl,
        zone_id=zone_id
    )
    cloudflare_dns_record_id = cloudflare_dns_record.get("result").get("id")
    await domain_services.update_dns_record(
        dns_record_id=dns_record.id,
        cloudflare_dns_record_id=cloudflare_dns_record_id
    )
    domain_record = await selectors.domain_records.get(cloudflare_id=cloudflare_dns_record_id)

    assert domain_record.cloudflare_dns_record_id == cloudflare_dns_record_id

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=zone_id,
        dns_identifier=cloudflare_dns_record_id,
        dns_records=True
    )

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=zone_id
    )

    async with driver.session() as db:
        await db.delete(dns_record)
        await db.delete(domain_create)
        await db.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain_name", [("test.com")])
async def test_delete_not_existing_dns_records(domain_name):
    async with driver.session() as db:
        domain = Domains(domain_name=domain_name, created_at=123123123)
        db.add(domain)
        await db.commit()

    zone = await services.create_zone(domain_name=domain.domain_name)
    zone_id = zone.get("result").get("id")

    payload: dict = {
        "content": "198.51.100.4",
        "proxied": True,
        "name": domain_name,
        "type": "A",
        "ttl": 1
    }
    created_dns_record = await manager.post(
        payload=payload,
        url=CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_records=True
    )
    parsed_dns_record = await created_dns_record.json()
    dns_record_id = parsed_dns_record.get("result").get("id")

    await services.delete_not_existing_dns_record(cloudflare_dns_record_id=dns_record_id, zone_id=zone_id)

    cloudflare_dns_record = await manager.get(
        url=CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_identifier=dns_record_id,
        dns_records=True,
        detail=True
    )
    parsed_cloudflare_dns_record = await cloudflare_dns_record.json()
    assert parsed_cloudflare_dns_record.get("result") == None

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=zone_id
    )

    async with driver.session() as db:
        await db.delete(domain)
        await db.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain_name", [("test.com")])
async def test_update_dns_record(domain_name):
    async with driver.session() as db:
        domain = Domains(domain_name=domain_name, created_at=123123123)
        db.add(domain)
        await db.flush()

        domain_record = DomainRecords(
            domain_id=domain.id,
            record_type="A",
            record_content="198.51.100.4",
            record_proxied=1,
            record_ttl=1
        )
        db.add(domain_record)
        await db.commit()

    zone = await services.create_zone(domain_name=domain.domain_name)
    zone_id = zone.get("result").get("id")

    payload: dict = {
        "content": domain_record.record_content,
        "proxied": bool(domain_record.record_proxied),
        "name": domain_name,
        "type": domain_record.record_type,
        "ttl": domain_record.record_ttl
    }
    created_dns_record = await manager.post(
        payload=payload,
        url=CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_records=True
    )
    parsed_dns_record = await created_dns_record.json()
    dns_record_id = parsed_dns_record.get("result").get("id")
    await services.update_dns_record(
        content="204.51.100.4",
        proxied=False,
        type_="A",
        ttl=3600,
        dns_record_id=dns_record_id,
        zone_id=zone_id
    )

    updated_dns_record = await services.get_dns_record_by_id(zone_id=zone_id, dns_id=dns_record_id)
    dns_record = updated_dns_record.get("result")
    assert domain_record.record_ttl != dns_record.get("ttl")
    assert domain_record.record_content != dns_record.get("content")
    assert domain_record.record_proxied != dns_record.get("proxied")

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=zone_id,
        dns_identifier=dns_record_id,
        dns_records=True
    )

    await manager.delete(
        url=CLOUDFLARE_API,
        identifier=zone_id
    )

    async with driver.session() as db:
        await db.delete(domain_record)
        await db.delete(domain)
        await db.commit()
