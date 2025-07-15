from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database.database import get_db_session
from ..repositories.heatmap_repo import HeatmapRepository
from ..models.base_models import (
    HeatmapPointCreate, 
    HeatmapPointResponse, 
    HeatmapData
)
from ..core.logger_config import logger

router = APIRouter()

@router.get("/heatmap", response_model=HeatmapData)
async def get_heatmap_data(
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lat: Optional[float] = Query(None, ge=-90, le=90), 
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    limit: int = Query(1000, le=10000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> HeatmapData:
    """
    Get heatmap data with optional geographical bounds filtering.

    Args:
        min_lat: Minimum latitude.
        max_lat: Maximum latitude.
        min_lon: Minimum longitude.
        max_lon: Maximum longitude.
        limit: Maximum number of points to return.
        offset: Offset for pagination.
        db: Database session.

    Returns:
        HeatmapData: The heatmap data.
    """
    try:
        repo = HeatmapRepository(db)
        if all(coord is not None for coord in [min_lat, max_lat, min_lon, max_lon]):
            if max_lat <= min_lat or max_lon <= min_lon:
                raise HTTPException(status_code=400, detail="Invalid bounds")
            points = await repo.get_points_in_bounds(min_lat, max_lat, min_lon, max_lon, limit)
            bounds = {
                "min_lat": min_lat, "max_lat": max_lat,
                "min_lon": min_lon, "max_lon": max_lon
            }
        else:
            points = await repo.get_all_points(limit, offset)
            bounds = None
        point_responses = [HeatmapPointResponse.from_orm(point) for point in points]
        return HeatmapData(
            points=point_responses,
            total_count=len(point_responses),
            bounds=bounds
        )
    except Exception as e:
        logger.error(f"Error fetching heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/heatmap/point", response_model=HeatmapPointResponse)
async def create_heatmap_point(
    point: HeatmapPointCreate,
    db: AsyncSession = Depends(get_db_session)
) -> HeatmapPointResponse:
    """
    Create a new heatmap point.

    Args:
        point: Heatmap point data.
        db: Database session.

    Returns:
        HeatmapPointResponse: The created heatmap point.
    """
    try:
        repo = HeatmapRepository(db)
        db_point = await repo.create_point(point)
        return HeatmapPointResponse.from_orm(db_point)
    except Exception as e:
        logger.error(f"Error creating heatmap point: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create point")

@router.get("/heatmap/statistics")
async def get_heatmap_statistics(db: AsyncSession = Depends(get_db_session)) -> dict:
    """
    Get heatmap statistics.

    Args:
        db: Database session.

    Returns:
        dict: Statistics about heatmap points.
    """
    try:
        repo = HeatmapRepository(db)
        stats = await repo.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.delete("/heatmap/point/{point_id}")
async def delete_heatmap_point(
    point_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Delete a heatmap point.

    Args:
        point_id: ID of the point to delete.
        db: Database session.

    Returns:
        dict: Success message.
    """
    try:
        repo = HeatmapRepository(db)
        success = await repo.delete_point(point_id)
        if not success:
            raise HTTPException(status_code=404, detail="Point not found")
        return {"message": "Point deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting point: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete point")

# NOTE: If this router grows, split endpoints into separate modules (e.g., heatmap_points.py, heatmap_stats.py)
