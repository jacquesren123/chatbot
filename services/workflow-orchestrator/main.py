from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio

from shared.queue import MessageConsumer, MessagePublisher, Event, EventType

app = FastAPI(title="Workflow Orchestrator Service")

publisher = MessagePublisher()


class WorkflowEngine:
    def __init__(self):
        self.active_workflows = {}

    async def start_listening(self):
        consumer = MessageConsumer(
            queue_name="workflow_orchestrator",
            routing_keys=["lead.qualified", "appointment.scheduled", "conversation.escalated"]
        )
        
        await consumer.consume(self.handle_event)

    async def handle_event(self, event: Event):
        if event.type == EventType.LEAD_QUALIFIED:
            await self.trigger_qualified_lead_workflow(event)
        elif event.type == EventType.APPOINTMENT_SCHEDULED:
            await self.trigger_appointment_workflow(event)
        elif event.type == EventType.CONVERSATION_ESCALATED:
            await self.trigger_escalation_workflow(event)

    async def trigger_qualified_lead_workflow(self, event: Event):
        """Workflow: Send confirmation SMS and schedule follow-up"""
        lead_id = event.payload.get("lead_id")
        
        # Step 1: Send confirmation message
        await publisher.publish(
            Event(
                type=EventType.MESSAGE_SENT,
                tenant_id=event.tenant_id,
                payload={
                    "lead_id": lead_id,
                    "message": "Great! You're qualified. Let's schedule a time to talk.",
                    "workflow_step": "confirmation"
                }
            ),
            routing_key="message.send"
        )
        
        # Step 2: Schedule follow-up in 24 hours if no appointment booked
        await asyncio.sleep(1)  # In production, use scheduled tasks
        print(f"Scheduled follow-up for lead {lead_id}")

    async def trigger_appointment_workflow(self, event: Event):
        """Workflow: Send confirmation and reminders"""
        appointment_id = event.payload.get("appointment_id")
        
        # Send confirmation
        await publisher.publish(
            Event(
                type=EventType.MESSAGE_SENT,
                tenant_id=event.tenant_id,
                payload={
                    "appointment_id": appointment_id,
                    "message": "Your appointment is confirmed! We'll send a reminder 24 hours before.",
                    "workflow_step": "appointment_confirmation"
                }
            ),
            routing_key="message.send"
        )

    async def trigger_escalation_workflow(self, event: Event):
        """Workflow: Notify agents and prepare handoff"""
        conversation_id = event.payload.get("conversation_id")
        
        print(f"Escalating conversation {conversation_id} to human agent")
        # In production: notify agent dashboard, send alerts, etc.


engine = WorkflowEngine()


@app.on_event("startup")
async def startup():
    asyncio.create_task(engine.start_listening())


@app.get("/health")
async def health():
    return {"status": "healthy"}
