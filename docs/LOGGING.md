# Logging Configuration

The application uses Python's built-in `logging` module with both console and file outputs.

## Features

- **Console Output**: All logs are printed to the console in real-time
- **File Output**: Logs are saved to `logs/app.log` with automatic rotation
- **Log Rotation**: Log files are automatically rotated when they reach 10MB
- **Backup Files**: Keeps up to 5 backup log files
- **Configurable Log Level**: Set via `LOG_LEVEL` environment variable

## Log Levels

You can set the log level using the `LOG_LEVEL` environment variable. Available levels:

- `DEBUG`: Detailed information, typically useful only for diagnosing problems
- `INFO`: Confirmation that things are working as expected (default)
- `WARNING`: An indication that something unexpected happened
- `ERROR`: A more serious problem
- `CRITICAL`: A very serious error

## Usage

### Default (INFO level)
```bash
python run.py
```

### Debug mode (shows all headers and detailed information)
```bash
# Linux/Mac
LOG_LEVEL=DEBUG python run.py

# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python run.py
```

### Production mode (errors only)
```bash
# Linux/Mac
LOG_LEVEL=ERROR python run.py

# Windows PowerShell
$env:LOG_LEVEL="ERROR"; python run.py
```

## Log Format

Each log entry includes:
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Logger name
- Log level
- Message

Example:
```
2025-11-20 21:57:00 - checkpoint_api - INFO - Proxying request to: https://203.0.113.100:443/web_api/login
2025-11-20 21:57:01 - checkpoint_api - INFO - >>> X-chkp-sid: abc123def456... (SESSION ID)
```

## Log Files Location

- Primary log file: `logs/app.log`
- Rotated backups: `logs/app.log.1`, `logs/app.log.2`, etc.

## Debugging Session ID Issues
 
When `LOG_LEVEL=DEBUG`, the application will log:
- Detailed proxy operations
- Upstream response headers (essential for debugging missing session IDs)
 
When `LOG_LEVEL=INFO` (default), the application logs are concise:
- Request method and URL (e.g., `POST /proxy/login`)
- **Session ID Detection**: Explicitly logs "Found session ID in response body" or "Forwarding session ID".
- Response status codes
- Warnings if the session ID is missing from the upstream response.
