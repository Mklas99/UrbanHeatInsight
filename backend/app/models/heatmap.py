from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

from ..database.database import Base

class HeatmapPoint(Base):
    __tablename__ = "heatmap_points"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    intensity = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)  # sensor, satellite, manual
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    geometry = Column(Geometry('POINT', srid=4326), nullable=True)
    meta_data = Column(String)  # JSON string for additional data
    
    def __repr__(self):
        return f"<HeatmapPoint(lat={self.latitude}, lon={self.longitude}, intensity={self.intensity})>"

class HeatmapDataset(Base):
    __tablename__ = "heatmap_datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500), nullable=True)
    bounds = Column(Geometry('POLYGON', srid=4326), nullable=True)
    point_count = Column(Integer, default=0)
