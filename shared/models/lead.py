from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database.base import Base


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    CONVERTED = "converted"
    LOST = "lost"


class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
    qualification_score = Column(Float, default=0.0)
    attributes = Column(JSON, default={})
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QualificationScoreModel(Base):
    __tablename__ = "qualification_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    score = Column(Float, nullable=False)
    criteria = Column(JSON, default={})
    reasoning = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Lead(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    phone_number: str
    email: Optional[str] = None
    name: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    qualification_score: float = 0.0
    attributes: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QualificationScore(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    lead_id: uuid.UUID
    score: float
    criteria: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
