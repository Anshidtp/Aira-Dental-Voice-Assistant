from beanie import PydanticObjectId
from beanie.operators import And, In
from datetime import datetime, date, time, timedelta
from typing import List, Optional
from loguru import logger

from ..models.database import Appointment, AppointmentStatus, LanguageEnum
from ..models.schemas import AppointmentCreate, AppointmentUpdate
from ..config.settings import settings


class AppointmentService:
    """Service for managing appointments with MongoDB"""
    
    @staticmethod
    async def create_appointment(
        appointment_data: AppointmentCreate,
        call_sid: Optional[str] = None
    ) -> Appointment:
        """
        Create a new appointment
        
        Args:
            appointment_data: Appointment data
            call_sid: Optional call SID for tracking
            
        Returns:
            Created appointment
        """
        try:
            # Combine date and time
            appointment_datetime = datetime.combine(
                appointment_data.appointment_date,
                datetime.strptime(appointment_data.appointment_time, "%H:%M").time()
            )
            
            # Create appointment document
            appointment = Appointment(
                patient_name=appointment_data.patient_name,
                patient_phone=appointment_data.patient_phone,
                patient_email=appointment_data.patient_email,
                appointment_date=appointment_datetime,
                appointment_time=appointment_data.appointment_time,
                duration_minutes=settings.APPOINTMENT_SLOT_DURATION,
                reason=appointment_data.reason,
                notes=appointment_data.notes,
                preferred_language=appointment_data.preferred_language,
                status=AppointmentStatus.PENDING,
                call_sid=call_sid,
            )
            
            # Insert into MongoDB
            await appointment.insert()
            
            logger.info(f"Created appointment {appointment.id} for {appointment.patient_name}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise
    
    @staticmethod
    async def get_appointment(
        appointment_id: str
    ) -> Optional[Appointment]:
        """Get appointment by ID"""
        try:
            appointment = await Appointment.get(PydanticObjectId(appointment_id))
            return appointment
            
        except Exception as e:
            logger.error(f"Error getting appointment: {e}")
            return None
    
    @staticmethod
    async def list_appointments(
        skip: int = 0,
        limit: int = 100,
        status: Optional[AppointmentStatus] = None,
        phone: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Appointment]:
        """
        List appointments with optional filters
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by status
            phone: Filter by phone number
            date_from: Filter appointments from this date
            date_to: Filter appointments until this date
            
        Returns:
            List of appointments
        """
        try:
            # Build query
            query = {}
            
            if status:
                query["status"] = status
            
            if phone:
                query["patient_phone"] = phone
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = datetime.combine(date_from, time.min)
                if date_to:
                    date_query["$lte"] = datetime.combine(date_to, time.max)
                query["appointment_date"] = date_query
            
            # Execute query
            appointments = await Appointment.find(query) \
                .sort("-appointment_date") \
                .skip(skip) \
                .limit(limit) \
                .to_list()
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error listing appointments: {e}")
            raise
    
    @staticmethod
    async def update_appointment(
        appointment_id: str,
        update_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """Update an appointment"""
        try:
            appointment = await AppointmentService.get_appointment(appointment_id)
            if not appointment:
                return None
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                setattr(appointment, field, value)
            
            appointment.updated_at = datetime.utcnow()
            
            # Save to MongoDB
            await appointment.save()
            
            logger.info(f"Updated appointment {appointment_id}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")
            raise
    
    @staticmethod
    async def cancel_appointment(
        appointment_id: str
    ) -> Optional[Appointment]:
        """Cancel an appointment"""
        try:
            appointment = await AppointmentService.get_appointment(appointment_id)
            if not appointment:
                return None
            
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancelled_at = datetime.utcnow()
            appointment.updated_at = datetime.utcnow()
            
            await appointment.save()
            
            logger.info(f"Cancelled appointment {appointment_id}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            raise
    
    @staticmethod
    async def confirm_appointment(
        appointment_id: str
    ) -> Optional[Appointment]:
        """Confirm an appointment"""
        try:
            appointment = await AppointmentService.get_appointment(appointment_id)
            if not appointment:
                return None
            
            appointment.status = AppointmentStatus.CONFIRMED
            appointment.confirmed_at = datetime.utcnow()
            appointment.updated_at = datetime.utcnow()
            
            await appointment.save()
            
            logger.info(f"Confirmed appointment {appointment_id}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error confirming appointment: {e}")
            raise
    
    @staticmethod
    async def check_availability(
        appointment_date: date,
        appointment_time: str
    ) -> bool:
        """
        Check if a time slot is available
        
        Args:
            appointment_date: Desired date
            appointment_time: Desired time (HH:MM)
            
        Returns:
            True if available
        """
        try:
            # Combine date and time
            desired_datetime = datetime.combine(
                appointment_date,
                datetime.strptime(appointment_time, "%H:%M").time()
            )
            
            # Check for overlapping appointments
            buffer_start = desired_datetime - timedelta(minutes=settings.APPOINTMENT_BUFFER_MINUTES)
            buffer_end = desired_datetime + timedelta(
                minutes=settings.APPOINTMENT_SLOT_DURATION + settings.APPOINTMENT_BUFFER_MINUTES
            )
            
            # Query for conflicts
            conflicts = await Appointment.find(
                {
                    "appointment_date": {
                        "$gte": buffer_start,
                        "$lt": buffer_end
                    },
                    "status": {
                        "$in": [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
                    }
                }
            ).to_list()
            
            is_available = len(conflicts) == 0
            logger.debug(f"Time slot {appointment_date} {appointment_time} available: {is_available}")
            
            return is_available
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    @staticmethod
    async def get_available_slots(
        target_date: date,
        slot_duration: int = None
    ) -> List[str]:
        """
        Get available time slots for a given date
        
        Args:
            target_date: Date to check
            slot_duration: Slot duration in minutes
            
        Returns:
            List of available time slots
        """
        try:
            if slot_duration is None:
                slot_duration = settings.APPOINTMENT_SLOT_DURATION
            
            # Define working hours (9 AM to 8 PM)
            start_hour = 9
            end_hour = 20
            
            all_slots = []
            current_time = datetime.combine(target_date, time(hour=start_hour))
            end_time = datetime.combine(target_date, time(hour=end_hour))
            
            while current_time < end_time:
                slot_time = current_time.strftime("%H:%M")
                
                # Check if slot is available
                is_available = await AppointmentService.check_availability(
                    target_date, slot_time
                )
                
                if is_available:
                    all_slots.append(slot_time)
                
                current_time += timedelta(minutes=slot_duration)
            
            logger.debug(f"Found {len(all_slots)} available slots for {target_date}")
            return all_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    @staticmethod
    async def get_appointments_count() -> dict:
        """Get appointment statistics"""
        try:
            total = await Appointment.count()
            
            # Count by status
            pending = await Appointment.find({"status": AppointmentStatus.PENDING}).count()
            confirmed = await Appointment.find({"status": AppointmentStatus.CONFIRMED}).count()
            cancelled = await Appointment.find({"status": AppointmentStatus.CANCELLED}).count()
            completed = await Appointment.find({"status": AppointmentStatus.COMPLETED}).count()
            
            return {
                "total": total,
                "pending": pending,
                "confirmed": confirmed,
                "cancelled": cancelled,
                "completed": completed,
            }
            
        except Exception as e:
            logger.error(f"Error getting appointment count: {e}")
            return {}


# Global service instance
appointment_service = AppointmentService()