-- Create User Table
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_operator BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    national_id VARCHAR(25) UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create AdminProfile Table
CREATE TABLE AdminProfile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Create OperatorProfile Table
CREATE TABLE OperatorProfile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Create Customer Table
CREATE TABLE Customer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    national_id VARCHAR(25) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Route Table
CREATE TABLE Routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME,
    stops TEXT,
    fare DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Vehicle Table
CREATE TABLE Vehicle (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    route_id INTEGER REFERENCES Routes(id) ON DELETE SET NULL,  -- Link to Routes
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    available_seats INTEGER NOT NULL CHECK (available_seats >= 0),
    status VARCHAR(12) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Booking Table
CREATE TABLE Booking (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES Customer(id) ON DELETE CASCADE,  -- Link to Customer
    route_id INTEGER NOT NULL REFERENCES Routes(id) ON DELETE SET NULL,  -- Link to Routes
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(10) DEFAULT 'Pending',
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Ticket Table
CREATE TABLE Ticket (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES Booking(id) ON DELETE CASCADE,  -- Link to Booking
    qr_code TEXT NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP
);

-- Create Payment Table
CREATE TABLE Payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES Booking(id) ON DELETE CASCADE,  -- Link to Booking
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(12) NOT NULL,
    status VARCHAR(10) DEFAULT 'Pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Transaction Table
CREATE TABLE Transaction (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL REFERENCES Payments(id) ON DELETE CASCADE,  -- Link to Payments
    booking_id INTEGER NOT NULL REFERENCES Booking(id) ON DELETE CASCADE,  -- Link to Booking
    amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(10) DEFAULT 'Success',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
