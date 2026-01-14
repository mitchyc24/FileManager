import os

# Configuration settings for FileManager
class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'filemanager.db')
    
    # Directory to manage (default to a 'managed_files' folder in the app directory)
    MANAGED_DIRECTORY = os.environ.get('MANAGED_DIRECTORY') or os.path.join(os.path.dirname(__file__), 'managed_files')
    
    # Ensure managed directory exists
    if not os.path.exists(MANAGED_DIRECTORY):
        os.makedirs(MANAGED_DIRECTORY)
