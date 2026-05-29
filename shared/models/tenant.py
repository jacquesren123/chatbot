from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database.base import Base


class TenantModel(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tenant(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    api_key: str
    config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TenantConfig(BaseModel):
    ai_provider: str = "openai"
    ai_model: str = "gpt-4-turbo-preview"
    qualification_rules: Dict[str, Any] = Field(default_factory=dict)
    business_hours: Dict[str, Any] = Field(default_factory=dict)
    escalation_threshold: float = 0.7
    max_conversation_turns: int = 20
