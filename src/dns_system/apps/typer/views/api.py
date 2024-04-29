import asyncio

import typer

from dns_system.apps.typer import services
from dns_system.apps.typer.base import manager
from dns_system.apps.typer.mappers import TASK
from dns_system.apps.typer.decorators import coro
from dns_system.apps.domains import selectors as domain_selectors
from dns_system.apps.domains import services as domain_services
from dns_system.apps.domains.constants import DomainDNSQueueStatus
from dns_system.apps.commons.constants import CLOUDFLARE_API, SYNC_DNS_RECORD

app = typer.Typer()


@app.command()
@coro
async def process_domain_queue():
    while True:
        queue = await domain_selectors.queue.get(status=DomainDNSQueueStatus.PENDING.value)

        if queue:
            # Set queue status IN PROGRESS
            await domain_selectors.queue.update_fields(
                {"id": queue.id},
                {"status": DomainDNSQueueStatus.IN_PROGRESS.value},
                *["id"]
            )

            # Getting queue task
            task = TASK.get(queue.task)

            domain_name = queue.domain.domain_name
            await task(search_query=domain_name, queue_id=queue.id)

        else:
            try:
                await asyncio.sleep(5)
            except KeyboardInterrupt:
                pass


@app.command()
@coro
async def domain_sync():
    # Getting all zones
    zones = await services.get_zones(task=SYNC_DNS_RECORD)
    if zones.get("result"):
        parsed_zones = zones.get("result")

        for zone in parsed_zones:
            if zone:
                # Getting zone name and id
                zone_name = zone.get("name")
                zone_id = zone.get("id")

                # Getting domain in DB with zone name
                domain = await domain_selectors.domain.get(name=zone_name)
                if domain:

                    # If we have domain in DB
                    domain_records = await domain_selectors.domain_records.list(domain_id=domain.id)
                    # Syncing records
                    await services.sync_dns_records(
                        zone_id=zone_id,
                        domain_records=domain_records,
                        domain_name=zone_name,
                        task=SYNC_DNS_RECORD
                    )
                else:
                    # Or delete zone
                    await manager.delete(CLOUDFLARE_API, zone_id, task=SYNC_DNS_RECORD)

                # Trying to get Cloudflare Domain Records
                dns_record_response = await manager.get(
                    url=CLOUDFLARE_API,
                    zone_identifier=zone_id,
                    dns_records=True,
                    task=SYNC_DNS_RECORD
                )
                dns_records = await dns_record_response.json()
                cloudflare_dns_records = dns_records.get("result")

                # If we get Cloudflare Domain Records
                if cloudflare_dns_records:
                    # Sync records if their in DB, or delete from cloudflare
                    for dns_record in cloudflare_dns_records:
                        cloudflare_dns_record_id = dns_record.get("id")
                        await services.delete_not_existing_dns_record(
                            cloudflare_dns_record_id=cloudflare_dns_record_id,
                            zone_id=zone_id,
                            task=SYNC_DNS_RECORD
                        )

    domains = await domain_selectors.domain.list()
    for domain in domains:
        zone = await services.create_zone(domain_name=domain.domain_name, task=SYNC_DNS_RECORD)
        parsed_zone = zone.get("result")
        if parsed_zone:
            zone_id = parsed_zone.get("id")
            dns_records = await domain_selectors.domain_records.list(domain_id=domain.id)
            if dns_records:
                for domain_record in dns_records:

                    cloudflare_dns_record = await services.create_dns_record(
                        content=domain_record.record_content,
                        proxied=domain_record.record_proxied,
                        domain_name=domain.domain_name,
                        type_=domain_record.record_type,
                        ttl=domain_record.record_ttl,
                        zone_id=zone_id,
                        task=SYNC_DNS_RECORD
                    )
                    cloudflare_dns_record_id = cloudflare_dns_record.get("result").get("id")
                    await domain_services.update_dns_record(
                        dns_record_id=domain_record.id,
                        cloudflare_dns_record_id=cloudflare_dns_record_id
                    )


if __name__ == "__main__":
    app()
