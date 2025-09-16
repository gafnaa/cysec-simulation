from models.database import execute_query

class Product:
    @staticmethod
    def get_all():
        query = "SELECT * FROM products ORDER BY created_at DESC"
        return execute_query(query, fetch=True)
    
    @staticmethod
    def get_featured(limit=8):
        query = "SELECT * FROM products ORDER BY created_at DESC LIMIT %s"
        return execute_query(query, (limit,), fetch=True)
    
    @staticmethod
    def search(search_term, category=None):
        if category:
            query = "SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s) AND category = %s"
            params = (f'%{search_term}%', f'%{search_term}%', category)
        else:
            query = "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s"
            params = (f'%{search_term}%', f'%{search_term}%')
        
        return execute_query(query, params, fetch=True)
    
    @staticmethod
    def get_by_id(product_id):
        query = "SELECT * FROM products WHERE id = %s"
        return execute_query(query, (product_id,), fetch_one=True)
    
    @staticmethod
    def get_categories():
        query = "SELECT * FROM categories"
        return execute_query(query, fetch=True)
    
    @staticmethod
    def get_by_category(category):
        query = "SELECT * FROM products WHERE category = %s"
        return execute_query(query, (category,), fetch=True)