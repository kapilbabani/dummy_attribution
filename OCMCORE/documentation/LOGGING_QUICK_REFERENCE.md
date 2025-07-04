# Logging Quick Reference

## 🚀 Quick Start

### Basic Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Logging with Context
```python
logger.info("Operation completed", extra={
    'user_id': user.id,
    'operation': 'data_processing',
    'duration_ms': 150
})
```

## 📁 Log File Locations

| Environment | Path | Description |
|-------------|------|-------------|
| Development | `logs/` | Local log files |
| Docker | `/app/logs/` | Container logs |
| Production | `/var/log/ocmcore/` | System logs |

## 🔍 Viewing Logs

### Command Line
```bash
# View specific app logs
tail -f logs/attribution/attribution_2024-01-17.log

# Search for errors
grep -r "ERROR" logs/

# View logs from last hour
find logs/ -name "*.log" -exec grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" {} \;
```

### Docker
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f attribution

# View logs for time period
docker-compose logs --since="2024-01-17T10:00:00" --until="2024-01-17T11:00:00"
```

### Web Interface
- **URL**: http://localhost:8000/logs/
- **Features**: Real-time viewing, filtering, searching, downloading

## 📊 Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Development details | `logger.debug("Processing user data: %s", data)` |
| **INFO** | Normal flow | `logger.info("User %s logged in", username)` |
| **WARNING** | Potential issues | `logger.warning("Slow response: %s seconds", time)` |
| **ERROR** | Problems | `logger.error("API call failed: %s", error)` |
| **CRITICAL** | Severe issues | `logger.critical("Database connection lost")` |

## 🏗️ Per-App Logging

### Log File Structure
```
logs/
├── attribution/
│   ├── attribution_2024-01-15.log
│   ├── attribution_2024-01-16.log
│   └── attribution_2024-01-17.log
├── cache/
│   ├── cache_2024-01-15.log
│   └── cache_2024-01-16.log
└── django/
    ├── django_2024-01-15.log
    └── django_2024-01-16.log
```

### App-Specific Loggers
```python
# In attribution/views.py
logger = logging.getLogger('attribution')

# In cache/views.py
logger = logging.getLogger('cache')

# In logs/views.py
logger = logging.getLogger('logs')
```

## 🔧 Common Patterns

### Performance Logging
```python
import time
from functools import wraps

def log_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} completed", extra={
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
def my_function():
    pass
```

### Exception Logging
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

### Request Logging
```python
def log_request(request, response, duration):
    logger.info("HTTP Request", extra={
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code,
        'duration_ms': duration * 1000,
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'ip_address': request.META.get('REMOTE_ADDR')
    })
```

## 📈 Monitoring Commands

### Log Statistics
```bash
# Count errors by app
for app in logs/*/; do
    echo "$(basename $app): $(grep -c "ERROR" $app/*.log 2>/dev/null | awk '{sum+=$1} END {print sum+0}')"
done

# Find largest log files
find logs/ -name "*.log" -exec ls -lh {} \; | sort -k5 -hr

# Monitor log growth
watch -n 5 'du -sh logs/*/'
```

### Performance Analysis
```python
# Analyze response times
grep "duration_ms" logs/*/*.log | awk '{print $NF}' | sort -n

# Find slow requests (>1 second)
grep "duration_ms" logs/*/*.log | awk '$NF > 1000 {print $0}'
```

## 🚨 Troubleshooting

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

#### 2. High Log Volume
```python
# Reduce verbosity in production
LOGGING = {
    'loggers': {
        'django': {'level': 'WARNING'},
        'attribution': {'level': 'INFO'},
    }
}
```

#### 3. Docker Logs Not Persistent
```bash
# Check volume mounts
docker-compose config

# Verify volume exists
docker volume ls
```

## 🔗 API Endpoints

### Logs API
```bash
# Get log files
GET /api/logs/files/

# Get log content
GET /api/logs/content/{app_name}/{filename}

# Get app logs
GET /api/logs/app/{app_name}

# Get statistics
GET /api/logs/stats/

# Stream logs
GET /api/logs/stream/{app_name}
```

## ✅ Best Practices

### Do's
- ✅ Use appropriate log levels
- ✅ Include context with `extra` parameter
- ✅ Use structured logging format
- ✅ Log exceptions with `exc_info=True`
- ✅ Use lazy evaluation for expensive operations

### Don'ts
- ❌ Never log sensitive data (passwords, tokens)
- ❌ Don't use string concatenation in log messages
- ❌ Don't log at DEBUG level in production
- ❌ Don't log entire request/response bodies
- ❌ Don't use print() statements

## 📚 Related Documentation

- **[Full Logging Guide](LOGGING_GUIDE.md)** - Comprehensive logging documentation
- **[Development Guide](../DEV_GUIDE.md)** - Development setup and workflows
- **[Docker Guide](../README_SWITCH.md)** - Container configuration

---

*Quick Reference - Last updated: January 2024* 