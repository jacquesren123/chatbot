from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database.base import Base


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    phone_number = Column(String, nullable=False)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    context = Column(JSON, default={})
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(String, nullable=False)
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    lead_id: Optional[uuid.UUID] = None
    phone_number: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    context: Dict[str, Any] = Field(default_factory=dict)
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: uuid.UUID
    role: MessageRole
    content: str
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
