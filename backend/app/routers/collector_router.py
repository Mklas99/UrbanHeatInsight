from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import os

from ..database.database import get_db_session
from ..repositories.heatmap_repo import HeatmapRepository
from ..services.gpkg_converter import GPKGtoGeoJSONConverter
from ..models.base_models import HeatmapPointCreate, GPKGUploadResponse
from ..core.logger_config import logger

router = APIRouter()

@router.post("/collector/upload-gpkg", response_model=GPKGUploadResponse)
async def upload_gpkg_file(
    file: UploadFile = File(...),
    layer_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
) -> GPKGUploadResponse:
    """
    Upload and process a GPKG file to extract heatmap data.

    Args:
        file: Uploaded GPKG file.
        layer_name: Optional layer name to extract.
        db: Database session.

    Returns:
        GPKGUploadResponse: Result of the upload and processing.
    """
    if not file.filename.endswith('.gpkg'):
        raise HTTPException(status_code=400, detail="File must be a GPKG file")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpkg') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        converter = GPKGtoGeoJSONConverter(tmp_path)
        geojson_data = converter.convert(layer_name)
        repo = HeatmapRepository(db)
        points_created = 0
        for feature in geojson_data.get('features', []):
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            if geometry.get('type') == 'Point':
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) >= 2:
                    intensity = properties.get('intensity', 0.5)
                    temperature = properties.get('temperature')
                    humidity = properties.get('humidity')
                    point_data = HeatmapPointCreate(
                        latitude=coordinates[1],
                        longitude=coordinates[0],
                        intensity=min(max(intensity, 0), 1),
                        temperature=temperature,
                        humidity=humidity,
                        source="gpkg_upload"
                    )
                    await repo.create_point(point_data)
                    points_created += 1
        os.unlink(tmp_path)
        logger.info(f"Successfully processed GPKG file: {points_created} points created")
        return GPKGUploadResponse(
            message=f"Successfully processed GPKG file",
            points_created=points_created
        )
    except Exception as e:
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        logger.error(f"Error processing GPKG file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process GPKG file: {str(e)}")

@router.post("/collector/manual-point")
async def add_manual_point(
    point: HeatmapPointCreate,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Manually add a heatmap point.

    Args:
        point: Heatmap point data.
        db: Database session.

    Returns:
        dict: Success message and point ID.
    """
    try:
        repo = HeatmapRepository(db)
        point.source = "manual"
        db_point = await repo.create_point(point)
        return {"message": "Point added successfully", "point_id": str(db_point.id)}
    except Exception as e:
        logger.error(f"Error adding manual point: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add point")

# NOTE: If this router grows, split endpoints into separate modules