"""
Configuration settings for the EDA Application
"""
import os

class Config:
    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
    SAMPLE_DATA_FOLDER = os.path.join(BASE_DIR, 'sample_data')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Maximum file size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Secret key for sessions
    SECRET_KEY = 'eda-capstone-2026-secret-key'
    
    # Debug mode
    DEBUG = True

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
os.makedirs(Config.SAMPLE_DATA_FOLDER, exist_ok=True)
