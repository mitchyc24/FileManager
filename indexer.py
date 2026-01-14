import os
from datetime import datetime
from database import Database
from config import Config

class FileIndexer:
    def __init__(self, directory=None, db=None):
        self.directory = directory or Config.MANAGED_DIRECTORY
        self.db = db or Database()
    
    def sync_directory(self):
        """
        Synchronize the database with the managed directory.
        Adds new files and removes files that no longer exist.
        """
        if not os.path.exists(self.directory):
            print(f"Directory {self.directory} does not exist. Creating it...")
            os.makedirs(self.directory)
            return
        
        existing_files = []
        
        # Walk through the directory
        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, self.directory)
                
                # Get file stats
                stat = os.stat(filepath)
                file_size = stat.st_size
                file_modified = datetime.fromtimestamp(stat.st_mtime)
                
                # Add to database
                self.db.add_file(filename, relative_path, file_size, file_modified)
                existing_files.append(relative_path)
        
        # Remove files from database that no longer exist
        self.db.clear_orphaned_files(existing_files)
        
        return len(existing_files)
    
    def get_full_path(self, relative_path):
        """Convert relative path to full path"""
        return os.path.join(self.directory, relative_path)
