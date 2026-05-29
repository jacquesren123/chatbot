from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from shared.queue import MessagePublisher, Event, EventType

app = FastAPI(title="Scheduling Service")

publisher = MessagePublisher()


class AvailabilityRequest(BaseModel):
    tenant_id: str
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 30


class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    available: bool


class BookAppointmentRequest(BaseModel):
    tenant_id: str
    lead_id: str
    conversation_id: str
    start_time: datetime
    duration_minutes: int = 30
    attendee_email: Optional[str] = None
    attendee_phone: str


class AppointmentResponse(BaseModel):
    appointment_id: str
    calendar_event_id: str
    start_time: datetime
    end_time: datetime
    status: str


class SchedulingService:
    def __init__(self):
        self.credentials = self._get_credentials()

    def _get_credentials(self):
        # In production, implement proper OAuth flow
        # For POC, using service account or stored credentials
        return None

    async def get_availability(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        duration_minutes: int
    ) -> List[TimeSlot]:
        """Get available time slots from Google Calendar"""
        if not self.credentials:
            # Return mock availability for POC
            return self._generate_mock_availability(start_date, end_date, duration_minutes)
        
        service = build('calendar', 'v3', credentials=self.credentials)
        
        # Query calendar for busy times
        body = {
            "timeMin": start_date.isoformat() + 'Z',
            "timeMax": end_date.isoformat() + 'Z',
            "items": [{"id": "primary"}]
        }
        
        events_result = service.freebusy().query(body=body).execute()
        busy_times = events_result['calendars']['primary']['busy']
        
        # Generate available slots
        slots = []
        current = start_date
        
        while current < end_date:
            slot_end = current + timedelta(minutes=duration_minutes)
            is_available = not self._overlaps_busy_time(current, slot_end, busy_times)
            
            slots.append(TimeSlot(
                start=current,
                end=slot_end,
                available=is_available
            ))
            
            current += timedelta(minutes=30)
        
        return slots

    def _generate_mock_availability(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        duration_minutes: int
    ) -> List[TimeSlot]:
        """Generate mock availability for POC"""
        slots = []
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            if 9 <= current.hour < 17:  # Business hours
                slot_end = current + timedelta(minutes=duration_minutes)
                slots.append(TimeSlot(
                    start=current,
                    end=slot_end,
                    available=True
                ))
            
            current += timedelta(minutes=30)
            
            if current.hour >= 17:
                current = (current + timedelta(days=1)).replace(hour=9, minute=0)
        
        return slots[:20]  # Return first 20 slots

    def _overlaps_busy_time(self, start: datetime, end: datetime, busy_times: List) -> bool:
        for busy in busy_times:
            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            
            if start < busy_end and end > busy_start:
                return True
        
        return False

    async def book_appointment(
        self, 
        start_time: datetime, 
        duration_minutes: int,
        attendee_email: Optional[str],
        attendee_phone: str,
        lead_id: str
    ) -> AppointmentResponse:
        """Book appointment in Google Calendar"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        if not self.credentials:
            # Mock booking for POC
            return AppointmentResponse(
                appointment_id=f"apt_{lead_id}",
                calendar_event_id=f"cal_event_{lead_id}",
                start_time=start_time,
                end_time=end_time,
                status="scheduled"
            )
        
        service = build('calendar', 'v3', credentials=self.credentials)
        
        event = {
            'summary': f'Appointment with {attendee_phone}',
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
            'attendees': [{'email': attendee_email}] if attendee_email else [],
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return AppointmentResponse(
            appointment_id=f"apt_{lead_id}",
            calendar_event_id=created_event['id'],
            start_time=start_time,
            end_time=end_time,
            status="scheduled"
        )


service = SchedulingService()


@app.post("/availability", response_model=List[TimeSlot])
async def get_availability(request: AvailabilityRequest):
    try:
        slots = await service.get_availability(
            start_date=request.start_date,
            end_date=request.end_date,
            duration_minutes=request.duration_minutes
        )
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book", response_model=AppointmentResponse)
async def book_appointment(request: BookAppointmentRequest):
    try:
        appointment = await service.book_appointment(
            start_time=request.start_time,
            duration_minutes=request.duration_minutes,
            attendee_email=request.attendee_email,
            attendee_phone=request.attendee_phone,
            lead_id=request.lead_id
        )
        
        await publisher.publish(
            Event(
                type=EventType.APPOINTMENT_SCHEDULED,
                tenant_id=request.tenant_id,
                payload={
                    "appointment_id": appointment.appointment_id,
                    "lead_id": request.lead_id,
                    "start_time": appointment.start_time.isoformat()
                }
            ),
            routing_key="appointment.scheduled"
        )
        
        return appointment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
