import enum


class DomainDNSQueueStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    ERROR = 3


class TaskEnum(enum.Enum):
    CREATE_ZONE = 1
    DELETE_ZONE = 2
    SYNC_DNS_RECORD = 3
