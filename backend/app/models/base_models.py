from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class HeatmapPointBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    intensity: float = Field(..., ge=0, le=1, description="Heat intensity (0-1)")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    source: Optional[str] = Field(None, description="Data source")

class HeatmapPointCreate(HeatmapPointBase):
    pass

class HeatmapPointResponse(HeatmapPointBase):
    id: UUID
    timestamp: datetime
    
    class Config:
        from_attributes = True

class HeatmapData(BaseModel):
    points: List[HeatmapPointResponse]
    total_count: int
    bounds: Optional[dict] = None

class BoundsQuery(BaseModel):
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    limit: Optional[int] = Field(1000, le=10000)

    @validator('max_lat')
    def validate_lat_bounds(cls, v, values):
        if 'min_lat' in values and v <= values['min_lat']:
            raise ValueError('max_lat must be greater than min_lat')
        return v

    @validator('max_lon')
    def validate_lon_bounds(cls, v, values):
        if 'min_lon' in values and v <= values['min_lon']:
            raise ValueError('max_lon must be greater than min_lon')
        return v

class GPKGUploadResponse(BaseModel):
    message: str
    points_created: int
    dataset_id: Optional[UUID] = None