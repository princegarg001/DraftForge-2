from typing import Dict
from pydantic import BaseModel


class ServiceStatus(BaseModel):
    reachable: bool
    details: str


class HealthCheckResponse(BaseModel):
    status: str
    app_version: str
    services: Dict[str, ServiceStatus]