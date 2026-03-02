# Memory Visualization Web Interface - Setup Complete

## What Was Built

A comprehensive web interface for visualizing OpenClaw memory files with the following features:

### Core Components:
1. **Memory Parser** (`parse_memory.py`)
   - Parses `MEMORY.md` and daily memory files
   - Extracts structured data (sections, dates, topics)
   - Exports to JSON for web consumption

2. **Flask Web Application** (`app.py`)
   - RESTful API endpoints for data access
   - Web interface with real-time updates
   - Search functionality across all memory files

3. **Interactive Web Interface** (`templates/index.html`)
   - Dark theme with modern UI design
   - Timeline visualization of memory entries
   - Statistics dashboard with charts
   - Full-text search with highlighting
   - Topic analysis and tagging

4. **Supporting Files**
   - Startup script (`start.sh`)
   - Systemd service file (`memory-viz.service`)
   - Requirements file (`requirements.txt`)
   - CSS styling (`static/style.css`)

## Features

### 1. **Timeline View**
   - Chronological display of memory entries
   - Color-coded by type (main vs daily)
   - Interactive click-to-view details
   - Filter by memory type

### 2. **Search Functionality**
   - Full-text search across all memory content
   - Real-time results with preview
   - Click results to view full content
   - Highlight matching terms

### 3. **Statistics Dashboard**
   - Total files, entries, and words
   - Date range and activity metrics
   - Topic frequency analysis
   - Interactive charts (line, doughnut)

### 4. **Data Visualization**
   - Activity trends over time
   - Word count distribution
   - Topic frequency charts
   - Recent activity feed

### 5. **Memory Content Viewer**
   - Detailed view of selected entries
   - Format-preserving display
   - Metadata (date, type, file)
   - Related content navigation

## Installation Status

✅ **Virtual Environment**: Created at `memory-viz/venv/`
✅ **Dependencies**: Installed (Flask, BeautifulSoup4, Markdown, etc.)
✅ **Data Parsed**: Memory files successfully parsed to JSON
✅ **Web Server**: Running on port 5000

## Access Instructions

### Quick Start:
```bash
cd /home/ubuntu/.openclaw/workspace/memory-viz
./start.sh
```

### Access Web Interface:
Open browser and navigate to: `http://localhost:5000`

### API Endpoints:
- `GET /` - Main web interface
- `GET /api/memory-data` - Complete memory data
- `GET /api/timeline` - Timeline data
- `GET /api/search?q=<query>` - Search memory
- `GET /api/stats` - Statistics
- `GET /api/refresh` - Refresh data

## Data Sources

The visualization reads from:
- `/home/ubuntu/.openclaw/workspace/MEMORY.md`
- `/home/ubuntu/.openclaw/workspace/memory/YYYY-MM-DD.md` files
- Other `.md` files in the memory directory

## Current Statistics (from initial parse)

- **Daily Files**: 5
- **Total Entries**: 20
- **Date Range**: 2025-02-25 to 2026-03-01 (369 days)
- **Common Topics**: telegram, tools, policy, cron, heartbeat, error, thesis, security

## Next Steps

### 1. **Production Deployment**
```bash
# Copy service file to systemd
sudo cp memory-viz.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable memory-viz
sudo systemctl start memory-viz
```

### 2. **Access Control** (if needed)
- Add authentication to `app.py`
- Configure HTTPS with reverse proxy
- Set up firewall rules for port 5000

### 3. **Enhancements**
- Add export functionality (PDF/CSV)
- Implement real-time updates
- Add memory editing capabilities
- Create mobile-responsive design
- Add data backup/restore features

## Troubleshooting

### Web Interface Not Loading
```bash
# Check if server is running
ps aux | grep app.py

# Check logs
cd /home/ubuntu/.openclaw/workspace/memory-viz
tail -f nohup.out
```

### Data Not Updating
```bash
# Refresh data manually
curl http://localhost:5000/api/refresh
```

### Port Conflicts
Edit `app.py` and change port number:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Maintenance

### Regular Updates
1. The parser automatically updates data on refresh
2. Memory files are read in real-time when accessed
3. Charts update automatically with new data

### Backup
Backup the entire directory:
```bash
tar -czf memory-viz-backup.tar.gz /home/ubuntu/.openclaw/workspace/memory-viz/
```

## Integration with OpenClaw

This tool complements OpenClaw by:
- Providing visual insights into memory patterns
- Enabling easy search and discovery
- Tracking system evolution over time
- Identifying common themes and issues

The interface can be extended to integrate directly with OpenClaw's API for real-time memory updates.