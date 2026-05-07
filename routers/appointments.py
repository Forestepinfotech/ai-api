"""
Appointments router
Endpoints for managing business appointments
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from datetime import datetime
from models import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from database import db_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["Appointments"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/",
    response_model=AppointmentResponse,
    summary="Create appointment",
    description="Create a new appointment for a customer"
)
async def create_appointment(business_id: UUID, appointment_data: AppointmentCreate):
    """
    Create a new appointment
    
    - **business_id**: UUID of the business
    - **customer_name**: Name of the customer
    - **customer_phone**: Phone number of the customer
    - **appointment_date**: Date in YYYY-MM-DD format
    - **appointment_time**: Time in HH:MM format
    """
    try:
        # Combine date and time into appointment_datetime
        appointment_dt = f"{appointment_data.appointment_date}T{appointment_data.appointment_time}:00Z"
        
        data = appointment_data.model_dump()
        data["appointment_datetime"] = appointment_dt

        result = await db_service.create_appointment(str(business_id), data)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create appointment")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment details",
    description="Retrieve details of a specific appointment"
)
async def get_appointment(appointment_id: UUID):
    """Get appointment by ID"""
    try:
        result = await db_service.get_appointment(str(appointment_id))
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
    description="Update appointment details or status"
)
async def update_appointment(appointment_id: UUID, appointment_update: AppointmentUpdate):
    """Update appointment"""
    try:
        # Get current appointment first
        current = await db_service.get_appointment(str(appointment_id))
        if not current:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Prepare update data
        update_data = appointment_update.model_dump(exclude_unset=True)
        
        # If date or time changed, update datetime
        if "appointment_date" in update_data or "appointment_time" in update_data:
            date = update_data.get("appointment_date", current.get("appointment_date"))
            time = update_data.get("appointment_time", current.get("appointment_time"))
            update_data["appointment_datetime"] = f"{date}T{time}:00Z"
        
        result = await db_service.update_appointment(str(appointment_id), update_data)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update appointment")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/business/{business_id}",
    response_model=List[AppointmentResponse],
    summary="Get business appointments",
    description="Retrieve all appointments for a business"
)
async def get_business_appointments(
    business_id: UUID,
    status: str = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get all appointments for a business
    
    - **status**: Optional status filter (scheduled, confirmed, completed, cancelled)
    - **limit**: Number of results to return
    """
    try:
        result = await db_service.list_appointments(str(business_id), limit=limit)

        if status:
            result = [a for a in result if a.get("status") == status]

        return result
    except Exception as e:
        logger.error(f"Error getting appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/business/{business_id}/upcoming",
    response_model=List[AppointmentResponse],
    summary="Get upcoming appointments",
    description="Get appointments scheduled for the future"
)
async def get_upcoming_appointments(business_id: UUID, days_ahead: int = Query(7, ge=1, le=90)):
    """
    Get upcoming appointments for a business
    
    - **days_ahead**: Number of days to look ahead
    """
    try:
        result = await db_service.list_appointments(str(business_id), limit=500)

        active_statuses = ["scheduled", "confirmed"]
        result = [a for a in result if a.get("status") in active_statuses]

        return result
    except Exception as e:
        logger.error(f"Error getting upcoming appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
