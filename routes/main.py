import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, abort
from werkzeug.utils import secure_filename
from models.database import get_db_connection, execute_query
from models.product import Product
from models.user import User
from utils.xss_protection import xss_protection
import logging

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    products = Product.get_featured(limit=8)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news WHERE featured = TRUE ORDER BY published_at DESC LIMIT 3")
    news = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', products=products, news=news)

@main_bp.route('/products')
def products():
    products = Product.get_all()
    categories = Product.get_categories()
    return render_template('products.html', products=products, categories=categories)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    products = []  # Initialize products to an empty list

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if query:
        if xss_protection.is_potentially_malicious(query):
            logging.warning(f"Potentially malicious search attempt: {query} from IP: {request.remote_addr}")

        safe_query = xss_protection.sanitize_search_input(query)

        if category:
            if xss_protection.is_potentially_malicious(category):
                logging.warning(f"Potentially malicious category attempt: {category} from IP: {request.remote_addr}")
            safe_category = xss_protection.sanitize_search_input(category)
        else:
            safe_category = category

        if safe_category and query:
            cursor.execute("SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s) AND category = %s",
                           (f'%{query}%', f'%{query}%', safe_category))
        elif query:
            cursor.execute("SELECT * FROM products WHERE name LIKE %s OR description LIKE %s",
                           (f'%{query}%', f'%{query}%'))
        
        products = cursor.fetchall() # Fetch products here

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('search.html', products=products, categories=categories,
                           query=query, category=category)

@main_bp.route('/api/search_suggestions')
def search_suggestions():
    """API endpoint for search suggestions with XSS protection"""
    query = request.args.get('q', '')

    if not query or len(query) < 2:
        return {'suggestions': []}

    # Sanitize input
    if xss_protection.is_potentially_malicious(query):
        logging.warning(f"Malicious search suggestion attempt: {query} from IP: {request.remote_addr}")
        return {'suggestions': []}

    safe_query = xss_protection.sanitize_search_input(query)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT name FROM products WHERE name LIKE %s LIMIT 5",
                   (f'%{query}%',))
    suggestions = [row['name'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # Sanitize suggestions before sending
    safe_suggestions = [xss_protection.sanitize_search_input(s) for s in suggestions]

    return {'suggestions': safe_suggestions}

@main_bp.route('/news')
def news():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news ORDER BY published_at DESC")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('news.html', articles=articles)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/view')
def view_file():
    if 'user_id' not in session:
        abort(403)

    user = User.find_by_id(session['user_id'])
    if not user or not user.is_admin():
        abort(403)

    file_id = request.args.get('id', '')
    if not file_id:
        abort(400)

    try:
        from utils.crypto import oracle
        decrypted_path = oracle.decrypt(file_id)
    except ValueError as e:
        error_msg = str(e)
        return error_msg
    except Exception:
        return "Bad request", 400

    # Database triggers for flag retrieval
    database_triggers = {
        '/flag.txt': 'flag',
        'flag.txt': 'flag',
        '../../flag.txt': 'flag',
        '../../../flag.txt': 'flag',
        '//flag.txt': 'flag',
        '../flag.txt': 'flag'
    }

    if decrypted_path in database_triggers:
        try:
            result = execute_query(
                "SELECT config_value FROM system_config WHERE config_key = %s",
                (database_triggers[decrypted_path],),
                fetch_one=True
            )
            if result:
                return result['config_value'], 200, {'Content-Type': 'text/plain'}
            else:
                return "File not found", 404
        except Exception:
            return "Database error", 500
    else:
        try:
            if not decrypted_path.startswith('/'):
                file_path = os.path.join('uploads', decrypted_path) # Using 'uploads' instead of Config.UPLOAD_FOLDER
            else:
                file_path = decrypted_path

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()

                file_ext = os.path.splitext(file_path)[1].lower()

                if file_ext == '.pdf':
                    return content, 200, {
                        'Content-Type': 'application/pdf',
                        'Content-Disposition': 'inline'
                    }
                else:
                    try:
                        return content.decode('utf-8'), 200, {'Content-Type': 'text/plain'}
                    except UnicodeDecodeError:
                        return content, 200, {'Content-Type': 'application/octet-stream'}
            else:
                return "File not found", 404
        except Exception as e:
            return f"Server error: {str(e)}", 500

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    upload_info = None

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not all([name, email, subject, message]):
            flash('All fields are required.', 'error')
            return redirect(url_for('main.contact'))

        file_path = None
        original_filename = None
        stored_filename = None
        file_size = 0

        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                if allowed_file(file.filename):
                    # Use the original filename (securely)
                    original_filename = secure_filename(file.filename)

                    # Use the configured upload folder instead of constructing our own path
                    from flask import current_app
                    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')

                    # Ensure upload directory exists
                    os.makedirs(upload_dir, exist_ok=True)

                    file_path = os.path.join(upload_dir, original_filename)

                    # Check file size
                    file.seek(0, 2) # Seek to end
                    file_size = file.tell()
                    file.seek(0) # Reset to beginning

                    if file_size > MAX_FILE_SIZE:
                        flash('File too large. Maximum size is 16MB.', 'error')
                        return redirect(url_for('main.contact'))

                    file.save(file_path)

                    # Encrypt the file path using crypto oracle - this becomes the stored_filename
                    from utils.crypto import oracle
                    stored_filename = oracle.encrypt(file_path)

                else:
                    flash('Only PDF files are allowed.', 'error')
                    return redirect(url_for('main.contact'))

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO contact_uploads
            (original_filename, stored_filename, file_path, file_size, user_email, user_name, subject, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (original_filename or '', stored_filename or '', file_path or '', file_size, email, name, subject, message))

        conn.commit()
        upload_id = cursor.lastrowid
        cursor.close()
        conn.close()

        if original_filename and stored_filename:
            upload_info = {
                'original_name': original_filename,
                'view_url': url_for('main.view_file', id=stored_filename),
                'size': file_size
            }

        flash('Thank you for your message! We will get back to you soon.', 'success')

    return render_template('contact.html', upload_info=upload_info)
