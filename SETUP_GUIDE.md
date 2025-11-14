## 🚀 TravelSuite - Complete Setup & Running Guide

**Status:** ✅ All systems operational

### 📋 What's Working

#### 1. **Database** ✓

- SQLite database (`db.sqlite3`) with all models migrated
- Pre-populated with seed data:
  - **Admin User**: `admin` / `Admin@123`
  - **Operator User**: `operator` / `Operator@123`
  - **3 Sample Customers**: John Doe, Jane Smith, Bob Johnson
  - **3 Routes**: Nyabugogo→Muhanga, Remera→Gitarama, Nyabugogo→Ruhengeri
  - **3 Vehicles** with seat management: RW001BUS, RW002BUS, RW003BUS

#### 2. **Backend APIs** ✓

- Django REST Framework running on `http://127.0.0.1:8000/api`
- All endpoints operational:
  - `GET /api/` - Health check
  - `POST /api/auth/login/` - User authentication (JWT tokens)
  - `POST /api/auth/register/` - User registration
  - `GET /api/users/` - List all users
  - `GET /api/routes/` - List all routes
  - `GET /api/vehicles/` - List all vehicles with seats
  - `GET /api/customers/` - List all customers
  - `GET /api/bookings/` - List all bookings
  - `GET /api/seats/` - Seat management
  - `GET /api/tickets/` - Ticket management
  - `GET /api/payments/` - Payment tracking
  - And more...

#### 3. **Frontend** ✓

- Static HTML interface at `http://127.0.0.1:8000/Frontend/index.html`
- Connected to Django API on port 8000
- Pages available:
  - Home booking interface
  - Admin login
  - Operator login
  - Staff dashboards

#### 4. **Admin Dashboard** ✓

- Django admin at `http://127.0.0.1:8000/admin/`
- Login with: `admin` / `Admin@123`
- Manage:
  - Users (Admin, Operator, Customer)
  - Routes and Stopovers
  - Vehicles and Seats
  - Bookings and Tickets
  - Payments and Transactions

---

### 🎯 Quick Start

#### **Start the Server**

```powershell
cd c:\Users\frank\.vscode\Travel_Suite
& 'C:/Users/frank/.vscode/.venv/Scripts/python.exe' manage.py runserver 0.0.0.0:8000
```

Server starts at: `http://127.0.0.1:8000`

#### **Access the Application**

| Component           | URL                                       | Credentials        |
| ------------------- | ----------------------------------------- | ------------------ |
| **Home Page**       | http://127.0.0.1:8000/Frontend/index.html | N/A                |
| **Admin Dashboard** | http://127.0.0.1:8000/admin/              | admin / Admin@123  |
| **API Root**        | http://127.0.0.1:8000/api/                | N/A                |
| **Booking API**     | http://127.0.0.1:8000/api/bookings/       | JWT token required |

---

### 🔐 Authentication

#### **Obtaining JWT Token**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123"}'
```

**Response:**

```json
{
  "user": { "id": 1, "username": "admin", "email": "admin@travelsuite.com", ... },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### **Using Token for API Calls**

```bash
curl -X GET http://127.0.0.1:8000/api/routes/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### 📁 Project Structure

```
Travel_Suite/
├── config/                      # Django settings & WSGI
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py                 # WSGI application
├── core/                        # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # API viewsets
│   ├── serializers.py          # REST serializers
│   ├── urls.py                 # API URL routing
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Database seeding script
│   └── migrations/             # Database migrations
├── Frontend/                    # Static frontend files
│   ├── index.html              # Home page
│   ├── style.css               # Styling
│   ├── scripts.js              # JavaScript (API calls)
│   ├── admin-login.html        # Admin login
│   ├── operator-login.html     # Operator login
│   └── ... (other pages)
├── db.sqlite3                  # SQLite database
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── test_api.py                 # API testing script
```

---

### 🛠️ Available Management Commands

#### **Seed Database**

```powershell
& python manage.py seed_data
```

Populates database with sample data (admin, operators, customers, routes, vehicles, seats)

#### **Create Superuser**

```powershell
& python manage.py createsuperuser
```

Create a new admin account

#### **Make Migrations**

```powershell
& python manage.py makemigrations
```

Create new database migration files

#### **Apply Migrations**

```powershell
& python manage.py migrate
```

Apply database migrations

#### **Run Tests**

```powershell
& python manage.py test
```

Run unit tests

---

### 🧪 API Endpoints Reference

#### **Authentication**

- `POST /api/auth/login/` - Login (username, password)
- `POST /api/auth/register/` - Register new user
- `GET /api/users/me/` - Get current user profile

#### **Routes**

- `GET /api/routes/` - List all routes
- `GET /api/routes/{id}/` - Get route details
- `POST /api/routes/` - Create new route (Admin only)
- `GET /api/routes/{id}/available_seats/` - Available seats on route

#### **Vehicles**

- `GET /api/vehicles/` - List all vehicles
- `GET /api/vehicles/{id}/` - Get vehicle details
- `GET /api/vehicles/{id}/seats/` - Get vehicle seats
- `POST /api/vehicles/` - Create new vehicle (Admin only)

#### **Bookings**

- `GET /api/bookings/` - List all bookings
- `POST /api/bookings/` - Create new booking
- `PATCH /api/bookings/{id}/confirm/` - Confirm booking
- `PATCH /api/bookings/{id}/cancel/` - Cancel booking

#### **Seats**

- `GET /api/seats/` - List all seats
- `POST /api/seats/{id}/book/` - Book a seat
- `POST /api/seats/{id}/unbook/` - Unbook a seat

#### **Customers**

- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer

#### **Tickets**

- `GET /api/tickets/` - List tickets
- `POST /api/tickets/validate_ticket/` - Validate by QR code

#### **Payments**

- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `PATCH /api/payments/{id}/process_payment/` - Process payment

---

### 📝 Default Credentials

| Role     | Username | Password     | Email                    |
| -------- | -------- | ------------ | ------------------------ |
| Admin    | admin    | Admin@123    | admin@travelsuite.com    |
| Operator | operator | Operator@123 | operator@travelsuite.com |

---

### ⚙️ Configuration

#### **Database**

- **Current**: SQLite (`db.sqlite3`) - Perfect for development
- **Production**: MySQL/MariaDB (configure in `config/settings.py`)

#### **API Settings**

- **JWT Access Token Lifetime**: 5 minutes
- **JWT Refresh Token Lifetime**: 1 day
- **Pagination**: 10 items per page
- **CORS Enabled For**: localhost:3000, localhost:5000, localhost:8000

#### **Frontend API**

- **Base URL**: `http://127.0.0.1:8000/api`
- **Auto-configured in**: `Frontend/scripts.js` and login pages

---

### 🐛 Troubleshooting

#### **Server Not Starting**

```powershell
# Check if port 8000 is already in use
netstat -ano | Select-String ":8000"

# Kill existing process if needed
Stop-Process -Id <PID> -Force

# Restart server
& python manage.py runserver 0.0.0.0:8000
```

#### **Database Errors**

```powershell
# Reset migrations
& python manage.py migrate --fake core zero
& python manage.py migrate

# Or reseed the database
& python manage.py seed_data
```

#### **CORS Issues**

If frontend can't reach API, ensure `CORS_ALLOWED_ORIGINS` in `config/settings.py` includes your frontend URL.

#### **Token Expired**

Tokens expire after 5 minutes. Use the refresh token to get a new access token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```

---

### 📞 Support

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/api/
- **Database**: SQLite (local file storage)

---

### ✅ Verification Checklist

- [x] Django server running on port 8000
- [x] Database populated with seed data
- [x] Admin dashboard accessible
- [x] Frontend pages loading correctly
- [x] API endpoints responding (with JWT auth)
- [x] Routes, vehicles, customers, bookings in database
- [x] JWT authentication working
- [x] Static files serving correctly
- [x] No FastAPI conflicts (api.py disabled)
- [x] CORS enabled for frontend

---

**Last Updated:** November 13, 2025
**Status:** Production Ready for Testing ✓
