import pymysql

# --- MySQL user connection settings ---
HOSTS = ["localhost"]  # try both local and server IP
PORT = 3306
USER = "user_app"            # your MySQL user
PASSWORD = "Password123!"   # MySQL user's password
DATABASE = None              # optional: set a database name if needed

for host in HOSTS:
    try:
        print(f"Trying to connect to MySQL at {host}...")
        conn = pymysql.connect(
            host=host,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            connect_timeout=5
        )
        print(f"Connection successful at {host}!")
        conn.close()
        break  # stop after first successful connection
    except pymysql.OperationalError as e:
        print(f"Connection failed at {host}: {e}")
