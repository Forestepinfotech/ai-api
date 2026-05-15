"""
Vapi.ai Assistant Setup Script
Run once to create your AI receptionist assistant in Vapi.

Usage:
    python vapi_setup.py --business-id <your-business-uuid> --phone-number "+17809931330"

After running, copy the assistant_id and phone_number_id into your .env file.
"""

import argparse
import json
import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://ai-api-production-f36d.up.railway.app")
VAPI_BASE = "https://api.vapi.ai"

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
}


def create_assistant(business_id: str, business_name: str) -> dict:
    """Create the AI receptionist assistant in Vapi."""
    payload = {
        "name": f"{business_name} AI Receptionist",
        "firstMessage": f"Hello! Thank you for calling {business_name}. I'm your AI receptionist. How can I help you today?",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en",
        },
        "model": {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "temperature": 0.7,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a professional, warm AI receptionist for {business_name}. "
                        "Greet callers, answer questions about the clinic, and book appointments. "
                        "Always confirm appointment details before booking. "
                        "For emergencies, direct callers to call 911 immediately. "
                        f"business_id: {business_id}"
                    ),
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "check_availability",
                        "description": "Check available appointment slots for a given date.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "YYYY-MM-DD"}
                            },
                            "required": ["date"],
                        },
                    },
                    "server": {"url": f"{API_BASE_URL}/api/v1/vapi/webhook"},
                },
                {
                    "type": "function",
                    "function": {
                        "name": "book_appointment",
                        "description": "Book a confirmed appointment for the caller.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_name": {"type": "string"},
                                "appointment_date": {"type": "string", "description": "YYYY-MM-DD"},
                                "appointment_time": {"type": "string", "description": "HH:MM 24h"},
                                "service_type": {"type": "string"},
                                "special_requests": {"type": "string"},
                            },
                            "required": ["customer_name", "appointment_date", "appointment_time", "service_type"],
                        },
                    },
                    "server": {"url": f"{API_BASE_URL}/api/v1/vapi/webhook"},
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_business_info",
                        "description": "Get clinic name, address, phone, and email.",
                        "parameters": {"type": "object", "properties": {}, "required": []},
                    },
                    "server": {"url": f"{API_BASE_URL}/api/v1/vapi/webhook"},
                },
            ],
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "stability": 0.5,
            "similarityBoost": 0.75,
            "optimizeStreamingLatency": 3,
        },
        "endCallMessage": "Thank you for calling. Have a wonderful day! Goodbye.",
        "endCallPhrases": ["goodbye", "bye", "thank you bye", "that's all"],
        "silenceTimeoutSeconds": 10,
        "maxDurationSeconds": 600,
        "serverUrl": f"{API_BASE_URL}/api/v1/vapi/webhook",
        "serverUrlSecret": os.getenv("VAPI_WEBHOOK_SECRET", ""),
        "metadata": {"business_id": business_id},
    }

    resp = httpx.post(f"{VAPI_BASE}/assistant", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def import_phone_number(phone_number: str, assistant_id: str) -> dict:
    """
    Import an existing phone number into Vapi (for Twilio/your own number).
    If you want Vapi to provision a new number, use buy_phone_number() instead.
    """
    payload = {
        "provider": "twilio",  # change to your provider if different
        "number": phone_number,
        "assistantId": assistant_id,
        "name": "Clinic Main Line",
        "serverUrl": f"{API_BASE_URL}/api/v1/vapi/webhook",
    }
    resp = httpx.post(f"{VAPI_BASE}/phone-number", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def buy_phone_number(area_code: str, assistant_id: str) -> dict:
    """Buy a new Vapi-provisioned phone number."""
    payload = {
        "provider": "vapi",
        "areaCode": area_code,
        "assistantId": assistant_id,
        "name": "Clinic Main Line",
    }
    resp = httpx.post(f"{VAPI_BASE}/phone-number", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Set up Vapi AI receptionist")
    parser.add_argument("--business-id", required=True, help="Business UUID from Supabase")
    parser.add_argument("--business-name", default="our clinic", help="Clinic display name")
    parser.add_argument("--phone-number", help="Existing phone number to import (e.g. +17809931330)")
    parser.add_argument("--buy-area-code", help="Area code to buy a new Vapi number (e.g. 780)")
    args = parser.parse_args()

    if not VAPI_API_KEY:
        print("ERROR: VAPI_API_KEY not set in .env")
        sys.exit(1)

    print(f"Creating Vapi assistant for: {args.business_name} (business_id: {args.business_id})")
    assistant = create_assistant(args.business_id, args.business_name)
    assistant_id = assistant["id"]
    print(f"  Assistant created: {assistant_id}")

    if args.phone_number:
        print(f"Importing phone number: {args.phone_number}")
        phone = import_phone_number(args.phone_number, assistant_id)
        print(f"  Phone number ID: {phone['id']}")
    elif args.buy_area_code:
        print(f"Buying a new number with area code: {args.buy_area_code}")
        phone = buy_phone_number(args.buy_area_code, assistant_id)
        print(f"  Phone number: {phone.get('number')}  ID: {phone['id']}")
    else:
        print("  No phone number configured — add one later in the Vapi dashboard.")
        phone = {}

    print("\n" + "="*60)
    print("Add these to your .env file:")
    print(f"  VAPI_ASSISTANT_ID={assistant_id}")
    if phone:
        print(f"  VAPI_PHONE_NUMBER_ID={phone.get('id', '')}")
    print("="*60)


if __name__ == "__main__":
    main()
