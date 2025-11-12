"""
Synthetic data generation endpoints
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import pandas as pd
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.core.permissions import Permission, has_permission
from app.models.user import User
from app.schemas.synthetic_data import (
    SyntheticDataRequest,
    SyntheticDataResponse,
    SyntheticDataStatsResponse,
)

router = APIRouter()


@router.post("/generate", response_model=SyntheticDataResponse)
async def generate_synthetic_data(
    request: SyntheticDataRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Generate synthetic sensor data (admin only)"""
    if not has_permission(current_user.role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Admin access required"
        )
    
    try:
        # Import generator
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "data-processing"))
        
        from synthetic_data_generator import SyntheticALSDataGenerator
        
        # Initialize generator
        generator = SyntheticALSDataGenerator(seed=request.seed)
        
        # Calculate start date
        start_date = request.start_date or (datetime.utcnow() - timedelta(days=request.days))
        
        # Generate data
        if len(request.well_ids) == 1:
            df = generator.generate_well_data(
                well_id=request.well_ids[0],
                start_date=start_date,
                days=request.days,
                interval_seconds=request.interval_seconds,
                include_anomalies=request.include_anomalies,
                include_failures=request.include_failures,
                failure_probability=request.failure_probability,
            )
        else:
            df = generator.generate_multiple_wells(
                well_ids=request.well_ids,
                start_date=start_date,
                days=request.days,
                interval_seconds=request.interval_seconds,
                include_anomalies=request.include_anomalies,
                include_failures=request.include_failures,
                failure_probability=request.failure_probability,
            )
        
        # Export if requested
        output_path = None
        if request.export_format:
            output_dir = Path("data/generated")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"synthetic_data_{timestamp}"
            
            if request.export_format == 'parquet':
                output_path = output_dir / f"{filename}.parquet"
                generator.export_to_parquet(df, output_path)
            elif request.export_format == 'csv':
                output_path = output_dir / f"{filename}.csv"
                generator.export_to_csv(df, output_path)
            elif request.export_format == 'json':
                output_path = output_dir / f"{filename}.json"
                # Limit JSON export to avoid memory issues
                sample_df = df.head(10000) if len(df) > 10000 else df
                generator.export_to_json(sample_df, output_path)
        
        # Get statistics
        stats = generator.get_statistics(df)
        
        return SyntheticDataResponse(
            success=True,
            message=f"Generated {len(df):,} records",
            record_count=len(df),
            well_ids=request.well_ids,
            date_range={
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat(),
            },
            output_path=str(output_path) if output_path else None,
            statistics=stats,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating synthetic data: {str(e)}"
        )


@router.get("/stats", response_model=SyntheticDataStatsResponse)
async def get_synthetic_data_stats(
    file_path: str = Query(..., description="Path to generated data file"),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics for generated synthetic data file"""
    if not has_permission(current_user.role, Permission.VIEW_SENSOR_DATA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Load data based on format
        if file_path.suffix == '.parquet':
            df = pd.read_parquet(file_path)
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format"
            )
        
        # Import generator for statistics
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "data-processing"))
        
        from synthetic_data_generator import SyntheticALSDataGenerator
        
        generator = SyntheticALSDataGenerator()
        stats = generator.get_statistics(df)
        
        return SyntheticDataStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )

