import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'img', 'profiles', picture_fn)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    form_picture.save(picture_path)
    
    return os.path.join('img', 'profiles', picture_fn).replace("\\", "/")


def save_upload_file(file_obj):
    if file_obj and file_obj.filename:
        filename = secure_filename(file_obj.filename)
        save_dir = os.path.join(current_app.root_path, 'static', 'img')
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        file_path = os.path.join(save_dir, filename)
        file_obj.save(file_path)
        return filename
    return None

def delete_file(filename):
    if not filename:
        return
        
    file_path = os.path.join(current_app.root_path, 'static', 'img', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
