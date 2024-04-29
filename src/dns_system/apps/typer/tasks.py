from dns_system.apps.typer import services
from dns_system.apps.typer.base import manager
from dns_system.apps.domains import selectors as domain_selectors
from dns_system.apps.commons.constants import CREATE_ZONE, CLOUDFLARE_API, SYNC_DNS_RECORD, DELETE_ZONE


async def create_zone(search_query: str, queue_id: int):
    # Get zone with domain name
    zone = await services.get_zone(domain_name=search_query, task=CREATE_ZONE, queue_id=queue_id)
    # if zones not null
    if zone.get("result"):
        # Getting zone
        parsed_zone = zone.get("result")[0]
    else:
        # Or creating new zone
        zone = await services.create_zone(
            domain_name=search_query,
            task=CREATE_ZONE,
            queue_id=queue_id
        )
        parsed_zone = zone.get("result")

    zone_id = parsed_zone.get("id")

    domain = await domain_selectors.domain.get(name=search_query)
    # Getting domain records
    domain_records = await domain_selectors.domain_records.list(domain_id=domain.id)
    # If new zone has domain records in DB
    if domain_records:
        await services.sync_dns_records(zone_id=zone_id, domain_records=domain_records, domain_name=search_query,
                                        task=CREATE_ZONE, queue_id=queue_id)


async def delete_zone(search_query: str, queue_id: int):

    # Get zone with domain name
    zone_response = await manager.get(
        CLOUDFLARE_API,
        search_query={"name": search_query},
        task=DELETE_ZONE,
        queue_id=queue_id
    )
    zone = await zone_response.json()

    # If zone in Cloudflare
    if zone.get("result"):
        zone_id = zone.get("result")[0].get("id")
        # Deleting zone
        await manager.delete(CLOUDFLARE_API, identifier=zone_id, task=DELETE_ZONE, queue_id=queue_id)

    # Deleting zone and domain records in DB
    domain = await domain_selectors.domain.get(name=search_query)
    await domain_selectors.domain.delete_obj({"domain_name": search_query}, *["domain_name"])
    await domain_selectors.domain_records.delete_obj({"domain_id": domain.id}, *["domain_id"])


async def sync_dns_records(search_query: str, queue_id: int):

    # Get zone with zone name
    zone = await services.get_zone(domain_name=search_query, task=SYNC_DNS_RECORD, queue_id=queue_id)
    # If not zone
    if not zone.get("result"):
        # Creating new zone
        await services.create_zone(domain_name=search_query, task=SYNC_DNS_RECORD, queue_id=queue_id)
    else:
        parsed_zone = zone.get("result")[0]
        zone_id = parsed_zone.get("id")

        # Getting domain in DB
        domain = await domain_selectors.domain.get(name=search_query)
        if domain:
            # If domain in DB
            domain_records = await domain_selectors.domain_records.list(domain_id=domain.id)
            if domain_records:
                # Syncing all of Domain Records
                await services.sync_dns_records(
                    zone_id=zone_id,
                    domain_records=domain_records,
                    domain_name=search_query,
                    task=SYNC_DNS_RECORD,
                    queue_id=queue_id
                )
        else:
            await manager.delete(CLOUDFLARE_API, zone_id, task=SYNC_DNS_RECORD, queue_id=queue_id)

        # Get DNS Records with zone_id
        dns_records = await services.get_dns_records(zone_id=zone_id, task=SYNC_DNS_RECORD, queue_id=queue_id)
        cloudflare_dns_records = dns_records.get("result")

        # If we get zones DNS Records
        if cloudflare_dns_records:

            # Sync records if their in DB, or delete from cloudflare
            for dns_record in cloudflare_dns_records:
                cloudflare_dns_record_id = dns_record.get("id")
                await services.delete_not_existing_dns_record(
                    cloudflare_dns_record_id=cloudflare_dns_record_id,
                    zone_id=zone_id,
                    task=SYNC_DNS_RECORD,
                    queue_id=queue_id
                )
