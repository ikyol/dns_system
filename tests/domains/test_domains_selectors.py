from datetime import datetime

import pytest

from dns_system.apps.db.session import driver
from dns_system.apps.db.models.domain_models import Domains


@pytest.fixture()
async def domain_create():
    """
    Creates one Domains objects in the database for use in tests.
    """
    async with driver.session() as db:
        current_datetime = datetime.now()
        timestamp = int(current_datetime.timestamp())
        domain = Domains(domain_name="helloworld.com", created_at=timestamp)
        db.add(domain)
        await db.commit()
        return domain
