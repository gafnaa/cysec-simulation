import mysql.connector
from config import Config

def get_db_connection():
    try:
        return mysql.connector.connect(**Config.DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False, fetch_one=False):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
            
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        print(f"Database query error: {e}")
        conn.close()
        return None