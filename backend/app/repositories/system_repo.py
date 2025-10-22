from datetime import datetime

from backend.app.models.health import Health

from app.models.version import Version


class SystemRepository:
    def __init__(self):
        super().__init_subclass__()

    async def get_health(self) -> Health:
        return Health(status="ok", dependencies={"database": "?", "cache": "?"})

    async def get_version(self) -> Version:
        return Version(
            api_version="0.0.1",
            time=datetime.fromisoformat("2024-01-01T00:00:00"),
            build_sha="0000000",
            model_version="v0.0.1",
        )
