"""
Vapi.ai webhook router
Handles incoming voice call events: assistant-request, tool-calls, end-of-call-report
"""

import json
import logging
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Request

from database import db_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vapi",
    tags=["Vapi Voice"],
)

# ── Webhook entry point ────────────────────────────────────────────────────────

@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Single endpoint that receives all Vapi call lifecycle events.
    Vapi Server URL in your dashboard should point here.
    """
    body = await request.json()
    message = body.get("message", {})
    event_type = message.get("type", "")

    logger.info(f"Vapi event received: {event_type}")

    if event_type == "assistant-request":
        return await _handle_assistant_request(message)

    if event_type == "status-update":
        return await _handle_status_update(message)

    if event_type == "tool-calls":
        return await _handle_tool_calls(message)

    if event_type == "end-of-call-report":
        return await _handle_end_of_call(message)

    return {"status": "ok"}


# ── Event handlers ─────────────────────────────────────────────────────────────

async def _handle_assistant_request(message: dict) -> dict:
    """
    Vapi calls this when a new call arrives and needs to know which assistant to use.
    We look up the business by the called phone number and return a custom config.
    """
    call = message.get("call", {})
    called_number = call.get("phoneNumber", {}).get("number", "")
    caller_number = call.get("customer", {}).get("number", "unknown")

    business = await db_service.get_business_by_phone(called_number)

    if business:
        business_id = str(business["id"])
        business_name = business.get("business_name", "the clinic")
        greeting = (
            business.get("ai_greeting_message")
            or f"Hello! Thank you for calling {business_name}. I'm your AI receptionist. How can I help you today?"
        )
    else:
        business_id = getattr(settings, "default_business_id", "")
        business_name = "the clinic"
        greeting = "Hello! Thank you for calling. I'm your AI receptionist. How can I help you today?"

    return {
        "assistant": _build_assistant_config(business_id, business_name, greeting, caller_number)
    }


async def _handle_status_update(message: dict) -> dict:
    """Log call when it moves to in-progress."""
    status = message.get("status", "")
    if status != "in-progress":
        return {"status": "ok"}

    call = message.get("call", {})
    caller_phone = call.get("customer", {}).get("number", "unknown")
    vapi_call_id = call.get("id", "")
    business_id = _extract_business_id(call)

    if business_id:
        try:
            await db_service.create_call_log(business_id, {
                "caller_phone": caller_phone,
                "call_status": "in_progress",
                "external_call_id": vapi_call_id,
            })
        except Exception as e:
            logger.error(f"Error logging call start: {e}")

    return {"status": "ok"}


async def _handle_tool_calls(message: dict) -> dict:
    """Execute tool functions the AI requested (book appointment, check availability, etc.)."""
    call = message.get("call", {})
    caller_phone = call.get("customer", {}).get("number", "")
    business_id = _extract_business_id(call)
    tool_call_list = message.get("toolCallList", [])

    results = []
    for tool_call in tool_call_list:
        tool_id = tool_call.get("id")
        fn = tool_call.get("function", {})
        tool_name = fn.get("name", "")
        raw_args = fn.get("arguments", "{}")
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

        result = await _execute_tool(tool_name, args, business_id, caller_phone)
        results.append({
            "toolCallId": tool_id,
            "result": json.dumps(result),
        })

    return {"results": results}


async def _handle_end_of_call(message: dict) -> dict:
    """Update the call log with transcript, summary, and duration when the call ends."""
    call = message.get("call", {})
    vapi_call_id = call.get("id", "")
    transcript = message.get("transcript", "")
    summary = message.get("summary", "")
    duration = int(message.get("durationSeconds") or 0)

    if vapi_call_id:
        try:
            await db_service.update_call_log_by_external_id(vapi_call_id, {
                "call_status": "completed",
                "call_transcript": transcript,
                "call_summary": summary,
                "call_duration_seconds": duration,
            })
        except Exception as e:
            logger.error(f"Error updating call end: {e}")

    return {"status": "ok"}


# ── Tool execution ─────────────────────────────────────────────────────────────

async def _execute_tool(tool_name: str, args: dict, business_id: str, caller_phone: str) -> dict:
    if tool_name == "check_availability":
        return await _tool_check_availability(args, business_id)

    if tool_name == "book_appointment":
        return await _tool_book_appointment(args, business_id, caller_phone)

    if tool_name == "get_business_info":
        return await _tool_get_business_info(business_id)

    return {"error": f"Unknown tool: {tool_name}"}


async def _tool_check_availability(args: dict, business_id: str) -> dict:
    check_date = args.get("date", str(date.today() + timedelta(days=1)))
    try:
        appointments = await db_service.list_appointments(business_id, limit=500)
        booked = {
            a.get("appointment_time")
            for a in appointments
            if a.get("appointment_date") == check_date
            and a.get("status") in ("scheduled", "confirmed")
        }
        # 9 AM – 5 PM, every 30 minutes
        all_slots = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0, 30)]
        available = [s for s in all_slots if s not in booked][:6]

        if not available:
            return {"available": False, "date": check_date, "slots": [], "message": f"No slots available on {check_date}."}

        return {
            "available": True,
            "date": check_date,
            "slots": available,
            "message": f"Available times on {check_date}: {', '.join(available)}",
        }
    except Exception as e:
        logger.error(f"check_availability error: {e}")
        return {"available": False, "message": "Could not check availability right now."}


async def _tool_book_appointment(args: dict, business_id: str, caller_phone: str) -> dict:
    try:
        appt_date = args.get("appointment_date", "")
        appt_time = args.get("appointment_time", "")
        result = await db_service.create_appointment(business_id, {
            "customer_name": args.get("customer_name"),
            "customer_phone": caller_phone or args.get("customer_phone", ""),
            "customer_email": args.get("customer_email"),
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "appointment_datetime": f"{appt_date}T{appt_time}:00Z",
            "service_type": args.get("service_type", "General Consultation"),
            "duration_minutes": args.get("duration_minutes", 30),
            "special_requests": args.get("special_requests"),
            "status": "scheduled",
        })
        return {
            "success": True,
            "appointment_id": str(result.get("id", "")),
            "message": (
                f"Appointment confirmed for {args.get('customer_name')} "
                f"on {appt_date} at {appt_time}. "
                "You will receive a confirmation shortly."
            ),
        }
    except Exception as e:
        logger.error(f"book_appointment error: {e}")
        return {"success": False, "message": "I was unable to book the appointment. Please call back or try again."}


async def _tool_get_business_info(business_id: str) -> dict:
    try:
        business = await db_service.get_business(business_id)
        if not business:
            return {"error": "Business not found"}
        address = ", ".join(filter(None, [
            business.get("address_line1"),
            business.get("city"),
            business.get("state"),
            business.get("postal_code"),
        ]))
        return {
            "name": business.get("business_name"),
            "phone": business.get("phone_number"),
            "email": business.get("email"),
            "address": address,
            "timezone": business.get("timezone", "America/Edmonton"),
        }
    except Exception as e:
        logger.error(f"get_business_info error: {e}")
        return {"error": "Could not retrieve clinic information"}


# ── Assistant config builder ───────────────────────────────────────────────────

def _build_assistant_config(business_id: str, business_name: str, greeting: str, caller_phone: str) -> dict:
    """Build a full Vapi assistant config for a specific business."""
    return {
        "name": f"{business_name} AI Receptionist",
        "firstMessage": greeting,
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en",
        },
        "model": {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "messages": [
                {
                    "role": "system",
                    "content": _build_system_prompt(business_id, business_name, caller_phone),
                }
            ],
            "tools": _get_tools(),
            "temperature": 0.7,
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel — professional, warm female voice
            "stability": 0.5,
            "similarityBoost": 0.75,
            "optimizeStreamingLatency": 3,
        },
        "endCallMessage": "Thank you for calling. Have a wonderful day! Goodbye.",
        "endCallPhrases": ["goodbye", "bye", "thank you bye", "that's all", "no that's all"],
        "silenceTimeoutSeconds": 10,
        "maxDurationSeconds": 600,
        "metadata": {"business_id": business_id},
    }


def _build_system_prompt(business_id: str, business_name: str, caller_phone: str) -> str:
    return f"""You are a professional, warm AI receptionist for {business_name}.
The caller's phone number is {caller_phone}.
Your business_id for tool calls is: {business_id}

Your responsibilities:
1. Greet the caller warmly and find out why they are calling
2. Answer general questions about the clinic (hours, services, location) using get_business_info
3. Book appointments by collecting: full name, preferred date and time, reason for visit
4. Before booking, always confirm: "Just to confirm — [name], [date] at [time] for [reason]. Is that correct?"
5. For emergencies say: "This sounds urgent — please call 911 or go to your nearest emergency room immediately."

Conversation style:
- Sound like a real, friendly human receptionist — never robotic
- One question at a time, never overwhelm the caller
- Short, natural sentences. Use contractions (I'll, you're, that's)
- If asked if you are an AI, say you are a virtual receptionist assistant
- Today's date is {date.today().strftime("%A, %B %d, %Y")}

When booking an appointment:
- Use check_availability to confirm slots before offering them
- Dates must be in YYYY-MM-DD format, times in HH:MM (24-hour)
- Collect service_type (reason for visit)"""


def _get_tools() -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": "check_availability",
                "description": "Check available appointment slots for a given date. Always call this before offering a time to the caller.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date to check in YYYY-MM-DD format",
                        }
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Book a confirmed appointment for the caller after they have agreed to the time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "Full name of the patient"},
                        "appointment_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                        "appointment_time": {"type": "string", "description": "Time in HH:MM 24-hour format"},
                        "service_type": {"type": "string", "description": "Reason for visit or type of appointment"},
                        "special_requests": {"type": "string", "description": "Any special notes from the caller"},
                    },
                    "required": ["customer_name", "appointment_date", "appointment_time", "service_type"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_business_info",
                "description": "Get clinic name, address, phone, and email. Use when caller asks about location or contact info.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_business_id(call: dict) -> Optional[str]:
    return (call.get("metadata") or {}).get("business_id")
