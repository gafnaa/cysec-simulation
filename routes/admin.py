import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify, abort
from functools import wraps
from models.database import get_db_connection
from models.user import User
from models.product import Product
from utils.crypto import oracle
from utils.form_validation import validate_product_form, validate_category_form
from utils.file_handler import save_uploaded_file, delete_file

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))

        user = User.find_by_id(session['user_id'])
        if not user or user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get statistics
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) as total_products FROM products")
    total_products = cursor.fetchone()['total_products']

    cursor.execute("SELECT COUNT(*) as total_news FROM news")
    total_news = cursor.fetchone()['total_news']

    cursor.execute("SELECT COUNT(*) as total_uploads FROM contact_uploads")
    total_uploads = cursor.fetchone()['total_uploads']

    stats = {
        'total_users': total_users,
        'total_products': total_products,
        'total_news': total_news,
        'total_uploads': total_uploads
    }

    # Get recent users
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 5")
    recent_users = cursor.fetchall()

    # Get recent uploads
    cursor.execute("SELECT * FROM contact_uploads ORDER BY upload_time DESC LIMIT 5")
    recent_uploads = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard/admin.html', stats=stats, recent_users=recent_users, recent_uploads=recent_uploads)

@admin_bp.route('/users')
@admin_required
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/users.html', users=users)

@admin_bp.route('/products')
@admin_required
def products():
    products = Product.get_all()
    categories = Product.get_categories()
    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
@validate_product_form
def new_product():
    if request.method == 'POST':
        print("[DEBUG] Received POST request for new product")
        try:
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            category = request.form['category']
            stock = int(request.form['stock'])
            
            print(f"[DEBUG] Form data: name={name}, price={price}, category={category}, stock={stock}")
            
            # Handle image upload
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                print(f"[DEBUG] Image file received: {file.filename if file else 'No file'}")
                if file.filename:
                    image_url = save_uploaded_file(file)
                    print(f"[DEBUG] Image saved: {image_url}")
                    if not image_url:
                        print("[ERROR] Invalid file type")
                        flash('Invalid file type. Please upload a JPG, PNG, or GIF file.', 'error')
                        return redirect(url_for('admin.new_product'))

            try:
                print("[DEBUG] Attempting to create product in database")
                product_id = Product.create(name, description, price, category, stock, image_url)
                print(f"[DEBUG] Product creation result: {product_id}")
                
                if product_id:
                    print("[DEBUG] Product created successfully")
                    flash('Product created successfully!', 'success')
                    return redirect(url_for('admin.products'))
                else:
                    print("[ERROR] Failed to create product in database")
                    if image_url:
                        print(f"[DEBUG] Deleting uploaded image: {image_url}")
                        delete_file(image_url)
                    flash('Failed to create product. Database operation failed.', 'error')
            except Exception as e:
                print(f"[ERROR] Exception during product creation: {str(e)}")
                if image_url:
                    print(f"[DEBUG] Deleting uploaded image due to error: {image_url}")
                    delete_file(image_url)
                flash(f'Error creating product: {str(e)}', 'error')
                flash(f'Failed to create product. Error: {str(e)}', 'error')
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('admin.new_product'))

    categories = Product.get_categories()
    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
@validate_product_form
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin.products'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            category = request.form['category']
            stock = int(request.form['stock'])
            
            # Handle image upload
            image_url = product['image_url']  # Keep existing image by default
            if 'image' in request.files:
                file = request.files['image']
                if file.filename:
                    new_image_url = save_uploaded_file(file)
                    if not new_image_url:
                        flash('Invalid file type. Please upload a JPG, PNG, or GIF file.', 'error')
                        return redirect(url_for('admin.edit_product', product_id=product_id))
                    
                    # Delete old image if it exists
                    if image_url:
                        delete_file(image_url)
                    image_url = new_image_url

            try:
                updated_id = Product.update(product_id, name, description, price, category, stock, image_url)
                if updated_id:
                    flash('Product updated successfully!', 'success')
                    return redirect(url_for('admin.products'))
                else:
                    if image_url != product['image_url']:  # If we uploaded a new image but update failed
                        delete_file(image_url)
                    flash('Failed to update product. Database operation failed.', 'error')
            except Exception as e:
                if image_url != product['image_url']:
                    delete_file(image_url)
                print(f"Error updating product: {str(e)}")
                flash(f'Failed to update product. Error: {str(e)}', 'error')
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('admin.edit_product', product_id=product_id))

    categories = Product.get_categories()
    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    # Get product info first
    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin.products'))
    
    # Delete product from database
    if Product.delete(product_id):
        # If successful, delete associated image file
        if product['image_url']:
            delete_file(product['image_url'])
        flash('Product deleted successfully!', 'success')
    else:
        flash('Failed to delete product.', 'error')
    return redirect(url_for('admin.products'))

@admin_bp.route('/news')
@admin_required
def news():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news ORDER BY published_at DESC")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/news.html', articles=articles)

@admin_bp.route('/uploads')
@admin_required
def uploads():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_uploads ORDER BY upload_time DESC")
    uploads = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/uploads.html', uploads=uploads)

@admin_bp.route('/delete_upload/<int:id>', methods=['POST'])
@admin_required
def delete_upload(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get upload info first
    cursor.execute("SELECT * FROM contact_uploads WHERE id = %s", (id,))
    upload = cursor.fetchone()

    if not upload:
        flash('Upload not found.', 'error')
        return redirect(url_for('admin.uploads'))

    # Delete file from filesystem if it exists
    if upload['file_path'] and os.path.exists(upload['file_path']):
        try:
            os.remove(upload['file_path'])
        except OSError:
            pass

    # Delete from database
    cursor.execute("DELETE FROM contact_uploads WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Upload "{upload["original_filename"]}" has been deleted.', 'success')
    return redirect(url_for('admin.uploads'))

@admin_bp.route('/upload_details/<int:id>')
@admin_required
def upload_details(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_uploads WHERE id = %s", (id,))
    upload = cursor.fetchone()
    cursor.close()
    conn.close()

    if not upload:
        return jsonify({'error': 'Upload not found'}), 404

    return jsonify({
        'id': upload['id'],
        'original_filename': upload['original_filename'],
        'user_name': upload['user_name'],
        'user_email': upload['user_email'],
        'subject': upload['subject'],
        'message': upload['message'],
        'upload_time': upload['upload_time'].isoformat() if upload['upload_time'] else None,
        'file_size': upload['file_size']
    })
