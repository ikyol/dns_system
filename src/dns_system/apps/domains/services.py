from datetime import datetime

from dns_system.apps.domains import selectors


async def update_dns_record(dns_record_id: int, cloudflare_dns_record_id: str):
    await selectors.domain_records.update_fields(
        {"id": dns_record_id},
        {"cloudflare_dns_record_id": cloudflare_dns_record_id},
        *["id"]
    )


async def update_domain(domain_name: str, cloudflare_domain_id: str):
    current_datetime = datetime.now()
    timestamp_integer = int(current_datetime.timestamp())

    domain = await selectors.domain.get(name=domain_name)
    await selectors.domain.update_fields(
        {"domain_name": domain.domain_name},
        {"cloudflare_domain_id": cloudflare_domain_id, "updated_at": timestamp_integer},
        *["domain_name"]
    )
