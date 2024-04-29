from dns_system.config.settings import settings
from dns_system.apps.domains.constants import TaskEnum

CLOUDFLARE_API = settings.CLOUDFLARE_API
CREATE_ZONE = TaskEnum.CREATE_ZONE.value
DELETE_ZONE = TaskEnum.DELETE_ZONE.value
SYNC_DNS_RECORD = TaskEnum.SYNC_DNS_RECORD.value
