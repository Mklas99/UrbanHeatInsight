from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from ..models.heatmap import HeatmapPoint, HeatmapDataset
from ..models.base_models import HeatmapPointCreate, HeatmapPointResponse

class HeatmapRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_point(self, point_data: HeatmapPointCreate) -> HeatmapPoint:
        """Create a new heatmap point"""
        db_point = HeatmapPoint(
            latitude=point_data.latitude,
            longitude=point_data.longitude,
            intensity=point_data.intensity,
            temperature=point_data.temperature,
            humidity=point_data.humidity,
            source=point_data.source,
            geometry=ST_SetSRID(ST_MakePoint(point_data.longitude, point_data.latitude), 4326)
        )
        self.db.add(db_point)
        await self.db.commit()
        await self.db.refresh(db_point)
        return db_point

    async def get_points_in_bounds(
        self, 
        min_lat: float, 
        max_lat: float, 
        min_lon: float, 
        max_lon: float,
        limit: int = 1000
    ) -> List[HeatmapPoint]:
        """Get heatmap points within geographical bounds"""
        query = select(HeatmapPoint).where(
            HeatmapPoint.latitude >= min_lat,
            HeatmapPoint.latitude <= max_lat,
            HeatmapPoint.longitude >= min_lon,
            HeatmapPoint.longitude <= max_lon
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all_points(self, limit: int = 1000, offset: int = 0) -> List[HeatmapPoint]:
        """Get all heatmap points with pagination"""
        query = select(HeatmapPoint).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_point_by_id(self, point_id: str) -> Optional[HeatmapPoint]:
        """Get a single heatmap point by ID"""
        query = select(HeatmapPoint).where(HeatmapPoint.id == point_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_point(self, point_id: str) -> bool:
        """Delete a heatmap point"""
        point = await self.get_point_by_id(point_id)
        if point:
            await self.db.delete(point)
            await self.db.commit()
            return True
        return False

    async def create_dataset(self, name: str, description: str = None) -> HeatmapDataset:
        """Create a new dataset"""
        dataset = HeatmapDataset(name=name, description=description)
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def get_statistics(self) -> Dict[str, Any]:
        """Get heatmap statistics"""
        total_points = await self.db.scalar(select(func.count(HeatmapPoint.id)))
        avg_intensity = await self.db.scalar(select(func.avg(HeatmapPoint.intensity)))
        max_intensity = await self.db.scalar(select(func.max(HeatmapPoint.intensity)))
        min_intensity = await self.db.scalar(select(func.min(HeatmapPoint.intensity)))
        
        return {
            "total_points": total_points or 0,
            "average_intensity": float(avg_intensity) if avg_intensity else 0.0,
            "max_intensity": float(max_intensity) if max_intensity else 0.0,
            "min_intensity": float(min_intensity) if min_intensity else 0.0,
        }
