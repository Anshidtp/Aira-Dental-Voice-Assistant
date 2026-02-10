from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from loguru import logger

from backend.models.database import AppointmentStatus
from backend.models.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentList
)
from backend.services.appointment_service import appointment_service


router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(appointment: AppointmentCreate):
    """
    Create a new appointment
    
    Args:
        appointment: Appointment data
        
    Returns:
        Created appointment
    """
    try:
        # Check availability
        is_available = await appointment_service.check_availability(
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time
        )
        
        if not is_available:
            raise HTTPException(
                status_code=400,
                detail="The requested time slot is not available"
            )
        
        # Create appointment
        created_appointment = await appointment_service.create_appointment(
            appointment_data=appointment
        )
        
        # Ensure response fields are correct
        return {
            "id": created_appointment.id,
            "patient_name": created_appointment.patient_name,
            "patient_phone": created_appointment.patient_phone,
            "patient_email": created_appointment.patient_email,
            "appointment_date": created_appointment.appointment_date,
            "appointment_time": created_appointment.appointment_time,
            "duration_minutes": created_appointment.duration_minutes,
            "reason": created_appointment.reason,
            "notes": created_appointment.notes,
            "preferred_language": created_appointment.preferred_language,
            "status": created_appointment.status,
            "created_at": created_appointment.created_at,
            "updated_at": created_appointment.updated_at,
            "confirmed_at": created_appointment.confirmed_at,
            "cancelled_at": created_appointment.cancelled_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=AppointmentList)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AppointmentStatus] = None,
    phone: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """
    List appointments with optional filters
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        status: Filter by status
        phone: Filter by phone
        date_from: Filter from date
        date_to: Filter to date
        
    Returns:
        List of appointments
    """
    try:
        appointments = await appointment_service.list_appointments(
            skip=skip,
            limit=limit,
            status=status,
            phone=phone,
            date_from=date_from,
            date_to=date_to
        )
        
        return AppointmentList(
            appointments=appointments,
            total=len(appointments),
            page=skip // limit + 1,
            page_size=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_appointment_stats():
    """Get appointment statistics"""
    try:
        stats = await appointment_service.get_appointments_count()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting appointment stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    """
    Get appointment by ID
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        Appointment details
    """
    try:
        appointment = await appointment_service.get_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    update_data: AppointmentUpdate
):
    """
    Update an appointment
    
    Args:
        appointment_id: Appointment ID
        update_data: Update data
        
    Returns:
        Updated appointment
    """
    try:
        appointment = await appointment_service.update_appointment(
            appointment_id=appointment_id,
            update_data=update_data
        )
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """
    Cancel an appointment
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        Success message
    """
    try:
        appointment = await appointment_service.cancel_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return {"message": "Appointment cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(appointment_id: str):
    """
    Confirm an appointment
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        Confirmed appointment
    """
    try:
        appointment = await appointment_service.confirm_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return appointment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability/{target_date}")
async def check_availability(target_date: date):
    """
    Get available time slots for a date
    
    Args:
        target_date: Date to check
        
    Returns:
        List of available slots
    """
    try:
        available_slots = await appointment_service.get_available_slots(
            target_date=target_date
        )
        
        return {
            "date": target_date.isoformat(),
            "available_slots": available_slots,
            "count": len(available_slots)
        }
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))