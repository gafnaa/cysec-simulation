import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS_SUBSTRINGS = {'.png', '.jpg', '.jpeg', '.gif'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads/products')

def allowed_file(filename):
    if not filename:
        return False
    return any(ext in filename.lower() for ext in ALLOWED_EXTENSIONS_SUBSTRINGS)

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(file_path)
        
        return f"/uploads/products/{unique_filename}"
    
    return None

def delete_file(file_url):
    if file_url and file_url.startswith('/uploads/products/'):
        # Extract the unique filename from the URL
        unique_filename = file_url.split('/')[-1]
        # Construct the absolute file path using UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False
