# AI Reception System API

A production-ready FastAPI application for managing AI-powered business reception calls, appointments, and customer interactions with Supabase integration.

## 🎯 Features

- **FastAPI with Swagger/OpenAPI** - Auto-generated interactive API documentation
- **Supabase Integration** - PostgreSQL database with row-level security
- **Call Management** - Track, analyze, and manage incoming/outgoing calls
- **Appointment Scheduling** - Create and manage business appointments
- **AI Integration** - Ready for OpenAI/LangChain integration
- **CORS Enabled** - Ready for cross-origin requests
- **Environment Management** - Secure credentials with .env configuration
- **Comprehensive Logging** - Detailed error tracking and monitoring

## 📋 Prerequisites

- Python 3.9+
- pip or poetry
- Supabase account with credentials

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Clone and navigate to project
cd "e:\AI Project\api"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

**CRITICAL: Regenerate your Supabase keys immediately**

Your previous keys were exposed. Follow these steps:

1. Go to your Supabase dashboard: https://app.supabase.com
2. Navigate to Project Settings → API Keys
3. Copy your new **Anon Public** key
4. Copy your new **Service Role** key (keep this secret!)
5. Update `.env` file:

```bash
SUPABASE_URL=https://ephekrkexdxstkiawetk.supabase.co
SUPABASE_ANON_KEY=your_new_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_new_service_role_key_here
OPENAI_API_KEY=sk-your-key-here  # If using OpenAI
```

### 4. Run the API Server

```bash
# Development mode (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access Swagger Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📁 Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment settings
├── models.py              # Pydantic models for request/response
├── database.py            # Supabase service layer
├── routers/
│   ├── calls.py          # Call management endpoints
│   └── appointments.py    # Appointment management endpoints
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (never commit!)
├── .env.example          # Template for .env
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Calls
```
POST   /api/v1/calls                    # Create call log
GET    /api/v1/calls/{call_id}         # Get call details
PUT    /api/v1/calls/{call_id}         # Update call
GET    /api/v1/calls/business/{business_id}  # Get all calls
GET    /api/v1/calls/business/{business_id}/summary  # Call statistics
```

### Appointments
```
POST   /api/v1/appointments                          # Create appointment
GET    /api/v1/appointments/{appointment_id}        # Get appointment
PUT    /api/v1/appointments/{appointment_id}        # Update appointment
GET    /api/v1/appointments/business/{business_id}  # Get all appointments
GET    /api/v1/appointments/business/{business_id}/upcoming  # Get upcoming
```

## 🔒 Security Best Practices

### Environment Variables
- **Never commit** `.env` file to git
- `.gitignore` already excludes it
- Always use `.env.example` as template
- Rotate credentials regularly

### API Keys
- Service role key: Only for backend/server operations
- Anon key: For frontend/client applications
- Enable Row Level Security (RLS) in Supabase
- Use API key scopes appropriately

### CORS Configuration
- Current setup allows all origins for development
- In production, specify allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🤖 Integration Examples

### Using with OpenAI

```python
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.openai_api_key)

async def analyze_call(transcript: str):
    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[{"role": "user", "content": f"Analyze: {transcript}"}],
        temperature=settings.temperature
    )
    return response.choices[0].message.content
```

### Database Queries

```python
# In routers or service modules
from database import db_service

# Get call logs
calls = await db_service.get_business_call_logs(business_id)

# Create appointment
appointment = await db_service.create_appointment(
    business_id,
    {"customer_name": "John", "customer_phone": "555-1234", ...}
)
```

## 📊 Database Schema

The API uses these main tables:

- `businesses` - Business accounts
- `users` - User accounts with roles
- `call_logs` - Recorded call information
- `appointments` - Scheduled appointments
- `faqs` - Frequently asked questions
- `api_keys` - API key management
- `audit_logs` - Activity logging
- `notifications` - User notifications

See the schema in your Supabase dashboard for complete details.

## 🧪 Testing

```bash
# Using curl
curl -X GET http://localhost:8000/health

# Using Python requests
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())

# Create a call log
curl -X POST http://localhost:8000/api/v1/calls \
  -H "Content-Type: application/json" \
  -d '{"business_id":"uuid", "caller_phone":"555-1234", ...}'
```

## 📝 Adding New Endpoints

1. Create models in `models.py`:
```python
class NewItemCreate(BaseModel):
    field1: str
    field2: Optional[int] = None
```

2. Add database methods in `database.py`

3. Create router in `routers/new_feature.py`:
```python
from fastapi import APIRouter
from models import NewItemCreate

router = APIRouter(prefix="/api/v1/items", tags=["Items"])

@router.post("/")
async def create_item(item: NewItemCreate):
    # Implementation
    pass
```

4. Include router in `main.py`:
```python
from routers import new_feature
app.include_router(new_feature.router)
```

## 🐛 Troubleshooting

### Connection Issues
- Verify Supabase URL and keys in `.env`
- Check network connectivity to Supabase
- Ensure database tables exist

### Import Errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)
- Activate virtual environment

### Port Already in Use
```bash
# Change port in command
python main.py --port 8001
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 🤝 Contributing

1. Create feature branch
2. Follow PEP 8 style guide
3. Add docstrings to functions
4. Test endpoints with Swagger UI
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Important Notes

- **API Keys**: The Supabase keys you shared in the chat are now compromised and have been regenerated
- **Development Only**: CORS is set to allow all origins for development. Restrict in production
- **Environment Variables**: Always use .env files for sensitive data
- **Database Constraints**: Review the schema for validation rules and constraints

## 🆘 Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review error logs in terminal
3. Consult Supabase documentation
4. Check FastAPI best practices

---

**Last Updated**: May 6, 2026
**Version**: 1.0.0
