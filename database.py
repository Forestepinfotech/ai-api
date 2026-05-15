"""
Database service for Supabase integration
Handles all database operations
"""

from supabase import create_client, Client
from config import settings
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase database operations"""

    _instance: Optional["SupabaseService"] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass  # lazy init — client created on first use

    def _get_client(self) -> Client:
        if self._client is None:
            url = settings.supabase_url
            key = settings.supabase_service_role_key
            if not url or not key:
                raise RuntimeError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set "
                    "in environment variables."
                )
            self._client = create_client(url, key)
            logger.info("Supabase client initialized")
        return self._client

    @property
    def client(self) -> Client:
        return self._get_client()

    def _execute(self, builder):
        response = builder.execute()
        return response.data

    async def _select_one(
        self,
        table: str,
        filters: Dict[str, Any],
        columns: str = "*"
    ) -> Optional[Dict[str, Any]]:
        builder = self.client.table(table).select(columns)
        for key, value in filters.items():
            if value is not None:
                builder = builder.eq(key, value)
        data = self._execute(builder)
        return data[0] if data else None

    async def _select_many(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: bool = False,
    ) -> List[Dict[str, Any]]:
        builder = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                if value is not None:
                    builder = builder.eq(key, value)
        if order_by:
            builder = builder.order(order_by, desc=desc)
        if limit is not None and offset is not None:
            builder = builder.range(offset, offset + limit - 1)
        elif limit is not None:
            builder = builder.limit(limit)
        return self._execute(builder) or []

    async def _insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        builder = self.client.table(table).insert(data)
        result = self._execute(builder)
        return result[0] if result else None

    async def _update(self, table: str, object_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not data:
            return await self._select_one(table, {"id": object_id})
        builder = self.client.table(table).update(data).eq("id", object_id)
        result = self._execute(builder)
        return result[0] if result else None

    async def _delete(self, table: str, object_id: str, soft_delete: bool = True) -> Optional[Dict[str, Any]]:
        if soft_delete:
            return await self._update(table, object_id, {"is_active": False})
        builder = self.client.table(table).delete().eq("id", object_id)
        result = self._execute(builder)
        return result[0] if result else None

    async def _create_record(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._insert(table, data)

    async def _get_record(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        return await self._select_one(table, {"id": record_id})

    async def _list_records(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        desc: bool = False,
    ) -> List[Dict[str, Any]]:
        return await self._select_many(
            table,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
        )

    # Business operations
    async def create_business(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("businesses", data)

    async def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("businesses", business_id)

    async def list_businesses(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return await self._list_records("businesses", order_by="created_at", limit=limit, offset=offset)

    async def update_business(self, business_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("businesses", business_id, data)

    async def delete_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("businesses", business_id)

    # User operations
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self._select_one("users", {"email": email})

    async def create_user(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("users", data)

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("users", user_id)

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return await self._list_records("users", order_by="created_at", limit=limit, offset=offset)

    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("users", user_id, data)

    async def delete_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("users", user_id)

    # Business hours operations
    async def create_business_hours(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("business_hours", data)

    async def get_business_hours(self, hours_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("business_hours", hours_id)

    async def list_business_hours(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "business_hours",
            filters={"business_id": business_id},
            order_by="day_of_week",
            limit=limit,
            offset=offset,
        )

    async def update_business_hours(self, hours_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("business_hours", hours_id, data)

    async def delete_business_hours(self, hours_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("business_hours", hours_id)

    # Business user operations
    async def create_business_user(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("business_users", data)

    async def get_business_user(self, business_user_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("business_users", business_user_id)

    async def list_business_users(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "business_users",
            filters={"business_id": business_id},
            order_by="created_at",
            limit=limit,
            offset=offset,
        )

    async def update_business_user(self, business_user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("business_users", business_user_id, data)

    async def delete_business_user(self, business_user_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("business_users", business_user_id)

    # Call log operations
    async def create_call_log(self, business_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("call_logs", {"business_id": business_id, **data})

    async def get_call_log(self, call_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("call_logs", call_id)

    async def update_call_log(self, call_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("call_logs", call_id, data)

    async def get_business_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        return await self._select_one("businesses", {"phone_number": phone_number})

    async def update_call_log_by_external_id(self, external_call_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        builder = self.client.table("call_logs").update(data).eq("external_call_id", external_call_id)
        result = self._execute(builder)
        return result[0] if result else None

    async def get_business_call_logs(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._select_many(
            "call_logs",
            filters={"business_id": business_id},
            order_by="created_at",
            limit=limit,
            offset=offset,
            desc=True,
        )

    # Appointment operations
    async def create_appointment(self, business_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("appointments", {"business_id": business_id, **data})

    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("appointments", appointment_id)

    async def list_appointments(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "appointments",
            filters={"business_id": business_id},
            order_by="appointment_datetime",
            limit=limit,
            offset=offset,
        )

    async def update_appointment(self, appointment_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("appointments", appointment_id, data)

    async def delete_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("appointments", appointment_id)

    # FAQ operations
    async def create_faq(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("faqs", data)

    async def get_faq(self, faq_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("faqs", faq_id)

    async def list_faqs(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "faqs",
            filters={"business_id": business_id},
            order_by="display_order",
            limit=limit,
            offset=offset,
        )

    async def update_faq(self, faq_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("faqs", faq_id, data)

    async def delete_faq(self, faq_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("faqs", faq_id)

    # Notification operations
    async def create_notification(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("notifications", data)

    async def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("notifications", notification_id)

    async def list_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "notifications",
            filters={"user_id": user_id},
            order_by="created_at",
            limit=limit,
            offset=offset,
        )

    async def update_notification(self, notification_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("notifications", notification_id, data)

    async def delete_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("notifications", notification_id)

    # API key operations
    async def create_api_key(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if "api_key_prefix" not in data or not data.get("api_key_prefix"):
            data["api_key_prefix"] = data.get("key_name", "")[:8]
        return await self._create_record("api_keys", data)

    async def get_api_key(self, api_key_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("api_keys", api_key_id)

    async def list_api_keys(
        self,
        business_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await self._list_records(
            "api_keys",
            filters={"business_id": business_id},
            order_by="created_at",
            limit=limit,
            offset=offset,
        )

    async def update_api_key(self, api_key_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._update("api_keys", api_key_id, data)

    async def delete_api_key(self, api_key_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("api_keys", api_key_id)

    # Audit log operations
    async def create_audit_log(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self._create_record("audit_logs", data)

    async def get_audit_log(self, audit_log_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_record("audit_logs", audit_log_id)

    async def list_audit_logs(
        self,
        business_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        filters: Optional[Dict[str, Any]] = None
        if business_id:
            filters = {"business_id": business_id}
        return await self._list_records(
            "audit_logs",
            filters=filters,
            order_by="created_at",
            limit=limit,
            offset=offset,
        )

    async def delete_audit_log(self, audit_log_id: str) -> Optional[Dict[str, Any]]:
        return await self._delete("audit_logs", audit_log_id, soft_delete=False)

# Singleton instance

db_service = SupabaseService()
