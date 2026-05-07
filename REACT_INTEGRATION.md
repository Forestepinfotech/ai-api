# React Frontend Integration Guide

## Overview

This guide shows how to integrate the AI Reception System API with a React frontend application.

## API Client Setup

### Install Dependencies

```bash
npm install axios react-query dotenv
```

### Create API Client (`src/services/api.ts`)

```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if needed
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Environment Configuration

Create `.env.local`:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

## Example Components

### Call History Component

```typescript
import { useQuery } from 'react-query';
import apiClient from '../services/api';

const CallHistory = ({ businessId }: { businessId: string }) => {
  const { data, isLoading, error } = useQuery(
    ['calls', businessId],
    () => apiClient.get(`/api/v1/calls/business/${businessId}`),
    { refetchInterval: 5000 } // Refresh every 5 seconds
  );

  if (isLoading) return <div>Loading calls...</div>;
  if (error) return <div>Error loading calls</div>;

  return (
    <div>
      {data?.data.map((call: any) => (
        <div key={call.id}>
          <p>Caller: {call.caller_name}</p>
          <p>Phone: {call.caller_phone}</p>
          <p>Status: {call.call_status}</p>
        </div>
      ))}
    </div>
  );
};

export default CallHistory;
```

### Appointment Booking Component

```typescript
import { useMutation } from 'react-query';
import apiClient from '../services/api';

const BookAppointment = ({ businessId }: { businessId: string }) => {
  const mutation = useMutation((appointmentData: any) =>
    apiClient.post(`/api/v1/appointments?business_id=${businessId}`, appointmentData)
  );

  const handleSubmit = async (formData: any) => {
    try {
      await mutation.mutateAsync(formData);
      alert('Appointment booked successfully!');
    } catch (error) {
      alert('Error booking appointment');
    }
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const formData = new FormData(e.currentTarget);
      handleSubmit(Object.fromEntries(formData));
    }}>
      <input name="customer_name" placeholder="Your Name" required />
      <input name="customer_phone" placeholder="Phone" required />
      <input name="appointment_date" type="date" required />
      <input name="appointment_time" type="time" required />
      <button type="submit" disabled={mutation.isLoading}>
        {mutation.isLoading ? 'Booking...' : 'Book Appointment'}
      </button>
    </form>
  );
};

export default BookAppointment;
```

### API Statistics Component

```typescript
import { useQuery } from 'react-query';
import apiClient from '../services/api';

const Statistics = ({ businessId }: { businessId: string }) => {
  const { data } = useQuery(
    ['call-stats', businessId],
    () => apiClient.get(`/api/v1/calls/business/${businessId}/summary`),
    { refetchInterval: 30000 }
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
      <Card title="Total Calls" value={data?.data.total_calls} />
      <Card title="Completed" value={data?.data.completed_calls} />
      <Card title="Escalated" value={data?.data.escalated_calls} />
      <Card title="Avg Sentiment" value={data?.data.avg_sentiment?.toFixed(2)} />
    </div>
  );
};

const Card = ({ title, value }: { title: string; value: any }) => (
  <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
    <h3>{title}</h3>
    <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{value}</p>
  </div>
);

export default Statistics;
```

## CORS Configuration for Production

The API currently allows all origins. For production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Testing API Integration

### Using REST Client Extension

Create `requests.http`:

```http
### Create Call Log
POST http://localhost:8000/api/v1/calls?business_id=550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "caller_phone": "555-1234",
  "caller_name": "John Doe",
  "call_status": "in_progress"
}

### Get Call Statistics
GET http://localhost:8000/api/v1/calls/business/550e8400-e29b-41d4-a716-446655440000/summary

### Create Appointment
POST http://localhost:8000/api/v1/appointments?business_id=550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "customer_name": "Jane Doe",
  "customer_phone": "555-5678",
  "customer_email": "jane@example.com",
  "appointment_date": "2024-12-25",
  "appointment_time": "14:30",
  "service_type": "Consultation"
}
```

## WebSocket Integration (Optional)

For real-time updates, consider using WebSockets:

```python
# In main.py
from fastapi import WebSocket

@app.websocket("/ws/calls/{business_id}")
async def websocket_endpoint(websocket: WebSocket, business_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process data and send updates
            await websocket.send_json({"status": "update", "data": data})
    except WebSocketDisconnect:
        pass
```

## Common Issues

### CORS Errors
- Ensure API is running on correct port
- Check browser console for exact error
- Verify allow_origins in FastAPI middleware

### 401/403 Errors
- Check authentication token in localStorage
- Verify API keys in .env file
- Check Supabase Row Level Security policies

### Network Errors
- Use browser DevTools Network tab
- Check API server logs
- Verify firewall/proxy settings

## Performance Tips

1. **Use React Query** for caching and synchronization
2. **Implement pagination** for large datasets
3. **Debounce search** inputs
4. **Use WebSockets** for real-time updates
5. **Optimize images** and assets

---

For more information, see the main [README.md](./README.md)
