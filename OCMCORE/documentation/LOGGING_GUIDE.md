# OCMCORE Logging Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Logging Configuration](#logging-configuration)
- [Log Levels](#log-levels)
- [Per-App Logging](#per-app-logging)
- [Using Loggers in Your Code](#using-loggers-in-your-code)
- [Log File Management](#log-file-management)
- [Docker Logging](#docker-logging)
- [Monitoring and Debugging](#monitoring-and-debugging)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

OCMCORE implements a comprehensive logging system that provides:
- **Per-app log files** with daily rotation
- **Console logging** for development
- **Structured logging** with timestamps and context
- **Request logging** middleware for HTTP requests
- **Docker integration** with persistent log storage
- **Web-based log viewing** via the logs app

## ⚙️ Logging Configuration

The logging system is configured in `settings.py` and provides:

### Console Handler
- Logs to console during development
- Color-coded output for different log levels
- Immediate visibility of application activity

### File Handler (Rotating)
- Daily log rotation with date suffixes
- Automatic cleanup of old log files
- Per-app log file separation
- Persistent storage across application restarts

### Request Logging Middleware
- Logs all HTTP requests and responses
- Includes request time, method, path, status code
- Helps with debugging and performance monitoring

## 📊 Log Levels

The logging system supports standard Python log levels:

| Level | Description | Usage |
|-------|-------------|-------|
| **DEBUG** | Detailed information for debugging | Development and troubleshooting |
| **INFO** | General information about program execution | Normal application flow |
| **WARNING** | Indicates a potential problem | Issues that don't stop execution |
| **ERROR** | A more serious problem | Errors that need attention |
| **CRITICAL** | A critical problem that may prevent the program from running | Severe issues requiring immediate action |

## 🏗️ Per-App Logging

Each Django app gets its own log file:

```
logs/
├── attribution/
│   ├── attribution_2024-01-15.log
│   ├── attribution_2024-01-16.log
│   └── attribution_2024-01-17.log
├── cache/
│   ├── cache_2024-01-15.log
│   ├── cache_2024-01-16.log
│   └── cache_2024-01-17.log
├── logs/
│   ├── logs_2024-01-15.log
│   ├── logs_2024-01-16.log
│   └── logs_2024-01-17.log
└── django/
    ├── django_2024-01-15.log
    ├── django_2024-01-16.log
    └── django_2024-01-17.log
```

## 💻 Using Loggers in Your Code

### Basic Logging

```python
import logging

# Get logger for your app
logger = logging.getLogger(__name__)

# Basic logging examples
logger.debug("Debug message - detailed information")
logger.info("Info message - general information")
logger.warning("Warning message - potential issue")
logger.error("Error message - something went wrong")
logger.critical("Critical message - severe problem")
```

### Logging with Context

```python
import logging

logger = logging.getLogger(__name__)

# Logging with extra context
logger.info("User login successful", extra={
    'user_id': user.id,
    'ip_address': request.META.get('REMOTE_ADDR'),
    'user_agent': request.META.get('HTTP_USER_AGENT')
})

# Logging exceptions
try:
    # Some risky operation
    result = risky_function()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

### Structured Logging

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Structured logging with consistent format
def log_attribution_request(start_date, end_date, id1, id2, attributes):
    logger.info("Attribution request received", extra={
        'operation': 'attribution_generation',
        'start_date': start_date,
        'end_date': end_date,
        'id1': id1,
        'id2': id2,
        'attributes_count': len(attributes),
        'timestamp': datetime.now().isoformat()
    })

# Usage
log_attribution_request('2024-01-01', '2024-01-31', 'user_123', 'campaign_456', ['revenue', 'clicks'])
```

### Performance Logging

```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} completed successfully", extra={
                'function': func.__name__,
                'execution_time': execution_time,
                'status': 'success'
            })
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed", extra={
                'function': func.__name__,
                'execution_time': execution_time,
                'error': str(e),
                'status': 'error'
            })
            raise
    return wrapper

# Usage
@log_performance
def generate_attribution_data(start_date, end_date, id1, id2, attributes):
    # Your attribution logic here
    pass
```

## 📁 Log File Management

### Automatic Rotation
- Log files are rotated daily at midnight
- Old files are automatically cleaned up (default: 30 days)
- Each app maintains its own log history

### Manual Log Management

```bash
# View current log files
ls -la logs/

# View specific app logs
tail -f logs/attribution/attribution_2024-01-17.log

# Search for errors in logs
grep -r "ERROR" logs/

# View logs from last hour
find logs/ -name "*.log" -exec grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" {} \;
```

### Log File Locations

| Environment | Log Directory | Description |
|-------------|---------------|-------------|
| Development | `logs/` | Local log files |
| Docker | `/app/logs/` | Container logs |
| Production | `/var/log/ocmcore/` | System logs |

## 🐳 Docker Logging

### Docker Compose Configuration

The Docker Compose files include volume mounts for persistent logging:

```yaml
volumes:
  - ./logs:/app/logs
```

### Viewing Docker Logs

```bash
# View application logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f attribution
docker-compose logs -f cache

# View logs for specific time period
docker-compose logs --since="2024-01-17T10:00:00" --until="2024-01-17T11:00:00"
```

### Log Persistence

- Logs persist across container restarts
- Volume mounts ensure data isn't lost
- Separate log directories for each environment

## 📊 Monitoring and Debugging

### Web-Based Log Viewer

Access the web-based log viewer at `/logs/` to:
- View all app logs in real-time
- Filter logs by app, date, or log level
- Search through log content
- Download log files

### API Endpoints

The logs app provides REST API endpoints:

```bash
# Get list of log files
GET /api/logs/files/

# Get log content
GET /api/logs/content/{app_name}/{filename}

# Get app-specific logs
GET /api/logs/app/{app_name}

# Get log statistics
GET /api/logs/stats/

# Stream logs in real-time
GET /api/logs/stream/{app_name}
```

### Log Analysis Examples

```python
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def analyze_performance_logs():
    """Analyze performance logs for the last 24 hours"""
    yesterday = datetime.now() - timedelta(days=1)
    
    logger.info("Starting performance analysis", extra={
        'analysis_date': yesterday.strftime('%Y-%m-%d'),
        'analysis_type': 'performance_review'
    })
    
    # Your analysis logic here
    pass

def monitor_error_rates():
    """Monitor error rates across applications"""
    logger.info("Error rate monitoring started", extra={
        'monitoring_type': 'error_rate',
        'threshold': 0.05  # 5% error rate threshold
    })
    
    # Your monitoring logic here
    pass
```

## ✅ Best Practices

### 1. Use Appropriate Log Levels

```python
# Good examples
logger.debug("Processing user data: %s", user_data)  # Detailed debugging
logger.info("User %s logged in successfully", user.username)  # Normal flow
logger.warning("Database connection slow: %s seconds", response_time)  # Potential issue
logger.error("Failed to process payment for user %s", user.id)  # Error condition
logger.critical("Database connection lost, application may be unstable")  # Critical issue
```

### 2. Include Context

```python
# Good - includes context
logger.error("API call failed", extra={
    'endpoint': '/api/attribution/generate/',
    'user_id': user.id,
    'request_id': request_id,
    'error_code': response.status_code
})

# Bad - no context
logger.error("API call failed")
```

### 3. Use Structured Logging

```python
# Good - structured format
def log_cache_operation(operation, key, success, duration=None):
    logger.info("Cache operation completed", extra={
        'operation': operation,
        'cache_key': key,
        'success': success,
        'duration_ms': duration * 1000 if duration else None,
        'timestamp': datetime.now().isoformat()
    })

# Usage
log_cache_operation('get', 'user_123_profile', True, 0.002)
log_cache_operation('set', 'user_123_profile', False, None)
```

### 4. Avoid Sensitive Information

```python
# Good - no sensitive data
logger.info("User authentication successful", extra={
    'user_id': user.id,
    'ip_address': request.META.get('REMOTE_ADDR')
})

# Bad - includes sensitive data
logger.info("User authentication successful", extra={
    'user_id': user.id,
    'password': user.password,  # Never log passwords!
    'credit_card': user.credit_card  # Never log sensitive data!
})
```

### 5. Performance Considerations

```python
# Good - lazy evaluation
logger.debug("Processing data: %s", expensive_operation())

# Bad - always evaluates
logger.debug("Processing data: " + expensive_operation())
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Log Files Not Created

```bash
# Check permissions
ls -la logs/
chmod 755 logs/
chmod 644 logs/*/*.log

# Check disk space
df -h
```

#### 2. Log Rotation Not Working

```python
# Check log rotation settings in settings.py
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',  # Rotate at midnight
            'interval': 1,       # Every day
            'backupCount': 30,   # Keep 30 days
        }
    }
}
```

#### 3. Docker Logs Not Persistent

```bash
# Check volume mounts
docker-compose config

# Verify volume exists
docker volume ls

# Check container logs
docker-compose logs
```

#### 4. High Log Volume

```python
# Reduce log verbosity in production
LOGGING = {
    'loggers': {
        'django': {
            'level': 'WARNING',  # Only warnings and above
        },
        'attribution': {
            'level': 'INFO',     # Info and above
        }
    }
}
```

### Debug Commands

```bash
# Check log file sizes
du -sh logs/*/

# Find largest log files
find logs/ -name "*.log" -exec ls -lh {} \; | sort -k5 -hr

# Monitor log growth
watch -n 5 'du -sh logs/*/'

# Search for specific patterns
grep -r "ERROR" logs/ | wc -l
grep -r "WARNING" logs/ | wc -l
```

### Performance Monitoring

```python
# Monitor log file growth
import os
from datetime import datetime

def check_log_sizes():
    log_dir = 'logs/'
    for app_dir in os.listdir(log_dir):
        app_path = os.path.join(log_dir, app_dir)
        if os.path.isdir(app_path):
            total_size = sum(
                os.path.getsize(os.path.join(app_path, f))
                for f in os.listdir(app_path)
                if f.endswith('.log')
            )
            logger.info(f"Log size for {app_dir}: {total_size / 1024 / 1024:.2f} MB")
```

## 📚 Additional Resources

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Django Logging Configuration](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Docker Logging Best Practices](https://docs.docker.com/config/containers/logging/)

## 🤝 Support

For logging-related issues:
1. Check this guide first
2. Review the troubleshooting section
3. Check log files for specific error messages
4. Contact the development team with specific error details

---

*Last updated: January 2024* 