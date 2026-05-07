"""
Database models for AI Reception System
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

# Enums for status types
class CallStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    no_answer = "no_answer"

class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    rescheduled = "rescheduled"

class SubscriptionPlan(str, Enum):
    trial = "trial"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"
    client = "client"

class Industry(str, Enum):
    healthcare = "healthcare"
    legal = "legal"
    real_estate = "real_estate"
    hospitality = "hospitality"
    retail = "retail"
    other = "other"

# Business Models
class BusinessBase(BaseModel):
    business_name: str
    industry: Industry
    email: EmailStr
    phone_number: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: str = "America/Edmonton"
    subscription_plan: SubscriptionPlan = SubscriptionPlan.trial
    monthly_call_limit: int = 500

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    timezone: Optional[str] = None
    ai_greeting_message: Optional[str] = None

class BusinessResponse(BusinessBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

# Call Log Models
class CallLogCreate(BaseModel):
    caller_phone: str
    caller_name: Optional[str] = None
    call_status: CallStatus = CallStatus.in_progress
    detected_intent: Optional[str] = None

class CallLogUpdate(BaseModel):
    call_status: Optional[CallStatus] = None
    call_transcript: Optional[str] = None
    call_summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    escalated_to_human: Optional[bool] = None
    escalation_reason: Optional[str] = None

class CallLogResponse(BaseModel):
    id: UUID
    business_id: UUID
    caller_phone: str
    caller_name: Optional[str]
    call_status: CallStatus
    call_duration_seconds: Optional[int]
    call_transcript: Optional[str]
    call_summary: Optional[str]
    sentiment_score: Optional[float]
    escalated_to_human: Optional[bool]
    escalation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

# Appointment Models
class AppointmentCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    appointment_date: str  # YYYY-MM-DD
    appointment_time: str  # HH:MM
    service_type: Optional[str] = None
    duration_minutes: int = 30
    special_requests: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    cancellation_reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: UUID
    business_id: UUID
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    appointment_date: str
    appointment_time: str
    status: AppointmentStatus
    duration_minutes: int
    created_at: datetime
    updated_at: datetime

# API Key Models
class APIKeyCreate(BaseModel):
    business_id: UUID
    key_name: str
    scopes: List[str] = Field(default=["read"])
    expires_at: Optional[datetime] = None

class APIKeyUpdate(BaseModel):
    key_name: Optional[str] = None
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class APIKeyResponse(BaseModel):
    id: UUID
    business_id: UUID
    key_name: str
    api_key_prefix: str
    scopes: List[str]
    last_used_at: Optional[datetime]
    usage_count: int
    is_active: bool
    created_at: datetime

# User Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    role: UserRole
    last_login_at: Optional[datetime]
    is_active: bool
    created_at: datetime

# FAQ Models
class FAQCreate(BaseModel):
    business_id: UUID
    question: str
    answer: str
    category: Optional[str] = None
    display_order: int = 0

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    display_order: Optional[int] = None

class FAQResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    category: Optional[str]
    display_order: int
    times_asked: int
    created_at: datetime

# Notification Models
class NotificationCreate(BaseModel):
    user_id: Optional[UUID] = None
    title: str
    message: str
    notification_type: str = "info"

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    notification_type: str
    user_id: Optional[UUID]
    is_read: bool
    created_at: datetime

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[str] = None
    is_read: Optional[bool] = None

class BusinessHoursCreate(BaseModel):
    business_id: UUID
    day_of_week: str
    open_time: str
    close_time: str
    is_closed: bool = False

class BusinessHoursUpdate(BaseModel):
    day_of_week: Optional[str] = None
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_closed: Optional[bool] = None

class BusinessHoursResponse(BaseModel):
    id: UUID
    business_id: UUID
    day_of_week: str
    open_time: str
    close_time: str
    is_closed: bool
    created_at: datetime
    updated_at: datetime

class BusinessUserCreate(BaseModel):
    business_id: UUID
    user_id: UUID
    role: UserRole = UserRole.user
    is_active: bool = True

class BusinessUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class BusinessUserResponse(BaseModel):
    id: UUID
    business_id: UUID
    user_id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AuditLogCreate(BaseModel):
    business_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    event_type: str
    details: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: UUID
    business_id: Optional[UUID]
    user_id: Optional[UUID]
    event_type: str
    details: Optional[str]
    created_at: datetime

# Auth Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

# AI Receptionist Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ReceptionistChatRequest(BaseModel):
    business_id: UUID
    message: str
    conversation_history: List[ChatMessage] = []
    caller_phone: Optional[str] = None

class ReceptionistChatResponse(BaseModel):
    response: str
    detected_intent: Optional[str] = None
    suggested_action: Optional[str] = None

class CallAnalysisResponse(BaseModel):
    summary: str
    sentiment_score: float
    detected_intent: str
    escalation_recommended: bool
    escalation_reason: Optional[str] = None
