from fastapi.testclient import TestClient

from app.models.health import Health  # noqa: F401
from app.models.version import Version  # noqa: F401


def test_get_health(client: TestClient):
    """Test case for get_health

    Liveness / readiness probe
    """

    headers = {}
    response = client.request(
        "GET",
        "/health",
        headers=headers,
    )

    assert response.status_code == 200


def test_get_version(client: TestClient):
    """Test case for get_version

    API and build/version info
    """

    headers = {}

    response = client.request(
        "GET",
        "/version",
        headers=headers,
    )

    assert response.status_code == 200
