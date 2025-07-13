from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from dependencies import get_rabbitmq_service
from models.models import EnergyData
from services.rabbitmq_service import RabbitMQService
from services.energy_service import EnergyDataService

router = APIRouter()
energy_service = EnergyDataService()

@router.post("/collect", response_model=List[EnergyData], summary="Collect Energy Data", description="Collect energy data within a specified timeframe and send it to RabbitMQ.")
async def collect_energy_data(
    start_time: datetime = Query(..., description="Start of the timeframe"),
    end_time: datetime = Query(..., description="End of the timeframe"),
    rabbitmq_service_instance: RabbitMQService = Depends(get_rabbitmq_service)
):
    """
    Collect energy data from diffrent api´s within a specified timeframe and send it to RabbitMQ.

    Args:
        start_time (datetime): The start of the timeframe.
        end_time (datetime): The end of the timeframe.

    Returns:
        List[EnergyData]: The collected energy data.

    Raises:
        HTTPException: If the start time is not earlier than the end time.
    """
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be earlier than end time"
        )
    data = []  # await energy_service.collect_energy_data(start_time, end_time)
    await rabbitmq_service_instance.send_data(data)
    return data