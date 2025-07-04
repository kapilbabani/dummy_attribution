# Local Development with Memcached

This guide explains how to use Memcached in your local development environment.

## Quick Start (Recommended)

### 1. Using Docker for Memcached (Easiest)

```powershell
# Start development environment with Memcached
.\start-dev.ps1 memcached

# Or just (defaults to memcached mode)
.\start-dev.ps1
```

This will:
- Start Memcached in a Docker container
- Test the connection
- Start Django development server
- Load your environment variables

### 2. Stop Development Environment

```powershell
# Stop everything and clean up
.\stop-dev.ps1
```

## Alternative Setup Options

### Option 1: Docker Memcached (Recommended)

**Pros:**
- No local installation required
- Consistent with production environment
- Easy to start/stop
- Isolated from system

**Setup:**
1. Ensure Docker is installed and running
2. Use the provided scripts: `.\start-dev.ps1 memcached`

### Option 2: Local Memcached Installation

**Pros:**
- No Docker dependency
- Faster startup
- System-level installation

**Setup:**
1. Install Memcached on your system
2. Start Memcached service
3. Use: `.\start-dev.ps1 local`

### Option 3: No Memcached (Fallback)

**Pros:**
- No additional setup required
- Works without caching

**Setup:**
- Django will use the default cache backend (usually database or dummy cache)
- Caching will be disabled

## Installation Guides

### Windows - Local Memcached Installation

1. **Using Chocolatey:**
   ```powershell
   choco install memcached
   ```

2. **Using Scoop:**
   ```powershell
   scoop install memcached
   ```

3. **Manual Installation:**
   - Download from: https://memcached.org/downloads
   - Extract to a folder (e.g., `C:\memcached`)
   - Add to PATH
   - Start: `memcached -d -p 11211`

### macOS - Local Memcached Installation

```bash
# Using Homebrew
brew install memcached

# Start Memcached
brew services start memcached

# Or start manually
memcached -d -p 11211
```

### Linux - Local Memcached Installation

```bash
# Ubuntu/Debian
sudo apt-get install memcached

# CentOS/RHEL
sudo yum install memcached

# Start service
sudo systemctl start memcached
sudo systemctl enable memcached
```

## Environment Configuration

### 1. Create `.env` file for development

Copy `env.dev` to `.env` and update with your settings:

```env
# Database Configuration
MSSQL_DB=your_dev_db
MSSQL_USER=your_dev_user
MSSQL_PASSWORD=your_dev_password
MSSQL_HOST=your_dev_host
MSSQL_PORT=1433

# Memcached Configuration
MEMCACHED_HOST=localhost
MEMCACHED_PORT=11211

# Django Settings
DJANGO_SERVER_NAME=localhost
DJANGO_RUNSERVER_PORT=8000
```

### 2. Environment Variables Explained

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMCACHED_HOST` | Memcached server hostname | `localhost` |
| `MEMCACHED_PORT` | Memcached server port | `11211` |
| `DJANGO_RUNSERVER_PORT` | Django development server port | `8000` |

## Testing Memcached

### 1. Test Connection

```powershell
# Run the test script
python test_memcached.py
```

Expected output:
```
Testing Memcached connection...
✅ Memcached is working properly!
   Set/Get test passed: test_value
✅ Cache deletion test passed
✅ Cache timeout test passed

🎉 All Memcached tests passed!
```

### 2. Test API Endpoint with Caching

1. **Start your development server:**
   ```powershell
   .\start-dev.ps1 memcached
   ```

2. **Test without cache:**
   ```bash
   curl -X POST http://localhost:8000/api/genrate_attribution/ \
     -H "Content-Type: application/json" \
     -d '{
       "beg_date": "2024-01-01",
       "end_date": "2024-01-31",
       "id1": 1,
       "id2": 2,
       "attributes": ["attr1", "attr2"]
     }'
   ```

3. **Test with cache:**
   ```bash
   curl -X POST "http://localhost:8000/api/genrate_attribution/?cache=true" \
     -H "Content-Type: application/json" \
     -d '{
       "beg_date": "2024-01-01",
       "end_date": "2024-01-31",
       "id1": 1,
       "id2": 2,
       "attributes": ["attr1", "attr2"]
     }'
   ```

   **First call:** `"cached": false`
   **Second call:** `"cached": true`

## Using Caching in Your Code

### 1. Basic Caching

```python
from django.core.cache import cache

# Set a value (cache for 1 hour)
cache.set('my_key', 'my_value', 3600)

# Get a value
value = cache.get('my_key')

# Delete a value
cache.delete('my_key')
```

### 2. Caching API Responses

```python
from django.core.cache import cache
import hashlib
import json

def get_cached_data(parameters):
    # Create cache key from parameters
    cache_key = f"data_{hashlib.md5(json.dumps(parameters, sort_keys=True).encode()).hexdigest()}"
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result, True  # Return cached data
    
    # If not in cache, fetch from database
    result = fetch_from_database(parameters)
    
    # Cache the result for 1 hour
    cache.set(cache_key, result, 3600)
    
    return result, False  # Return fresh data
```

### 3. Cache Decorators

```python
from django.core.cache import cache
from functools import wraps

def cache_result(timeout=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

# Usage
@cache_result(timeout=1800)  # Cache for 30 minutes
def expensive_calculation(param1, param2):
    # Your expensive operation here
    return result
```

## Troubleshooting

### 1. Memcached Connection Issues

**Error:** `Connection refused`
**Solution:**
- Check if Memcached is running: `docker ps | grep memcached`
- Verify port 11211 is not blocked by firewall
- Try restarting Memcached container: `docker-compose -f docker-compose.dev.yml restart memcached`

### 2. Django Cache Errors

**Error:** `Cache backend not found`
**Solution:**
- Verify `django-pymemcache` is installed: `pip install django-pymemcache`
- Check cache configuration in `settings.py`

### 3. Performance Issues

**Slow cache operations:**
- Increase `max_pool_size` in cache options
- Check Memcached memory usage
- Consider using connection pooling

### 4. Cache Not Working

**Symptoms:** Cache hits always return `None`
**Solutions:**
- Run `python test_memcached.py` to verify connection
- Check environment variables
- Verify cache key generation

## Useful Commands

```powershell
# Start development with Memcached
.\start-dev.ps1 memcached

# Start development without Memcached
.\start-dev.ps1 local

# Stop development environment
.\stop-dev.ps1

# Test Memcached connection
python test_memcached.py

# Check Memcached container status
docker ps | grep memcached

# View Memcached logs
docker logs memcached

# Restart Memcached container
docker-compose -f docker-compose.dev.yml restart memcached
```

## Best Practices

1. **Use meaningful cache keys** that include relevant parameters
2. **Set appropriate timeouts** based on data freshness requirements
3. **Handle cache misses gracefully** - always have a fallback
4. **Monitor cache hit rates** to optimize caching strategy
5. **Use cache versioning** for major data structure changes
6. **Test caching behavior** in development before deploying

## Next Steps

1. Set up your `.env` file with your database credentials
2. Start development environment: `.\start-dev.ps1 memcached`
3. Test the caching functionality with your API endpoints
4. Add caching to other expensive operations in your code
5. Monitor performance and adjust cache settings as needed 