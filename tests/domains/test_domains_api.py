from fastapi.testclient import TestClient

from dns_system.app import app
from dns_system.apps.domains.middleware import API_KEY


client = TestClient(app)


def test_get_domains():
    response = client.get("/api/v1/domains", params={"api_key": API_KEY})

    assert response.status_code == 200
