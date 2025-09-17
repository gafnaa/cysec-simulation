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
        print("[ERROR] Failed to establish database connection")
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        print(f"[DEBUG] Executing query: {query}")
        print(f"[DEBUG] Parameters: {params}")
        
        cursor.execute(query, params or ())
        print("[DEBUG] Query executed successfully")
        
        if fetch_one:
            result = cursor.fetchone()
            print(f"[DEBUG] Fetched one row: {result}")
        elif fetch:
            result = cursor.fetchall()
            print(f"[DEBUG] Fetched all rows: {len(result) if result else 0} rows")
        else:
            conn.commit()
            result = cursor.rowcount
            print(f"[DEBUG] Rows affected: {result}")
            
        return result
    except mysql.connector.Error as e:
        print(f"[ERROR] Database query error: {e}")
        print(f"[ERROR] Error code: {e.errno}")
        print(f"[ERROR] SQL State: {e.sqlstate}")
        print(f"[ERROR] Error message: {e.msg}")
        conn.rollback()
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()