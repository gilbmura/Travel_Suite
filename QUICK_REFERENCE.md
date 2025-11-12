# 🚀 Quick Reference - Travel Suite Backend

## ⚡ Quick Start

**Server Status**: ✅ Running on `http://localhost:8000`

```bash
# API endpoints
GET/POST  http://localhost:8000/api/customers/
GET/POST  http://localhost:8000/api/routes/
GET/POST  http://localhost:8000/api/bookings/
GET/POST  http://localhost:8000/api/payments/

# Admin panel
http://localhost:8000/admin/
Username: admin
Password: admin123
```

---

## 🔑 Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123",
    "password2": "TestPass123",
    "phone_number": "254712345678",
    "national_id": "ID123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'

# Use token in requests
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📋 CRUD Operations

### CREATE (POST)
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "phone_number": "254700000000", "national_id": "ID123"}'
```

### READ (GET)
```bash
# All records
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN"

# Specific record
curl -X GET http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### UPDATE (PATCH/PUT)
```bash
curl -X PATCH http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane"}'
```

### DELETE
```bash
curl -X DELETE http://localhost:8000/api/customers/1/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register/` | POST | Register user |
| `/api/auth/login/` | POST | User login |
| `/api/customers/` | GET/POST | List/create customers |
| `/api/routes/` | GET/POST | List/create routes |
| `/api/vehicles/` | GET/POST | List/create vehicles |
| `/api/bookings/` | GET/POST | List/create bookings |
| `/api/bookings/{id}/confirm/` | POST | Confirm booking |
| `/api/bookings/{id}/cancel/` | POST | Cancel booking |
| `/api/tickets/` | GET/POST | List/create tickets |
| `/api/tickets/validate_ticket/` | POST | Validate by QR code |
| `/api/payments/` | GET/POST | List/create payments |
| `/api/payments/{id}/process_payment/` | POST | Process payment |
| `/api/seats/` | GET/POST | List/create seats |
| `/api/seats/{id}/book/` | POST | Book a seat |
| `/api/seats/{id}/unbook/` | POST | Unbook a seat |

---

## 🌐 WebSocket Connections

```javascript
// Bus Location Updates
const ws = new WebSocket('ws://localhost:8000/ws/bus-location/');
ws.send(JSON.stringify({
    type: 'bus_location',
    bus_id: 1,
    location: { lat: -1.95, lng: 29.87 },
    timestamp: new Date().toISOString()
}));

// Notifications
const notif_ws = new WebSocket('ws://localhost:8000/ws/notifications/');
```

---

## 📊 Available Models

1. **User** - Custom user with roles (admin, operator)
2. **Customer** - Passenger information
3. **Route** - Bus routes with origin/destination
4. **Vehicle** - Bus vehicles with capacity
5. **Seat** - Individual seats in vehicles
6. **Booking** - Customer ticket bookings
7. **Ticket** - QR code based tickets
8. **Payment** - Payment records
9. **Event** - Events/trips
10. **Transaction** - Transaction records
11. **AdminProfile** - Admin extended info
12. **OperatorProfile** - Operator extended info

---

## 🛠️ Common Commands

```bash
# Start server
python manage.py runserver

# Create migration
python manage.py makemigrations core

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Collect static
python manage.py collectstatic

# Run tests
python manage.py test
```

---

## 📂 File Structure

```
Travel_Suite/
├── manage.py                    ← Run Django
├── config/                      ← Project settings
│   ├── settings.py             ← Database & app config
│   └── urls.py                 ← URL router
├── core/                        ← Main app
│   ├── models.py               ← Database models
│   ├── views.py                ← API endpoints
│   ├── serializers.py          ← Data serialization
│   ├── urls.py                 ← API routing
│   └── admin.py                ← Admin interface
├── Frontend/                    ← HTML/CSS/JS files
└── db.sqlite3                   ← Database
```

---

## 🔒 Security Notes

- ✅ JWT authentication enabled
- ✅ CORS configured for localhost
- ✅ Password hashing with bcrypt
- ⚠️ Debug mode is ON (change for production)
- ⚠️ Default admin password should be changed

---

## 🐛 Common Issues

```bash
# Port in use
python manage.py runserver 8001

# Database issues
rm db.sqlite3
python manage.py migrate

# Module errors
pip install -r requirements.txt

# Server won't start
python manage.py check
```

---

## 📖 Documentation Files

- **SETUP_COMPLETE.md** - Full setup summary
- **BACKEND_SETUP.md** - Detailed backend guide
- **API_TESTING.md** - API testing examples
- **README.md** - Project overview

---

## ⏱️ Server Status

- **Django Version**: 4.2.26
- **Python Version**: 3.13+
- **Server**: Running on http://localhost:8000
- **Database**: SQLite (db.sqlite3)
- **Admin**: http://localhost:8000/admin

---

**Ready to build! 🚀**
