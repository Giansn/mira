# Memory Visualization Web Interface

A web-based dashboard for visualizing and exploring OpenClaw memory files.

## Features

- **Dashboard Overview**: Key statistics and metrics at a glance
- **Timeline Visualization**: Interactive chart showing memory activity over time
- **Full-Text Search**: Search across all memory content with highlighting
- **File Browser**: Browse and view individual memory files
- **Topic Analysis**: Visualize common topics and keywords
- **Content Preview**: View memory entries with formatted display
- **File Analysis**: Detailed statistics and analysis for each file

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

```bash
cd memory-viz
./start.sh
```

Or directly:
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Accessing the Interface

Open your browser and navigate to:
- `http://localhost:5000` - Main dashboard
- `http://localhost:5000/view/MEMORY.md` - View main memory file
- `http://localhost:5000/view/2026-03-01.md` - View daily memory file

## API Endpoints

- `GET /api/memory-data` - Get all parsed memory data
- `GET /api/timeline` - Get timeline data for visualization
- `GET /api/search?q=query` - Search memory entries
- `GET /api/stats` - Get memory statistics
- `GET /api/refresh` - Force refresh of memory data
- `GET /view/<filename>` - View a specific memory file

## Data Sources

The application reads from:
- `~/openclaw/workspace/MEMORY.md` - Main curated memory
- `~/openclaw/workspace/memory/*.md` - Daily memory files

## Architecture

### Backend (Flask)
- **MemoryParser**: Parses markdown files and extracts structured data
- **API Endpoints**: RESTful endpoints for data access
- **Template Rendering**: HTML templates with Bootstrap 5

### Frontend
- **Bootstrap 5**: Responsive UI with dark theme
- **Chart.js**: Interactive charts for visualization
- **Vanilla JavaScript**: Dynamic content loading and interaction

### Data Processing
1. **File Parsing**: Extracts sections and content from markdown
2. **Statistics Generation**: Calculates counts, frequencies, and metrics
3. **Timeline Generation**: Groups entries by date for visualization
4. **Topic Extraction**: Identifies common keywords and topics

## Customization

### Styling
The interface uses a custom dark theme based on GitHub's color scheme. Modify the CSS in `templates/base.html` to change colors and styling.

### Data Processing
Extend the `MemoryParser` class in `app.py` to add new analysis features or change how files are parsed.

### Charts
Chart configurations are in the JavaScript functions in `templates/index.html`. Modify the Chart.js options to change chart appearance and behavior.

## Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/0d1117/58a6ff?text=Memory+Dashboard)

### Timeline
![Timeline](https://via.placeholder.com/800x400/0d1117/238636?text=Timeline+Visualization)

### File Viewer
![File Viewer](https://via.placeholder.com/800x400/0d1117/f85149?text=File+Viewer+with+Analysis)

## Development

### Adding New Features
1. Add new API endpoints in `app.py`
2. Create new templates or extend existing ones
3. Add JavaScript functions for frontend interaction
4. Update the `MemoryParser` class for new data processing

### Testing
```bash
# Run the development server
python app.py

# Test API endpoints
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/search?q=heartbeat
```

### Deployment
For production deployment:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up a reverse proxy (Nginx, Apache)
3. Configure environment variables for secrets
4. Set up logging and monitoring

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Memory files not found**
   - Check that the workspace directory exists at `~/.openclaw/workspace`
   - Verify file permissions

3. **Server won't start on port 5000**
   ```bash
   # Check if port is in use
   sudo lsof -i :5000
   
   # Kill process using port
   sudo kill -9 $(sudo lsof -t -i:5000)
   ```

4. **Charts not loading**
   - Check browser console for JavaScript errors
   - Ensure internet connection for CDN resources

### Logs
Check the Flask console output for error messages and debugging information.

## License

Part of the OpenClaw ecosystem. See main OpenClaw repository for license information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## Support

For issues and questions:
- Open an issue in the OpenClaw repository
- Check the OpenClaw documentation
- Join the OpenClaw community Discord