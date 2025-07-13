from uuid import UUID
from fastapi import APIRouter
from fastapi.params import Depends
from api import collector_router
from . import energy_data_router, rabbitmq_router

# Define a custom JSON schema for PydanticObjectId
def custom_pydantic_object_id_schema(schema: dict):
    return {
        "type": "string",
        "format": "objectid",
        "example": "507f1f77bcf86cd799439011"
    }

# Register the custom schema with Pydantic
UUID.__get_pydantic_json_schema__ = custom_pydantic_object_id_schema

api_router = APIRouter()

api_router.include_router(energy_data_router.router, prefix="/energy", tags=["Energy Data"])
api_router.include_router(rabbitmq_router.router, prefix="/rabbitmq", tags=["RabbitMQ"])
api_router.include_router(collector_router.router, prefix="/collector", tags=["Collector"])
