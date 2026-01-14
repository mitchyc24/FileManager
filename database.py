import sqlite3
import os
from datetime import datetime
from config import Config

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize the database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                file_modified TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Create file_tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_file(self, filename, filepath, file_size, file_modified):
        """Add a file to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO files (filename, filepath, file_size, file_modified)
                VALUES (?, ?, ?, ?)
            ''', (filename, filepath, file_size, file_modified))
            conn.commit()
            file_id = cursor.lastrowid
            return file_id
        except sqlite3.IntegrityError:
            # File already exists, update it
            cursor.execute('''
                UPDATE files
                SET filename = ?, file_size = ?, file_modified = ?, indexed_at = CURRENT_TIMESTAMP
                WHERE filepath = ?
            ''', (filename, file_size, file_modified, filepath))
            conn.commit()
            cursor.execute('SELECT id FROM files WHERE filepath = ?', (filepath,))
            file_id = cursor.fetchone()['id']
            return file_id
        finally:
            conn.close()
    
    def get_all_files(self):
        """Get all files from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files ORDER BY filename')
        files = cursor.fetchall()
        conn.close()
        return files
    
    def get_file_by_id(self, file_id):
        """Get a specific file by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
        file = cursor.fetchone()
        conn.close()
        return file
    
    def update_file_notes(self, file_id, notes):
        """Update notes for a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE files SET notes = ? WHERE id = ?', (notes, file_id))
        conn.commit()
        conn.close()
    
    def delete_file(self, file_id):
        """Delete a file from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()
    
    def search_files(self, query=None, tags=None):
        """Search files by name or tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if tags and len(tags) > 0:
            # Search by tags
            placeholders = ','.join('?' * len(tags))
            query_sql = f'''
                SELECT DISTINCT f.* FROM files f
                INNER JOIN file_tags ft ON f.id = ft.file_id
                INNER JOIN tags t ON ft.tag_id = t.id
                WHERE t.tag_name IN ({placeholders})
                ORDER BY f.filename
            '''
            cursor.execute(query_sql, tags)
        elif query:
            # Search by filename or notes
            cursor.execute('''
                SELECT * FROM files
                WHERE filename LIKE ? OR notes LIKE ?
                ORDER BY filename
            ''', (f'%{query}%', f'%{query}%'))
        else:
            # Return all files
            cursor.execute('SELECT * FROM files ORDER BY filename')
        
        files = cursor.fetchall()
        conn.close()
        return files
    
    def add_tag(self, tag_name):
        """Add a tag to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO tags (tag_name) VALUES (?)', (tag_name,))
            conn.commit()
            tag_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Tag already exists, get its ID
            cursor.execute('SELECT id FROM tags WHERE tag_name = ?', (tag_name,))
            tag_id = cursor.fetchone()['id']
        finally:
            conn.close()
        
        return tag_id
    
    def get_all_tags(self):
        """Get all tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tags ORDER BY tag_name')
        tags = cursor.fetchall()
        conn.close()
        return tags
    
    def add_tag_to_file(self, file_id, tag_name):
        """Add a tag to a file"""
        tag_id = self.add_tag(tag_name)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)', (file_id, tag_id))
            conn.commit()
        except sqlite3.IntegrityError:
            # Tag already associated with file
            pass
        finally:
            conn.close()
    
    def remove_tag_from_file(self, file_id, tag_id):
        """Remove a tag from a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM file_tags WHERE file_id = ? AND tag_id = ?', (file_id, tag_id))
        conn.commit()
        conn.close()
    
    def get_file_tags(self, file_id):
        """Get all tags for a specific file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.* FROM tags t
            INNER JOIN file_tags ft ON t.id = ft.tag_id
            WHERE ft.file_id = ?
            ORDER BY t.tag_name
        ''', (file_id,))
        tags = cursor.fetchall()
        conn.close()
        return tags
    
    def clear_orphaned_files(self, existing_filepaths):
        """Remove files from database that no longer exist on disk"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if not existing_filepaths:
            # If no files exist, clear all
            cursor.execute('DELETE FROM files')
        else:
            placeholders = ','.join('?' * len(existing_filepaths))
            cursor.execute(f'DELETE FROM files WHERE filepath NOT IN ({placeholders})', existing_filepaths)
        
        conn.commit()
        conn.close()
