# FileManager

An open source, web based, tag based File Manager with extra features.

## Features

- **Auto-sync Indexing**: Automatically synchronizes the database with folder contents on startup and manual refresh
- **Metadata Management**: Store custom tags, user notes, and file timestamps for each file
- **Advanced Search**: Filter files by tags, partial names, or metadata
- **Simple Web UI**: Clean dashboard for viewing, tagging, and opening files
- **Native Python**: Uses Flask and native SQLite3 (no ORMs required)

## Requirements

- Python 3.7 or higher
- Flask 3.0.0
- Native SQLite3 (included with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mitchyc24/FileManager.git
cd FileManager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Start the application**:
```bash
python app.py
```

For development with debug mode enabled:
```bash
# Windows
set FLASK_DEBUG=1
python app.py

# Linux/Mac
export FLASK_DEBUG=1
python app.py
```

2. **Access the web interface**:
Open your browser and navigate to `http://127.0.0.1:5000`

3. **Configure managed directory** (optional):
By default, the application manages files in the `managed_files` folder. To change this, set the `MANAGED_DIRECTORY` environment variable:
```bash
# Windows
set MANAGED_DIRECTORY=C:\path\to\your\folder
python app.py

# Linux/Mac
export MANAGED_DIRECTORY=/path/to/your/folder
python app.py
```

## How It Works

### Database Schema

The application uses three main tables:
- **files**: Stores file information (name, path, size, timestamps, notes)
- **tags**: Stores unique tags
- **file_tags**: Junction table linking files to tags

### Key Operations

- **Indexing**: On startup and when you click "Refresh Index", the app scans the managed directory and updates the database
- **Tagging**: Add custom tags to files for categorization
- **Notes**: Add detailed notes to individual files
- **Search**: Search by filename, notes content, or filter by tags
- **Open Files**: Click "Open" to launch files in their default application

## Project Structure

```
FileManager/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── database.py         # SQLite database operations
├── indexer.py          # File indexing and sync logic
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   └── file_detail.html
├── static/
│   └── css/
│       └── style.css   # Styling
└── managed_files/      # Default directory for managed files
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /search?q=query` - Search files
- `GET /search?tags=tag1&tags=tag2` - Filter by tags
- `GET /file/<id>` - View file details
- `POST /file/<id>/update_notes` - Update file notes
- `POST /file/<id>/add_tag` - Add tag to file
- `POST /file/<id>/remove_tag/<tag_id>` - Remove tag from file
- `GET /file/<id>/open` - Open file in default application
- `GET /refresh` - Refresh file index
- `GET /api/files` - Get all files as JSON

## License

MIT License - Feel free to use and modify as needed.
