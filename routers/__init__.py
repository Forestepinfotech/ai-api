"""Routers package for AI Reception System"""

from .appointments import router as appointments_router
from .api_keys import router as api_keys_router
from .audit_logs import router as audit_logs_router
from .auth import router as auth_router
from .ai_receptionist import router as ai_receptionist_router
from .business_hours import router as business_hours_router
from .business_users import router as business_users_router
from .businesses import router as businesses_router
from .calls import router as calls_router
from .faqs import router as faqs_router
from .notifications import router as notifications_router
from .users import router as users_router

all_routers = [
    auth_router,
    businesses_router,
    users_router,
    business_hours_router,
    business_users_router,
    calls_router,
    appointments_router,
    faqs_router,
    notifications_router,
    api_keys_router,
    audit_logs_router,
    ai_receptionist_router,
]
