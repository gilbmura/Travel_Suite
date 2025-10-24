"""
Transport payment Database Setup Script
----------------------------------
Creates the 'transport_payment' database in MySQL, defines all tables, 
and inserts sample data for testing.
"""

import mysql.connector
from mysql.connector import Error

# --- Connecting Database ---
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="app_user",
        password="AppUser@123"
    )

    if connection.is_connected():
        print(" Connected to MySQL Server")

    cursor = connection.cursor()

    # To drop & recreate database
    cursor.execute("DROP DATABASE IF EXISTS transport_payments_db")
    cursor.execute("CREATE DATABASE transport_payments_db")
    cursor.execute("USE transport_payments_db")

    # --- Create Tables ---
    tables = {}

    tables['Admin'] = """
    CREATE TABLE Admin (
        AdminId INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(50) UNIQUE NOT NULL,
        Password VARCHAR(100) NOT NULL,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """

    tables['Operator'] = """
    CREATE TABLE Operator (
        OperatorId INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Location VARCHAR(100),
        Contact VARCHAR(50),
        License_Number VARCHAR(25) UNIQUE,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """

    tables['Customer'] = """
    CREATE TABLE Customer (
        CustomerId INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Address VARCHAR(255),
        Phone_Number VARCHAR(20) UNIQUE,
        NationalId VARCHAR(25) UNIQUE,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """

    tables['Routes'] = """
    CREATE TABLE Routes (
        RouteId INT AUTO_INCREMENT PRIMARY KEY,
        Origin VARCHAR(100) NOT NULL,
        Destination VARCHAR(100) NOT NULL,
        Departure_Time TIME,
        Arrival_Time TIME,
        Stops VARCHAR(255),
        Fare DECIMAL(10,2),
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """

    tables['Vehicle'] = """
    CREATE TABLE Vehicle (
        VehicleId INT AUTO_INCREMENT PRIMARY KEY,
        License_Plate VARCHAR(20) UNIQUE NOT NULL,
        RouteId INT,
        Capacity INT,
        Status ENUM('Available','Unavailable') DEFAULT 'Available',
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (RouteId) REFERENCES Routes(RouteId)
    )
    """

    tables['Events'] = """
    CREATE TABLE Events (
        EventId INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Date DATE,
        Location VARCHAR(100),
        Available_Seats INT,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """

    tables['Booking'] = """
    CREATE TABLE Booking (
        BookingId INT AUTO_INCREMENT PRIMARY KEY,
        CustomerId INT,
        EventId INT,
        RouteId INT,
        Seat_Number VARCHAR(20),
        Amount DECIMAL(10,2),
        Status ENUM('Pending','Confirmed','Cancelled') DEFAULT 'Pending',
        Date DATE,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (CustomerId) REFERENCES Customer(CustomerId),
        FOREIGN KEY (EventId) REFERENCES Events(EventId),
        FOREIGN KEY (RouteId) REFERENCES Routes(RouteId)
    )
    """

    tables['Payments'] = """
    CREATE TABLE Payments (
        PaymentId INT AUTO_INCREMENT PRIMARY KEY,
        BookingId INT,
        Amount DECIMAL(10,2),
        Payment_Method ENUM('Cash','Card','MobileMoney'),
        Status ENUM('Pending','Completed','Failed') DEFAULT 'Pending',
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (BookingId) REFERENCES Booking(BookingId)
    )
    """

    tables['Transaction'] = """
    CREATE TABLE Transaction (
        Transaction_Id INT AUTO_INCREMENT PRIMARY KEY,
        Payment_Id INT,
        Booking_Id INT,
        Amount DECIMAL(10,2),
        Payment_Status ENUM('Success','Failed','Refunded') DEFAULT 'Success',
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Payment_Id) REFERENCES Payments(PaymentId),
        FOREIGN KEY (Booking_Id) REFERENCES Booking(BookingId)
    )
    """

    # Execute table creation
    for name, ddl in tables.items():
        print(f" Creating table {name}...")
        cursor.execute(ddl)

    # --- Insert Sample Data ---
    print("\n Inserting sample data...")

    cursor.execute(
        "INSERT INTO Admin (Username, Password) VALUES ('superadmin', 'admin123')")
    cursor.execute(
        "INSERT INTO Admin (Username, Password) VALUES ('manager', 'securepass')")

    cursor.execute(
        "INSERT INTO Operator (Name, Location, Contact, License_Number) VALUES ('Volcano Express', 'Kigali', '+250788123456', 'LIC-VE-001')")
    cursor.execute(
        "INSERT INTO Operator (Name, Location, Contact, License_Number) VALUES ('RITCO', 'Musanze', '+250784789321', 'LIC-RT-002')")

    cursor.execute(
        "INSERT INTO Customer (Name, Address, Phone_Number, NationalId) VALUES ('John Doe', 'Kigali, Rwanda', '+250781111111', '1199887766554321')")
    cursor.execute(
        "INSERT INTO Customer (Name, Address, Phone_Number, NationalId) VALUES ('Grace Uwimana', 'Huye, Rwanda', '+250788999888', '1199776655443210')")

    cursor.execute("INSERT INTO Routes (Origin, Destination, Departure_Time, Arrival_Time, Stops, Fare) VALUES ('Kigali', 'Musanze', '07:00:00', '10:00:00', 'Nyirangarama, Gakenke', 5000.00)")
    cursor.execute("INSERT INTO Routes (Origin, Destination, Departure_Time, Arrival_Time, Stops, Fare) VALUES ('Kigali', 'Huye', '09:00:00', '12:00:00', 'Muhanga, Nyanza', 4500.00)")

    cursor.execute(
        "INSERT INTO Vehicle (License_Plate, RouteId, Capacity, Status) VALUES ('RAE123B', 1, 30, 'Available')")
    cursor.execute(
        "INSERT INTO Vehicle (License_Plate, RouteId, Capacity, Status) VALUES ('RAB456C', 2, 40, 'Available')")

    cursor.execute(
        "INSERT INTO Events (Name, Date, Location, Available_Seats) VALUES ('Gorilla Trekking Festival', '2025-12-15', 'Volcanoes National Park', 50)")
    cursor.execute(
        "INSERT INTO Events (Name, Date, Location, Available_Seats) VALUES ('Huye Culture Day', '2025-11-05', 'Huye', 100)")

    cursor.execute("INSERT INTO Booking (CustomerId, EventId, RouteId, Seat_Number, Amount, Status, Date) VALUES (1, 1, 1, 'A12', 5000.00, 'Confirmed', '2025-12-15')")
    cursor.execute(
        "INSERT INTO Booking (CustomerId, EventId, RouteId, Seat_Number, Amount, Status, Date) VALUES (2, 2, 2, 'B05', 4500.00, 'Pending', '2025-11-05')")

    cursor.execute(
        "INSERT INTO Payments (BookingId, Amount, Payment_Method, Status) VALUES (1, 5000.00, 'MobileMoney', 'Completed')")
    cursor.execute(
        "INSERT INTO Payments (BookingId, Amount, Payment_Method, Status) VALUES (2, 4500.00, 'Cash', 'Pending')")

    cursor.execute(
        "INSERT INTO Transaction (Payment_Id, Booking_Id, Amount, Payment_Status) VALUES (1, 1, 5000.00, 'Success')")
    cursor.execute(
        "INSERT INTO Transaction (Payment_Id, Booking_Id, Amount, Payment_Status) VALUES (2, 2, 4500.00, 'Failed')")

    connection.commit()
    print("\n Database setup and sample data inserted successfully.")

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n MySQL connection closed.")
