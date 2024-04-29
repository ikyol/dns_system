import uvicorn

from dns_system.app import app as fastapi
from dns_system.apps.commons.tasks import scheduler


def execute():
    """
    1. Run FastApi
    2. Start scheduler
    """
    scheduler.start()

    uvicorn.run(fastapi, host="0.0.0.0", port=8000)
