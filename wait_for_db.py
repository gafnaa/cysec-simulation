import mysql.connector
import os
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'database': os.getenv('DB_NAME', 'bl1tz_store'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def wait_for_db():
    max_retries = 30
    retry_interval = 5
    
    print("Waiting for database to be ready...")
    
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                print("Database is ready!")
                conn.close()
                return True
        except mysql.connector.Error as e:
            print(f"Attempt {i+1}/{max_retries}: Database connection failed - {e}")
        time.sleep(retry_interval)
        
    print("Failed to connect to database after multiple retries.")
    return False

if __name__ == '__main__':
    if not wait_for_db():
        exit(1)
