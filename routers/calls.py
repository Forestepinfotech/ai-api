"""
Call logs router
Endpoints for managing AI reception calls
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from models import CallLogCreate, CallLogUpdate, CallLogResponse, CallStatus
from database import db_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/calls",
    tags=["Calls"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/",
    response_model=CallLogResponse,
    summary="Create a new call log",
    description="Record a new incoming or outgoing call"
)
async def create_call(business_id: UUID, call_data: CallLogCreate):
    """
    Create a new call log entry
    
    - **business_id**: UUID of the business
    - **caller_phone**: Phone number of the caller
    - **caller_name**: Optional name of the caller
    """
    try:
        result = await db_service.create_call_log(
            str(business_id),
            call_data.model_dump()
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create call log")
        return result
    except Exception as e:
        logger.error(f"Error creating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/{call_id}",
    response_model=CallLogResponse,
    summary="Get call details",
    description="Retrieve details of a specific call"
)
async def get_call(call_id: UUID):
    """Get call log by ID"""
    try:
        result = await db_service.get_call_log(str(call_id))
        if not result:
            raise HTTPException(status_code=404, detail="Call not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/{call_id}",
    response_model=CallLogResponse,
    summary="Update call log",
    description="Update call status, transcript, or analysis"
)
async def update_call(call_id: UUID, call_update: CallLogUpdate):
    """Update call log"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in call_update.model_dump().items() if v is not None}
        
        result = await db_service.update_call_log(
            str(call_id),
            update_data
        )
        if not result:
            raise HTTPException(status_code=404, detail="Call not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/business/{business_id}",
    response_model=List[CallLogResponse],
    summary="Get business call history",
    description="Retrieve all calls for a specific business"
)
async def get_business_calls(
    business_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0)
):
    """
    Get all call logs for a business
    
    - **limit**: Number of results to return (1-500)
    - **skip**: Number of results to skip
    """
    try:
        result = await db_service.get_business_call_logs(str(business_id), limit=limit, offset=skip)
        return result
    except Exception as e:
        logger.error(f"Error getting business calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/business/{business_id}/summary",
    summary="Get call statistics",
    description="Get call summary statistics for a business"
)
async def get_call_statistics(business_id: UUID):
    """
    Get call statistics for a business
    
    Returns:
    - total_calls: Total number of calls
    - completed_calls: Completed calls
    - escalated_calls: Calls escalated to human
    - avg_sentiment: Average sentiment score
    """
    try:
        calls = await db_service.get_business_call_logs(str(business_id), 1000)
        
        total = len(calls)
        completed = len([c for c in calls if c.get("call_status") == "completed"])
        escalated = len([c for c in calls if c.get("escalated_to_human")])
        
        sentiments = [c.get("sentiment_score") for c in calls if c.get("sentiment_score")]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None
        
        return {
            "total_calls": total,
            "completed_calls": completed,
            "escalated_calls": escalated,
            "avg_sentiment": avg_sentiment
        }
    except Exception as e:
        logger.error(f"Error getting call statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
