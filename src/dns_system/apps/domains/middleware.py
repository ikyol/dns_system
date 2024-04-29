import json
import os

from fastapi.security import APIKeyHeader

from dns_system.utils.exceptions import PermissionDenied


config_path = os.path.join(os.path.dirname(__file__), "../../../config/config.json")

with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

API_KEY = config_data["API_KEY"]

api_key_header = APIKeyHeader(name="X-API-Key")


async def auth_middleware(api_key: str = api_key_header):
    if api_key == API_KEY:
        return
    raise PermissionDenied()
