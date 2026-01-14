from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import subprocess
import platform
from database import Database
from indexer import FileIndexer
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and indexer
db = Database()
indexer = FileIndexer()

# Sync directory on startup
print("Syncing managed directory on startup...")
file_count = indexer.sync_directory()
print(f"Indexed {file_count} files from {Config.MANAGED_DIRECTORY}")

@app.route('/')
def index():
    """Main dashboard"""
    files = db.get_all_files()
    
    # Get tags for each file
    files_with_tags = []
    for file in files:
        file_dict = dict(file)
        file_dict['tags'] = db.get_file_tags(file['id'])
        files_with_tags.append(file_dict)
    
    all_tags = db.get_all_tags()
    
    return render_template('index.html', 
                         files=files_with_tags, 
                         all_tags=all_tags,
                         managed_dir=Config.MANAGED_DIRECTORY)

@app.route('/search')
def search():
    """Search files"""
    query = request.args.get('q', '')
    tag_filter = request.args.getlist('tags')
    
    if tag_filter:
        files = db.search_files(tags=tag_filter)
    elif query:
        files = db.search_files(query=query)
    else:
        files = db.get_all_files()
    
    # Get tags for each file
    files_with_tags = []
    for file in files:
        file_dict = dict(file)
        file_dict['tags'] = db.get_file_tags(file['id'])
        files_with_tags.append(file_dict)
    
    all_tags = db.get_all_tags()
    
    return render_template('index.html', 
                         files=files_with_tags, 
                         all_tags=all_tags,
                         search_query=query,
                         selected_tags=tag_filter,
                         managed_dir=Config.MANAGED_DIRECTORY)

@app.route('/file/<int:file_id>')
def file_detail(file_id):
    """View file details"""
    file = db.get_file_by_id(file_id)
    if not file:
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    file_dict = dict(file)
    file_dict['tags'] = db.get_file_tags(file_id)
    all_tags = db.get_all_tags()
    
    return render_template('file_detail.html', 
                         file=file_dict, 
                         all_tags=all_tags,
                         managed_dir=Config.MANAGED_DIRECTORY)

@app.route('/file/<int:file_id>/update_notes', methods=['POST'])
def update_notes(file_id):
    """Update file notes"""
    notes = request.form.get('notes', '')
    db.update_file_notes(file_id, notes)
    flash('Notes updated successfully', 'success')
    return redirect(url_for('file_detail', file_id=file_id))

@app.route('/file/<int:file_id>/add_tag', methods=['POST'])
def add_tag(file_id):
    """Add tag to file"""
    tag_name = request.form.get('tag_name', '').strip()
    
    if tag_name:
        db.add_tag_to_file(file_id, tag_name)
        flash(f'Tag "{tag_name}" added successfully', 'success')
    
    return redirect(url_for('file_detail', file_id=file_id))

@app.route('/file/<int:file_id>/remove_tag/<int:tag_id>', methods=['POST'])
def remove_tag(file_id, tag_id):
    """Remove tag from file"""
    db.remove_tag_from_file(file_id, tag_id)
    flash('Tag removed successfully', 'success')
    return redirect(url_for('file_detail', file_id=file_id))

@app.route('/file/<int:file_id>/open')
def open_file(file_id):
    """Open file in default application"""
    file = db.get_file_by_id(file_id)
    if not file:
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    full_path = indexer.get_full_path(file['filepath'])
    
    # Security: Validate that the file path is within the managed directory
    try:
        real_path = os.path.realpath(full_path)
        managed_dir = os.path.realpath(Config.MANAGED_DIRECTORY)
        if not real_path.startswith(managed_dir):
            flash('Access denied: File is outside managed directory', 'error')
            return redirect(url_for('file_detail', file_id=file_id))
    except Exception:
        flash('Invalid file path', 'error')
        return redirect(url_for('file_detail', file_id=file_id))
    
    if not os.path.exists(full_path):
        flash('File does not exist on disk', 'error')
        return redirect(url_for('file_detail', file_id=file_id))
    
    try:
        # Open file with default application based on OS
        if platform.system() == 'Windows':
            os.startfile(full_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', full_path])
        else:  # Linux
            subprocess.run(['xdg-open', full_path])
        
        flash('File opened successfully', 'success')
    except Exception as e:
        flash(f'Error opening file: {str(e)}', 'error')
    
    return redirect(url_for('file_detail', file_id=file_id))

@app.route('/refresh')
def refresh():
    """Refresh file index"""
    file_count = indexer.sync_directory()
    flash(f'Directory synced successfully. {file_count} files indexed.', 'success')
    return redirect(url_for('index'))

@app.route('/api/files')
def api_files():
    """API endpoint to get all files as JSON"""
    files = db.get_all_files()
    return jsonify([dict(f) for f in files])

if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable to enable debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
