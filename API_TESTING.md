# Travel Suite - API Testing Guide

## 🚀 Quick Start

**Server Status**: ✅ Running on `http://localhost:8000`

## 🔐 Authentication

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "password2": "SecurePass123",
    "phone_number": "254712345678",
    "national_id": "ID12345",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response**:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "phone_number": "254712345678"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**Save the access token for API requests**:
```bash
export TOKEN="your_access_token_here"
```

## 📊 CRUD Operations

### Customers

**Create a Customer**:
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "phone_number": "254700123456",
    "national_id": "ID987654",
    "address": "Kigali, Rwanda"
  }'
```

**Get All Customers**:
```bash
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN"
```

**Get Specific Customer**:
```bash
curl -X GET http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN"
```

**Update Customer**:
```bash
curl -X PATCH http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Nyanza, Rwanda"
  }'
```

**Delete Customer**:
```bash
curl -X DELETE http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### Routes

**Create a Route**:
```bash
curl -X POST http://localhost:8000/api/routes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Kigali",
    "destination": "Butare",
    "departure_time": "08:00:00",
    "arrival_time": "11:00:00",
    "stops": "Muhanga, Rwamagana",
    "fare": "5000.00"
  }'
```

**Get All Routes**:
```bash
curl -X GET http://localhost:8000/api/routes/ \
  -H "Authorization: Bearer $TOKEN"
```

**Check Available Seats for Route**:
```bash
curl -X GET http://localhost:8000/api/routes/1/available_seats/ \
  -H "Authorization: Bearer $TOKEN"
```

### Vehicles

**Create a Vehicle**:
```bash
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "RAJ-123-A",
    "route": 1,
    "capacity": 50,
    "status": "Available"
  }'
```

**Get Vehicle Seats**:
```bash
curl -X GET http://localhost:8000/api/vehicles/1/seats/ \
  -H "Authorization: Bearer $TOKEN"
```

### Seats

**Create Seats for a Vehicle**:
```bash
curl -X POST http://localhost:8000/api/seats/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "seat_number": "A1",
    "is_booked": false
  }'
```

**Book a Seat**:
```bash
curl -X POST http://localhost:8000/api/seats/1/book/ \
  -H "Authorization: Bearer $TOKEN"
```

**Unbook a Seat**:
```bash
curl -X POST http://localhost:8000/api/seats/1/unbook/ \
  -H "Authorization: Bearer $TOKEN"
```

### Bookings

**Create a Booking**:
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 1,
    "route": 1,
    "seat_number": "A1",
    "amount": "5000.00",
    "date": "2025-11-20",
    "status": "Pending"
  }'
```

**Get All Bookings**:
```bash
curl -X GET http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer $TOKEN"
```

**Confirm Booking**:
```bash
curl -X POST http://localhost:8000/api/bookings/1/confirm/ \
  -H "Authorization: Bearer $TOKEN"
```

**Cancel Booking**:
```bash
curl -X POST http://localhost:8000/api/bookings/1/cancel/ \
  -H "Authorization: Bearer $TOKEN"
```

### Payments

**Create a Payment**:
```bash
curl -X POST http://localhost:8000/api/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking": 1,
    "amount": "5000.00",
    "payment_method": "Card",
    "status": "Pending"
  }'
```

**Process Payment**:
```bash
curl -X POST http://localhost:8000/api/payments/1/process_payment/ \
  -H "Authorization: Bearer $TOKEN"
```

### Tickets

**Create a Ticket**:
```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking": 1
  }'
```

**Validate Ticket by QR Code**:
```bash
curl -X POST http://localhost:8000/api/tickets/validate_ticket/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "qr_code": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

## 🌐 WebSocket Testing

### Bus Location Updates

Connect to WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/bus-location/');

// Send bus location
ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'bus_location',
        bus_id: 1,
        location: {
            lat: -1.9466,
            lng: 29.8739
        },
        timestamp: new Date().toISOString()
    }));
};

// Receive location updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Bus Location:', data);
};
```

### Notifications

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    console.log('Notification:', notification);
};
```

## 📱 Frontend Integration Example

### JavaScript/Fetch

```javascript
const API_BASE = 'http://localhost:8000/api';
let accessToken = null;

// Register
async function register(userData) {
    const res = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    const data = await res.json();
    accessToken = data.access;
    localStorage.setItem('token', accessToken);
    return data;
}

// Get Customers
async function getCustomers() {
    const res = await fetch(`${API_BASE}/customers/`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    return await res.json();
}

// Create Booking
async function createBooking(bookingData) {
    const res = await fetch(`${API_BASE}/bookings/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    });
    return await res.json();
}
```

## 🧪 Testing with Postman

1. **Create Environment Variables**:
   - `BASE_URL`: `http://localhost:8000`
   - `TOKEN`: (Get from login/register response)

2. **Import Endpoints**: Use the curl commands above in Postman

3. **Authorization**: Add `Bearer ${TOKEN}` to Authorization header

## 🐛 Common Issues

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Token expired or invalid. Re-login. |
| 404 Not Found | Check the resource ID or endpoint path. |
| 400 Bad Request | Validate JSON format and required fields. |
| 500 Server Error | Check Django console for detailed error. |

## 🔄 Server Management

```bash
# Restart server
python manage.py runserver

# Create new migrations
python manage.py makemigrations core

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Check database
sqlite3 db.sqlite3
```

---

**Happy Testing!** 🎉
