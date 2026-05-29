from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid


class EventType(str, Enum):
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    LEAD_CREATED = "lead.created"
    LEAD_QUALIFIED = "lead.qualified"
    APPOINTMENT_SCHEDULED = "appointment.scheduled"
    CONVERSATION_ESCALATED = "conversation.escalated"
    WORKFLOW_TRIGGERED = "workflow.triggered"


class Event(BaseModel):
    id: str = str(uuid.uuid4())
    type: EventType
    tenant_id: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    metadata: Dict[str, Any] = {}
