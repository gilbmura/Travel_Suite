# Database Setup Guide

## Django Configuration

Add the following to your Django `settings.py`:

### 1. Installed Apps
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'backend',  # Your backend app
]
```

### 2. Database Configuration (MySQL)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Authentication
```python
AUTH_USER_MODEL = 'backend.User'  # Use custom User model
```

## Running Migrations

Once Django is configured, apply the migrations:

```bash
python manage.py makemigrations backend
python manage.py migrate backend
```

## Database Schema

Your schema includes the following tables:
- `auth_user` - User accounts with admin/operator roles
- `AdminProfile` - Extended profile for admins
- `OperatorProfile` - Extended profile for operators
- `Customer` - Customer information
- `Routes` - Transportation routes
- `Vehicle` - Vehicles for routes
- `Seat` - Individual seats in vehicles
- `Booking` - Customer bookings
- `Ticket` - Tickets for bookings with QR codes
- `Payments` - Payment records
- `Transaction` - Transaction records

## Models Location

All models are located in `backend/models/` folder:
- `user.py` - User model
- `admin_profile.py` - AdminProfile model
- `operator_profile.py` - OperatorProfile model
- `customer.py` - Customer model
- `route.py` - Route model
- `vehicle.py` - Vehicle model
- `seat.py` - Seat model
- `booking.py` - Booking model
- `ticket.py` - Ticket model
- `payment.py` - Payment model
- `transaction.py` - Transaction model

All models are exported from `models/__init__.py` for easy importing.
