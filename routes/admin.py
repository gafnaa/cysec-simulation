import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify, abort
from functools import wraps
from models.database import get_db_connection
from models.user import User
from models.product import Product
from utils.crypto import oracle
from utils.form_validation import validate_product_form, validate_category_form

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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/products.html', products=products)

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
