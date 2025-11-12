# Travel Suite Backend - Complete Setup Guide

## ✅ Project Structure Setup Complete

Your Django project has been successfully configured with the following structure:

```
Travel_Suite/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── config/                   # Project configuration
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL router
│   ├── asgi.py              # ASGI configuration for Daphne/WebSocket
│   └── wsgi.py              # WSGI configuration
├── core/                     # Main app with all models
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── serializers.py       # REST API serializers
│   ├── views.py             # REST API ViewSets
│   ├── urls.py              # API URL routing
│   ├── consumers.py         # WebSocket consumers
│   ├── routing.py           # WebSocket URL routing
│   └── utils.py             # Utility functions
├── Frontend/                 # Frontend files (HTML, CSS, JS)
│   ├── index.html
│   ├── admin.html
│   ├── customer.html
│   ├── opa.html
│   ├── style.css
│   └── scripts.js
└── db.sqlite3               # SQLite database (for development)
```

## 🚀 Running the Server

The backend server is already running! To access it:

**API Base URL**: `http://localhost:8000/api/`

**Admin Dashboard**: `http://localhost:8000/admin/`
- Username: `admin`
- Password: `admin123`

### To start the server manually:

```bash
cd "d:\ALU_Trials\foundations project\Travel_Suite"
python manage.py runserver
```

## 📱 API Endpoints

Your backend now has fully functional CRUD endpoints:

### Authentication
- **Register**: `POST /api/auth/register/`
- **Login**: `POST /api/auth/login/`
- **Get Current User**: `GET /api/users/me/`

### Customers
- **List/Create**: `GET|POST /api/customers/`
- **Retrieve/Update/Delete**: `GET|PUT|PATCH|DELETE /api/customers/{id}/`

### Routes
- **List/Create**: `GET|POST /api/routes/`
- **Retrieve/Update/Delete**: `GET|PUT|PATCH|DELETE /api/routes/{id}/`
- **Get Available Seats**: `GET /api/routes/{id}/available_seats/`

### Vehicles
- **List/Create**: `GET|POST /api/vehicles/`
- **Retrieve/Update/Delete**: `GET|PUT|PATCH|DELETE /api/vehicles/{id}/`
- **Get Vehicle Seats**: `GET /api/vehicles/{id}/seats/`

### Seats
- **List/Create**: `GET|POST /api/seats/`
- **Book Seat**: `POST /api/seats/{id}/book/`
- **Unbook Seat**: `POST /api/seats/{id}/unbook/`

### Bookings
- **List/Create**: `GET|POST /api/bookings/`
- **Confirm Booking**: `POST /api/bookings/{id}/confirm/`
- **Cancel Booking**: `POST /api/bookings/{id}/cancel/`

### Tickets
- **List/Create**: `GET|POST /api/tickets/`
- **Validate Ticket**: `POST /api/tickets/validate_ticket/`

### Payments
- **List/Create**: `GET|POST /api/payments/`
- **Process Payment**: `POST /api/payments/{id}/process_payment/`

### Events
- **List/Create/Retrieve/Update/Delete**: `/api/events/`

### Transactions
- **List/Create/Retrieve/Update/Delete**: `/api/transactions/`

## 🔐 Database Configuration

### Current: SQLite (Development)
Perfect for testing and local development.

### For Production: MySQL

Edit `config/settings.py` and uncomment the MySQL configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travel_suite_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🌐 WebSocket Endpoints

Real-time communication via WebSockets:

- **Bus Location Updates**: `ws://localhost:8000/ws/bus-location/`
  - Send bus location data in real-time
  - All clients receive live location updates

- **Notifications**: `ws://localhost:8000/ws/notifications/`
  - Receive booking, payment, and ticket notifications

## 🔌 Frontend Integration

### REST API Example (JavaScript/Fetch)

```javascript
// Register
fetch('http://localhost:8000/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'john_doe',
        password: 'secure123',
        password2: 'secure123',
        phone_number: '254712345678',
        national_id: 'ID12345'
    })
})
.then(res => res.json())
.then(data => {
    console.log('Access Token:', data.access);
    localStorage.setItem('access_token', data.access);
});

// Get Customers (with auth)
const token = localStorage.getItem('access_token');
fetch('http://localhost:8000/api/customers/', {
    headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log('Customers:', data));
```

### WebSocket Example (JavaScript)

```javascript
// Connect to bus location updates
const ws = new WebSocket('ws://localhost:8000/ws/bus-location/');

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'bus_location',
        bus_id: 1,
        location: { lat: -1.2866, lng: 36.8172 },
        timestamp: new Date().toISOString()
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Bus Location:', data);
};
```

## 🛠️ Common Management Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic

# Access Django shell
python manage.py shell

# Run tests
python manage.py test
```

## 📊 Admin Interface Features

Access `http://localhost:8000/admin/` to manage:
- ✅ Users (with custom fields: phone_number, national_id)
- ✅ Admin Profiles
- ✅ Operator Profiles
- ✅ Customers
- ✅ Routes
- ✅ Vehicles
- ✅ Seats
- ✅ Events
- ✅ Bookings
- ✅ Tickets (with QR code validation)
- ✅ Payments
- ✅ Transactions

## 🔄 CORS Configuration

Frontend requests from different origins are enabled. Configured origins:
- `http://localhost:3000`
- `http://localhost:8000`
- `http://localhost:5000`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000`

To add more, edit `CORS_ALLOWED_ORIGINS` in `config/settings.py`.

## 📝 Key Features Implemented

✅ **Custom User Model** - with roles (admin, operator)
✅ **JWT Authentication** - via SimpleJWT
✅ **REST API** - Full CRUD operations on all models
✅ **WebSocket Support** - Real-time bus locations & notifications
✅ **Admin Interface** - Comprehensive Django admin panel
✅ **Database Migrations** - Fully initialized
✅ **CORS Support** - Ready for frontend integration
✅ **Utility Functions** - QR code validation, seat availability, etc.

## ⚡ Next Steps

1. **Connect Frontend**: Update your JavaScript to use the API endpoints
2. **Customize Database**: Switch to MySQL with your credentials
3. **Add Business Logic**: Extend views.py with custom endpoints
4. **Deploy**: Use Daphne/Gunicorn for production

## ❓ Troubleshooting

**Port already in use**: 
```bash
python manage.py runserver 0.0.0.0:8001
```

**Database locked**:
```bash
rm db.sqlite3
python manage.py migrate
```

**Module not found**:
```bash
python -m pip install -r requirements.txt
```

---

**Your Travel Suite backend is ready for CRUD operations!** 🎉
