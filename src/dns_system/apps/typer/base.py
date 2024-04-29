from loguru import logger
from aiohttp import ClientSession, TCPConnector

from dns_system.config.settings import settings
from dns_system.apps.typer.decorators import log_dns_actions


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DNSManager(metaclass=SingletonMeta):

    @property
    def config(self):
        return {
            "headers": {"Authorization": f"Bearer {settings.CLOUDFLARE_API_KEY}"},
            "connector": TCPConnector(ssl=False)
        }

    @log_dns_actions
    async def get(
        self,
        url: str,
        search_query: dict = None,
        zone_identifier: str = "",
        dns_identifier: str = "",
        dns_records: bool = False,
        detail: bool = False,
        **kwargs # noqa
    ):

        if dns_records and detail:
            url = f"{url}/{zone_identifier}/dns_records/{dns_identifier}"
        elif dns_records:
            url = f"{url}/{zone_identifier}/dns_records"

        async with ClientSession(**self.config) as session:
            async with session.get(url, params=search_query) as response:

                if response.status == 200:
                    payload = await response.json()
                    logger.info(f"Response text: {payload}")
                    return response
                else:
                    logger.error(f"Failed. Status code: {response.status}")
                    payload = await response.json()
                    logger.error(f"Response: {payload}")
                    return response

    @log_dns_actions
    async def post(
        self,
        payload: dict,
        url: str,
        zone_identifier: str = "",
        dns_records: bool = False,
        **kwargs # noqa
    ):

        if dns_records:
            url = f"{url}/{zone_identifier}/dns_records"
        async with ClientSession(**self.config) as session:
            async with session.post(url=url, json=payload) as response:

                payload = await response.json()
                logger.info(f"Response: {payload}")
                return response

    @log_dns_actions
    async def patch(
        self,
        payload: dict,
        url: str,
        zone_identifier: str,
        dns_identifier: str,
        dns_records: bool = False,
        **kwargs # noqa
    ):

        patch_url = f"{url}/{zone_identifier}"
        if dns_records:
            patch_url = f"{url}/{zone_identifier}/dns_records/{dns_identifier}"

        async with ClientSession(**self.config) as session:
            async with session.patch(url=patch_url, json=payload) as response:

                payload = await response.json()
                logger.info(f"Response: {payload}")
                return response

    @log_dns_actions
    async def delete(
        self,
        url: str,
        identifier: str,
        dns_identifier: str = "",
        dns_records: bool = False,
        **kwargs # noqa
    ):

        delete_url = f"{url}/{identifier}"
        if dns_records:
            delete_url = f"{url}/{identifier}/dns_records/{dns_identifier}"

        async with ClientSession(**self.config) as session:
            async with session.delete(url=delete_url) as response:
                logger.info(f"Response {response.status}")
                logger.info(f"Response text {await response.text()}")
                return response


manager = DNSManager()
