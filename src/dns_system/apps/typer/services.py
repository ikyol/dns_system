from typing import Any, Dict, Optional, List

from dns_system.apps.typer.base import manager
from dns_system.config.settings import settings
from dns_system.apps.db.models.domain_models import DomainRecords
from dns_system.apps.domains import selectors as domain_selectors, services


def get_dns_record_payload(
    *,
    content: str,
    proxied: int,
    type_: str,
    ttl: int,
    domain_name: Optional[str] = None
) -> Dict[str, Any]:
    payload: dict = {
        "content": content,
        "proxied": bool(proxied),
        "type": type_,
        "ttl": ttl
    }
    if domain_name:
        payload["name"] = domain_name
    return payload


def get_payload(domain_name: str) -> Dict[str, Any]:
    payload: dict = {"account": {
        "id": settings.CLOUDFLARE_ACCOUNT_ID
    },
        "name": domain_name, "type": "full"}
    return payload


async def create_zone(domain_name: str, **kwargs) -> Dict[str, Any]:
    payload: dict = get_payload(domain_name=domain_name)
    zone_response = await manager.post(
        payload=payload,
        url=settings.CLOUDFLARE_API,
        **kwargs
    )
    zone = await zone_response.json()

    if zone_response.status == 200:
        cloudflare_domain_id = zone.get("result").get("id")

        await services.update_domain(domain_name=domain_name, cloudflare_domain_id=cloudflare_domain_id)
    return zone


async def create_dns_record(
    *,
    content: str,
    proxied: int,
    domain_name: str,
    type_: str,
    ttl: int,
    zone_id: str,
    **kwargs
) -> Dict[str, Any]:

    payload: dict = get_dns_record_payload(
        content=content,
        proxied=proxied,
        type_=type_,
        ttl=ttl,
        domain_name=domain_name
    )
    dns_record = await manager.post(
        payload=payload,
        url=settings.CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_records=True,
        **kwargs
    )
    return await dns_record.json()


async def get_zone(*, domain_name: str, **kwargs) -> Dict[str, Any]:
    zone = await manager.get(
        url=settings.CLOUDFLARE_API,
        search_query={"name": domain_name},
        **kwargs
    )
    return await zone.json()


async def get_zones(**kwargs) -> Dict[str, Any]:
    zone = await manager.get(
        url=settings.CLOUDFLARE_API,
        **kwargs
    )
    return await zone.json()


async def get_zone_by_id(zone_id: str, **kwargs) -> Dict[str, Any]:
    zone = await manager.get(
        url=settings.CLOUDFLARE_API,
        zone_identifier=zone_id,
        **kwargs
    )
    return await zone.json()


async def get_dns_records(*, zone_id: str, **kwargs) -> Dict[str, Any]:
    dns_records = await manager.get(
        url=settings.CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_records=True,
        **kwargs
    )
    return await dns_records.json()


async def get_dns_record_by_id(*, zone_id: str, dns_id: str, **kwargs) -> Dict[str, Any]:
    dns_records = await manager.get(
        url=settings.CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_identifier=dns_id,
        dns_records=True,
        detail=True,
        **kwargs
    )
    return await dns_records.json()


async def update_dns_record(
    *,
    content: str,
    proxied: int,
    type_: str,
    ttl: int,
    dns_record_id: str,
    zone_id: str,
    **kwargs
) -> None:
    payload: dict = get_dns_record_payload(content=content, proxied=proxied, type_=type_, ttl=ttl)
    await manager.patch(
        payload=payload,
        url=settings.CLOUDFLARE_API,
        zone_identifier=zone_id,
        dns_identifier=dns_record_id,
        dns_records=True,
        **kwargs
    )


async def delete_not_existing_dns_record(*, cloudflare_dns_record_id: str, zone_id: str, **kwargs) -> None:
    domain_record = await domain_selectors.domain_records.get(cloudflare_id=cloudflare_dns_record_id)
    if not domain_record:
        await manager.delete(
            url=settings.CLOUDFLARE_API,
            identifier=zone_id,
            dns_identifier=cloudflare_dns_record_id,
            dns_records=True,
            **kwargs
        )


async def sync_dns_records(zone_id: str, domain_records: List[DomainRecords], domain_name: str, **kwargs):
    cloudflare_domain_records = await get_dns_records(zone_id=zone_id, **kwargs)
    parsed_cloudflare_domain_records = cloudflare_domain_records.get("result")

    for dns_record in parsed_cloudflare_domain_records:
        cloudflare_dns_record_id = dns_record.get("id")
        await delete_not_existing_dns_record(
            cloudflare_dns_record_id=cloudflare_dns_record_id,
            zone_id=zone_id,
            **kwargs
        )

    for domain_record in domain_records:
        if not domain_record.cloudflare_dns_record_id:
            created_dns_response = await create_dns_record(
                content=domain_record.record_content,
                proxied=domain_record.record_proxied,
                domain_name=domain_name,
                type_=domain_record.record_type,
                ttl=domain_record.record_ttl,
                zone_id=zone_id,
                **kwargs
            )
            cloudflare_dns_record_id = created_dns_response.get("result").get("id")

            await services.update_dns_record(
                dns_record_id=domain_record.id,
                cloudflare_dns_record_id=cloudflare_dns_record_id
            )

        elif domain_record.cloudflare_dns_record_id:
            cloudflare_dns_record_response = await get_dns_record_by_id(
                zone_id=zone_id,
                dns_id=domain_record.cloudflare_dns_record_id,
                **kwargs
            )

            cloudflare_dns_record = cloudflare_dns_record_response.get("result")
            if cloudflare_dns_record:

                if not (
                    domain_record.record_ttl == cloudflare_dns_record.get("ttl") and
                    domain_record.record_type == cloudflare_dns_record.get("type") and
                    domain_record.record_content == cloudflare_dns_record.get("content") and
                    domain_record.record_proxied == cloudflare_dns_record.get("proxied")
                ):
                    # If not we sync
                    await update_dns_record(
                        content=domain_record.record_content,
                        proxied=domain_record.record_proxied,
                        type_=domain_record.record_type,
                        ttl=domain_record.record_ttl,
                        dns_record_id=domain_record.cloudflare_dns_record_id,
                        zone_id=zone_id,
                        **kwargs
                    )
