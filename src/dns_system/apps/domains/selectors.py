from typing import List, Optional

from sqlalchemy import select, delete, update, asc

from dns_system.apps.db.session import driver
from dns_system.apps.domains.constants import DomainDNSQueueStatus
from dns_system.apps.db.models.domain_models import Domains, DomainDNSQueue, DomainRecords, DomainDNSLog


class BaseProvider:

    model = None

    def __init__(self) -> None:
        self.session = driver.session

    async def update_fields(self, filter_data: dict, values: dict, *fields):
        async with self.session() as db:
            query = update(self.model).where(
                *(
                    getattr(self.model, field) == (
                        filter_data.get(field)
                    )
                    for field in fields
                )
            ).values(**values)
            await db.execute(query)
            await db.commit()

    async def delete_obj(self, filter_data: dict, *fields):
        async with self.session() as db:
            query = delete(self.model).where(
                *(
                    getattr(self.model, field) == (
                        filter_data.get(field)
                    )
                    for field in fields
                )
            )
            await db.execute(query)
            await db.commit()


class DomainProvider(BaseProvider):

    model = Domains

    async def get(self, *, name: str) -> Optional[Domains]:
        async with self.session() as db:
            query = select(self.model).filter(self.model.domain_name == name).order_by(
                self.model.id)
            domain = await db.execute(query)
            return domain.scalar_one_or_none()

    async def list(self) -> List[Domains]:
        async with self.session() as db:
            query = select(self.model).order_by(
                self.model.id)
            domain = await db.execute(query)
            return domain.scalars().all()


domain = DomainProvider()


class DomainRecordProvider(BaseProvider):

    model = DomainRecords

    async def get(self, *, cloudflare_id: str) -> Optional[DomainRecords]:
        async with self.session() as db:
            query = select(self.model).filter(self.model.cloudflare_dns_record_id == cloudflare_id).order_by(
                self.model.id)
            domain_record = await db.execute(query)
            return domain_record.scalar_one_or_none()

    async def list(self, *, domain_id: int) -> List[DomainRecords]:
        async with self.session() as db:
            query = select(self.model).filter(self.model.domain_id == domain_id).order_by(
                self.model.id)
            domain_records = await db.execute(query)
            return domain_records.scalars().all()


domain_records = DomainRecordProvider()


class DomainDNSQueueProvider(BaseProvider):

    model = DomainDNSQueue

    async def get(self, *, status: DomainDNSQueueStatus) -> DomainDNSQueue:
        async with self.session() as db:
            query = select(self.model).filter(self.model.status == status).order_by(
                asc(self.model.id))
            queue = await db.execute(query)
            return queue.scalars().first()


queue = DomainDNSQueueProvider()


class DomainDNSLogProvider(BaseProvider):

    model = DomainDNSLog

    async def create(self, *, data: dict) -> DomainDNSLog:
        async with self.session() as db:
            dns_log = DomainDNSLog(**data)
            db.add(dns_log)
            await db.commit()
            return dns_log


dns_log = DomainDNSLogProvider()
