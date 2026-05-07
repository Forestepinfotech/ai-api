"""
AI Receptionist router
Endpoints for Claude-powered receptionist chat and call analysis
"""

from fastapi import APIRouter, HTTPException
from uuid import UUID
import anthropic
import json

from database import db_service
from models import (
    ReceptionistChatRequest,
    ReceptionistChatResponse,
    CallAnalysisResponse,
)
from config import settings

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI Receptionist"],
)

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

_SYSTEM_PROMPT = (
    "You are a professional AI receptionist. Your job is to greet callers warmly, "
    "understand their needs, and either answer their questions or schedule appointments. "
    "Be concise, friendly, and helpful. Always try to detect the caller's intent: "
    "appointment booking, general inquiry, complaint, or emergency. "
    "If it is an emergency, immediately advise the caller to call 911 or the relevant emergency service. "
    "When you detect an intent, mention it briefly. "
    "Keep responses under 3 sentences unless more detail is genuinely required."
)


def _build_messages(request: ReceptionistChatRequest) -> list:
    messages = []
    for msg in request.conversation_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})
    return messages


def _detect_intent(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["appointment", "book", "schedule", "reschedule", "cancel"]):
        return "appointment"
    if any(w in lower for w in ["emergency", "urgent", "911", "ambulance"]):
        return "emergency"
    if any(w in lower for w in ["complaint", "unhappy", "problem", "issue", "wrong"]):
        return "complaint"
    return "general_inquiry"


@router.post("/chat", response_model=ReceptionistChatResponse)
async def chat(request: ReceptionistChatRequest):
    business = await db_service.get_business(str(request.business_id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    system_prompt = business.get("ai_greeting_message") or _SYSTEM_PROMPT

    try:
        response = await _client.messages.create(
            model=settings.model_name,
            max_tokens=512,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=_build_messages(request),
        )
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    reply = response.content[0].text if response.content else ""
    detected_intent = _detect_intent(request.message)

    suggested_action = None
    if detected_intent == "appointment":
        suggested_action = "offer_booking"
    elif detected_intent == "emergency":
        suggested_action = "escalate_immediately"
    elif detected_intent == "complaint":
        suggested_action = "escalate_to_human"

    return ReceptionistChatResponse(
        response=reply,
        detected_intent=detected_intent,
        suggested_action=suggested_action,
    )


@router.post("/analyze-call/{call_id}", response_model=CallAnalysisResponse)
async def analyze_call(call_id: UUID):
    call = await db_service.get_call_log(str(call_id))
    if not call:
        raise HTTPException(status_code=404, detail="Call log not found")

    transcript = call.get("call_transcript", "")
    if not transcript:
        raise HTTPException(status_code=422, detail="Call has no transcript to analyze")

    prompt = (
        f"Analyze the following call transcript and respond with a JSON object containing:\n"
        f"- summary (string): a 1-2 sentence summary\n"
        f"- sentiment_score (float 0.0-1.0): 0 is very negative, 1 is very positive\n"
        f"- detected_intent (string): one of appointment, general_inquiry, complaint, emergency\n"
        f"- escalation_recommended (boolean): true if the call should be reviewed by a human\n"
        f"- escalation_reason (string or null): reason if escalation_recommended is true\n\n"
        f"Transcript:\n{transcript}\n\n"
        f"Respond with only valid JSON, no markdown."
    )

    try:
        response = await _client.messages.create(
            model=settings.model_name,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    raw = response.content[0].text if response.content else "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned invalid JSON during analysis")

    update_data = {
        "call_summary": parsed.get("summary"),
        "sentiment_score": parsed.get("sentiment_score"),
    }
    if parsed.get("escalation_recommended"):
        update_data["escalated_to_human"] = True
        update_data["escalation_reason"] = parsed.get("escalation_reason")

    await db_service.update_call_log(str(call_id), update_data)

    return CallAnalysisResponse(
        summary=parsed.get("summary", ""),
        sentiment_score=float(parsed.get("sentiment_score", 0.5)),
        detected_intent=parsed.get("detected_intent", "general_inquiry"),
        escalation_recommended=bool(parsed.get("escalation_recommended", False)),
        escalation_reason=parsed.get("escalation_reason"),
    )
