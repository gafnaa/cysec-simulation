from functools import wraps
from flask import request, flash, redirect, url_for

def validate_product_form(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '')
            category = request.form.get('category', '').strip()
            stock = request.form.get('stock', '')
            
            errors = []

            # Validate name
            if not name:
                errors.append("Product name is required.")
            elif len(name) > 100:
                errors.append("Product name must be less than 100 characters.")

            # Validate description
            if not description:
                errors.append("Product description is required.")
            elif len(description) > 500:
                errors.append("Product description must be less than 500 characters.")

            # Validate price
            try:
                price_float = float(price)
                if price_float < 0:
                    errors.append("Price cannot be negative.")
                elif price_float > 1000000:
                    errors.append("Price cannot exceed $1,000,000.")
            except (ValueError, TypeError):
                errors.append("Please enter a valid price.")

            # Validate stock
            try:
                stock_int = int(stock)
                if stock_int < 0:
                    errors.append("Stock cannot be negative.")
                elif stock_int > 100000:
                    errors.append("Stock cannot exceed 100,000 units.")
            except (ValueError, TypeError):
                errors.append("Please enter a valid stock number.")

            # Validate category
            if not category:
                errors.append("Category is required.")

            # Optional: Validate image URL if provided
            image_url = request.form.get('image_url', '').strip()
            if image_url:
                if not image_url.startswith(('http://', 'https://')):
                    errors.append("Image URL must start with http:// or https://")
                elif len(image_url) > 500:
                    errors.append("Image URL must be less than 500 characters.")

            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(request.url)

            # If validation passes, proceed with the original function
            return f(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated_function

def validate_category_form(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            
            errors = []

            # Validate category name
            if not name:
                errors.append("Category name is required.")
            elif len(name) > 50:
                errors.append("Category name must be less than 50 characters.")
            elif not name.replace(' ', '').isalnum():
                errors.append("Category name can only contain letters, numbers, and spaces.")

            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(request.url)

            # If validation passes, proceed with the original function
            return f(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated_function