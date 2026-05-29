from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database.base import Base


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    calendar_event_id = Column(String, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(String, default="30")
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appointment(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    lead_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    calendar_event_id: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
