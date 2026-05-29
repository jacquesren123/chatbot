from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx

from shared.queue import MessagePublisher, Event, EventType
from shared.models import Lead, LeadStatus

app = FastAPI(title="Qualification Engine Service")

publisher = MessagePublisher()


class QualificationRequest(BaseModel):
    lead_id: str
    tenant_id: str
    conversation_history: List[Dict[str, Any]]
    lead_attributes: Dict[str, Any]


class QualificationResponse(BaseModel):
    score: float
    is_qualified: bool
    criteria_met: Dict[str, bool]
    reasoning: str
    next_action: str


class QualificationEngine:
    def __init__(self):
        self.default_rules = {
            "has_budget": {"weight": 0.3, "required": True},
            "has_timeline": {"weight": 0.2, "required": False},
            "decision_maker": {"weight": 0.3, "required": True},
            "need_identified": {"weight": 0.2, "required": True}
        }

    async def qualify_lead(
        self, 
        conversation_history: List[Dict[str, Any]], 
        lead_attributes: Dict[str, Any],
        rules: Optional[Dict[str, Any]] = None
    ) -> QualificationResponse:
        rules = rules or self.default_rules
        
        # Rule-based scoring
        criteria_met = self._evaluate_criteria(conversation_history, lead_attributes)
        
        # Calculate weighted score
        score = 0.0
        for criterion, rule in rules.items():
            if criteria_met.get(criterion, False):
                score += rule["weight"]
        
        # AI-enhanced reasoning
        reasoning = await self._generate_reasoning(conversation_history, criteria_met)
        
        is_qualified = score >= 0.7 and all(
            criteria_met.get(k, False) 
            for k, v in rules.items() 
            if v.get("required", False)
        )
        
        next_action = "schedule_appointment" if is_qualified else "continue_nurturing"
        
        return QualificationResponse(
            score=score,
            is_qualified=is_qualified,
            criteria_met=criteria_met,
            reasoning=reasoning,
            next_action=next_action
        )

    def _evaluate_criteria(
        self, 
        conversation_history: List[Dict[str, Any]], 
        lead_attributes: Dict[str, Any]
    ) -> Dict[str, bool]:
        conversation_text = " ".join([msg.get("content", "") for msg in conversation_history]).lower()
        
        return {
            "has_budget": any(word in conversation_text for word in ["budget", "afford", "price", "cost"]),
            "has_timeline": any(word in conversation_text for word in ["soon", "urgent", "asap", "this week", "next month"]),
            "decision_maker": lead_attributes.get("is_decision_maker", False) or "decision" in conversation_text,
            "need_identified": len(conversation_history) >= 3
        }

    async def _generate_reasoning(
        self, 
        conversation_history: List[Dict[str, Any]], 
        criteria_met: Dict[str, bool]
    ) -> str:
        met_criteria = [k for k, v in criteria_met.items() if v]
        unmet_criteria = [k for k, v in criteria_met.items() if not v]
        
        reasoning = f"Lead has demonstrated: {', '.join(met_criteria)}. "
        if unmet_criteria:
            reasoning += f"Still needs to establish: {', '.join(unmet_criteria)}."
        
        return reasoning


engine = QualificationEngine()


@app.post("/qualify", response_model=QualificationResponse)
async def qualify_lead(request: QualificationRequest):
    try:
        result = await engine.qualify_lead(
            conversation_history=request.conversation_history,
            lead_attributes=request.lead_attributes
        )
        
        if result.is_qualified:
            await publisher.publish(
                Event(
                    type=EventType.LEAD_QUALIFIED,
                    tenant_id=request.tenant_id,
                    payload={
                        "lead_id": request.lead_id,
                        "score": result.score,
                        "next_action": result.next_action
                    }
                ),
                routing_key="lead.qualified"
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
