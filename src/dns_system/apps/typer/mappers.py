from dns_system.apps.commons.constants import CREATE_ZONE, DELETE_ZONE, SYNC_DNS_RECORD
from dns_system.apps.typer.tasks import create_zone, delete_zone, sync_dns_records

TASK = {
        CREATE_ZONE: create_zone,
        DELETE_ZONE: delete_zone,
        SYNC_DNS_RECORD: sync_dns_records
}
