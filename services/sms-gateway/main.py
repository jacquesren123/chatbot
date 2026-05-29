from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import sys
import httpx
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.queue import MessagePublisher, Event, EventType

app = FastAPI(title="SMS Gateway Service")

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
publisher = MessagePublisher()

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8001")


class SendSMSRequest(BaseModel):
    to: str
    message: str
    tenant_id: str
    conversation_id: Optional[str] = None


@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """Handle incoming SMS from Twilio"""
    form_data = await request.form()
    
    from_number = form_data.get("From")
    message_body = form_data.get("Body")
    message_sid = form_data.get("MessageSid")
    
    await publisher.publish(
        Event(
            type=EventType.MESSAGE_RECEIVED,
            tenant_id="default",  # Extract from phone number mapping
            payload={
                "from": from_number,
                "message": message_body,
                "message_sid": message_sid
            }
        ),
        routing_key="message.received"
    )
    
    # Process with AI Engine
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AI_ENGINE_URL}/chat",
                json={
                    "conversation_id": from_number,
                    "tenant_id": "default",
                    "message": message_body,
                    "context": {}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Send response via Twilio
                twilio_client.messages.create(
                    body=ai_response["response"],
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=from_number
                )
                
                await publisher.publish(
                    Event(
                        type=EventType.MESSAGE_SENT,
                        tenant_id="default",
                        payload={
                            "to": from_number,
                            "message": ai_response["response"]
                        }
                    ),
                    routing_key="message.sent"
                )
        except Exception as e:
            print(f"Error processing message: {e}")
    
    return MessagingResponse()


@app.post("/send")
async def send_sms(request: SendSMSRequest):
    """Send outbound SMS"""
    try:
        message = twilio_client.messages.create(
            body=request.message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=request.to
        )
        
        await publisher.publish(
            Event(
                type=EventType.MESSAGE_SENT,
                tenant_id=request.tenant_id,
                payload={
                    "to": request.to,
                    "message": request.message,
                    "message_sid": message.sid
                }
            ),
            routing_key="message.sent"
        )
        
        return {"status": "sent", "message_sid": message.sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
