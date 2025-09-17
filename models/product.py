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
    
    @staticmethod
    def create(name, description, price, category, stock, image_url=None):
        query = """
            INSERT INTO products (name, description, price, category, stock, image_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        params = (name, description, price, category, stock, image_url)
        result = execute_query(query, params, fetch_one=True)
        return result['id'] if result else None

    @staticmethod
    def update(product_id, name, description, price, category, stock, image_url=None):
        query = """
            UPDATE products
            SET name = %s, description = %s, price = %s, category = %s,
                stock = %s, image_url = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id
        """
        params = (name, description, price, category, stock, image_url, product_id)
        result = execute_query(query, params, fetch_one=True)
        return result['id'] if result else None

    @staticmethod
    def delete(product_id):
        query = "DELETE FROM products WHERE id = %s RETURNING id"
        result = execute_query(query, (product_id,), fetch_one=True)
        return result['id'] if result else None

    @staticmethod
    def create_category(name):
        query = "INSERT INTO categories (name) VALUES (%s) RETURNING id"
        result = execute_query(query, (name,), fetch_one=True)
        return result['id'] if result else None

    @staticmethod
    def update_category(category_id, name):
        query = "UPDATE categories SET name = %s WHERE id = %s RETURNING id"
        result = execute_query(query, (name, category_id), fetch_one=True)
        return result['id'] if result else None

    @staticmethod
    def delete_category(category_id):
        query = "DELETE FROM categories WHERE id = %s RETURNING id"
        result = execute_query(query, (category_id,), fetch_one=True)
        return result['id'] if result else None