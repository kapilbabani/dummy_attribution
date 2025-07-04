# SimpleCache Developer Guide

## Overview

SimpleCache is a Memcached-backed caching system with key tracking, atomic dump operations, and automatic persistence. It's designed for Django applications running in Docker containers with robust data protection.

## 🚀 Quick Start

### 1. Basic Usage

```python
from core.simple_cache import simple_cache

# Set a value
simple_cache.set("user:123", {"name": "John", "email": "john@example.com"}, timeout=3600)

# Get a value
user_data = simple_cache.get("user:123")
if user_data:
    print(f"User: {user_data['name']}")

# Delete a key
simple_cache.delete("user:123")

# Refresh timeout
simple_cache.refresh("user:123", timeout=7200)
```

### 2. Cache Statistics

```python
# Get cache stats
stats = simple_cache.get_stats()
print(f"Cache size: {stats['size']}")
print(f"All keys: {stats['keys']}")
print(f"Auto-dump enabled: {stats['auto_dump_enabled']}")
```

## ⚙️ Configuration

### Environment Variables

Configure the cache behavior using environment variables:

```bash
# Cache dump file location
CACHE_DUMP_FILE=/tmp/cache_dump.json

# Maximum number of keys to track
CACHE_MAX_SIZE=1000

# Auto-dump interval in seconds (0 = disabled)
CACHE_AUTO_DUMP_INTERVAL=300
```

### Environment Files

The cache configuration is already set up in your environment files:

- `env.dev` - Development settings
- `env.windows` - Windows container settings  
- `env.linux` - Linux container settings

## 🔧 API Reference

### Core Methods

#### `set(key, value, timeout=3600)`
Store a value in cache with optional timeout.

```python
# Store simple data
simple_cache.set("config:app", {"version": "1.0", "debug": True})

# Store complex objects (automatically serialized)
simple_cache.set("user:session:456", user_session_object, timeout=1800)
```

#### `get(key)`
Retrieve a value from cache.

```python
# Get value
data = simple_cache.get("config:app")
if data:
    print(f"App version: {data['version']}")
else:
    print("Key not found or expired")
```

#### `delete(key)`
Remove a key from cache.

```python
# Delete specific key
simple_cache.delete("user:session:456")

# Delete multiple keys
for key in ["user:123", "user:456", "user:789"]:
    simple_cache.delete(key)
```

#### `refresh(key, timeout=3600)`
Extend the timeout for an existing key.

```python
# Refresh user session
if simple_cache.refresh("user:session:456", timeout=3600):
    print("Session refreshed")
else:
    print("Session not found")
```

#### `clear()`
Clear all cache data.

```python
# Clear entire cache
simple_cache.clear()
print("Cache cleared")
```

### Utility Methods

#### `size()`
Get current number of tracked keys.

```python
cache_size = simple_cache.size()
print(f"Cache contains {cache_size} keys")
```

#### `get_all_keys()`
Get list of all tracked keys.

```python
keys = simple_cache.get_all_keys()
print("All cache keys:", keys)

# Filter keys by pattern
user_keys = [k for k in keys if k.startswith("user:")]
print("User keys:", user_keys)
```

#### `get_stats()`
Get comprehensive cache statistics.

```python
stats = simple_cache.get_stats()
print(json.dumps(stats, indent=2))
```

## 🛡️ Atomic Dump Operations

The cache uses atomic dump operations to prevent corruption:

### How It Works

1. **Temporary File**: Data is written to `.tmp` file first
2. **Validation**: JSON integrity is verified
3. **Backup**: Old dump is backed up
4. **Atomic Move**: Temp file is moved to final location
5. **Cleanup**: Old backups are removed

### Manual Dump Operations

```python
import asyncio

# Async dump
success = await simple_cache.dump_cache()
if success:
    print("Cache dumped successfully")

# Sync dump
success = simple_cache.dump_cache_sync()
if success:
    print("Cache dumped successfully")
```

## 🔄 Auto-Dump Management

### Control Auto-Dump

```python
# Stop auto-dump
simple_cache.stop_auto_dump()

# Start auto-dump (restarts with current interval)
simple_cache.start_auto_dump()

# Change auto-dump interval
simple_cache.set_auto_dump_interval(600)  # 10 minutes
```

### Auto-Dump Configuration

```python
# Disable auto-dump
os.environ['CACHE_AUTO_DUMP_INTERVAL'] = '0'

# Set to 5 minutes
os.environ['CACHE_AUTO_DUMP_INTERVAL'] = '300'

# Set to 1 hour
os.environ['CACHE_AUTO_DUMP_INTERVAL'] = '3600'
```

## 📊 Cache Patterns

### 1. User Session Management

```python
class UserSessionManager:
    def __init__(self):
        self.cache = simple_cache
    
    def create_session(self, user_id: str, session_data: dict):
        key = f"session:{user_id}"
        self.cache.set(key, session_data, timeout=3600)
        return key
    
    def get_session(self, user_id: str):
        key = f"session:{user_id}"
        return self.cache.get(key)
    
    def refresh_session(self, user_id: str):
        key = f"session:{user_id}"
        return self.cache.refresh(key, timeout=3600)
    
    def delete_session(self, user_id: str):
        key = f"session:{user_id}"
        return self.cache.delete(key)
```

### 2. API Response Caching

```python
def cache_api_response(func):
    """Decorator to cache API responses"""
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = f"api:{func.__name__}:{hash(str(args) + str(kwargs))}"
        
        # Try to get from cache first
        cached_result = simple_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute function and cache result
        result = func(*args, **kwargs)
        simple_cache.set(cache_key, result, timeout=1800)  # 30 minutes
        
        return result
    return wrapper

# Usage
@cache_api_response
def get_user_profile(user_id: str):
    # Expensive database query
    return {"user_id": user_id, "profile": "data"}
```

### 3. Configuration Caching

```python
class ConfigManager:
    def __init__(self):
        self.cache = simple_cache
    
    def get_config(self, config_name: str):
        key = f"config:{config_name}"
        config = self.cache.get(key)
        
        if config is None:
            # Load from database/file
            config = self._load_config_from_source(config_name)
            self.cache.set(key, config, timeout=3600)  # 1 hour
        
        return config
    
    def update_config(self, config_name: str, new_config: dict):
        key = f"config:{config_name}"
        self.cache.set(key, new_config, timeout=3600)
        # Also update source
        self._save_config_to_source(config_name, new_config)
```

### 4. Rate Limiting

```python
class RateLimiter:
    def __init__(self):
        self.cache = simple_cache
    
    def check_rate_limit(self, user_id: str, action: str, limit: int, window: int):
        key = f"rate_limit:{user_id}:{action}"
        current_count = self.cache.get(key) or 0
        
        if current_count >= limit:
            return False
        
        # Increment counter
        self.cache.set(key, current_count + 1, timeout=window)
        return True
```

## 🔍 Monitoring and Debugging

### Cache Health Check

```python
def check_cache_health():
    """Check if cache is working properly"""
    try:
        # Test basic operations
        test_key = "health_check"
        test_value = {"timestamp": time.time()}
        
        # Set test value
        simple_cache.set(test_key, test_value, timeout=60)
        
        # Get test value
        retrieved_value = simple_cache.get(test_key)
        
        if retrieved_value and retrieved_value["timestamp"] == test_value["timestamp"]:
            print("✅ Cache is healthy")
            return True
        else:
            print("❌ Cache retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ Cache health check failed: {e}")
        return False
```

### Cache Performance Monitoring

```python
import time

def monitor_cache_performance():
    """Monitor cache performance metrics"""
    start_time = time.time()
    
    # Get cache stats
    stats = simple_cache.get_stats()
    
    # Measure operation speed
    test_key = "perf_test"
    simple_cache.set(test_key, "test_value")
    simple_cache.get(test_key)
    simple_cache.delete(test_key)
    
    end_time = time.time()
    operation_time = (end_time - start_time) * 1000  # milliseconds
    
    print(f"Cache Performance:")
    print(f"  Size: {stats['size']} keys")
    print(f"  Operation time: {operation_time:.2f}ms")
    print(f"  Auto-dump: {'Enabled' if stats['auto_dump_enabled'] else 'Disabled'}")
    print(f"  Dump interval: {stats['auto_dump_interval']}s")
```

## 🚨 Best Practices

### 1. Key Naming Convention

Use consistent, descriptive key names:

```python
# Good key patterns
simple_cache.set("user:profile:123", user_data)
simple_cache.set("config:app:production", config_data)
simple_cache.set("session:user:456", session_data)
simple_cache.set("rate_limit:api:user:789", count_data)

# Avoid generic keys
simple_cache.set("data", some_data)  # Bad
simple_cache.set("temp", temp_data)  # Bad
```

### 2. Timeout Strategy

```python
# Short-lived data (sessions, rate limits)
simple_cache.set("session:user:123", session_data, timeout=1800)  # 30 min

# Medium-lived data (API responses, user data)
simple_cache.set("user:profile:123", profile_data, timeout=3600)  # 1 hour

# Long-lived data (configurations, static data)
simple_cache.set("config:app", app_config, timeout=86400)  # 24 hours
```

### 3. Error Handling

```python
def safe_cache_operation(operation_func, *args, **kwargs):
    """Safely execute cache operations with error handling"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        print(f"Cache operation failed: {e}")
        # Fallback to database or default value
        return None

# Usage
user_data = safe_cache_operation(simple_cache.get, "user:123")
if user_data is None:
    # Load from database
    user_data = load_user_from_database(123)
```

### 4. Cache Warming

```python
def warm_cache():
    """Pre-load frequently accessed data into cache"""
    frequently_accessed_keys = [
        "config:app",
        "config:features",
        "static:menu_items",
        "static:categories"
    ]
    
    for key in frequently_accessed_keys:
        if simple_cache.get(key) is None:
            # Load from source and cache
            data = load_data_from_source(key)
            if data:
                simple_cache.set(key, data, timeout=3600)
                print(f"Warmed cache for: {key}")
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Cache Not Working
```python
# Check if Memcached is running
try:
    simple_cache.set("test", "value")
    result = simple_cache.get("test")
    if result == "value":
        print("✅ Memcached is working")
    else:
        print("❌ Memcached connection issue")
except Exception as e:
    print(f"❌ Memcached error: {e}")
```

#### 2. Keys Not Found
```python
# Check if key exists in registry
all_keys = simple_cache.get_all_keys()
if "your_key" in all_keys:
    print("Key exists in registry")
else:
    print("Key not in registry")

# Check if key expired
value = simple_cache.get("your_key")
if value is None:
    print("Key expired or doesn't exist")
```

#### 3. Auto-Dump Issues
```python
# Check auto-dump status
stats = simple_cache.get_stats()
print(f"Auto-dump enabled: {stats['auto_dump_enabled']}")
print(f"Auto-dump interval: {stats['auto_dump_interval']}s")

# Manually trigger dump
success = simple_cache.dump_cache_sync()
print(f"Manual dump: {'Success' if success else 'Failed'}")
```

## 📝 Integration Examples

### Django Views

```python
from django.http import JsonResponse
from core.simple_cache import simple_cache

def cached_user_view(request, user_id):
    # Try cache first
    cache_key = f"user:view:{user_id}"
    cached_data = simple_cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    # Load from database
    user_data = get_user_from_database(user_id)
    
    # Cache for 30 minutes
    simple_cache.set(cache_key, user_data, timeout=1800)
    
    return JsonResponse(user_data)
```

### Django Models

```python
from django.db import models
from core.simple_cache import simple_cache

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    def save(self, *args, **kwargs):
        # Save to database
        super().save(*args, **kwargs)
        
        # Update cache
        cache_key = f"user:model:{self.id}"
        simple_cache.set(cache_key, {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }, timeout=3600)
    
    def delete(self, *args, **kwargs):
        # Remove from cache first
        cache_key = f"user:model:{self.id}"
        simple_cache.delete(cache_key)
        
        # Delete from database
        super().delete(*args, **kwargs)
```

## 🎯 Summary

SimpleCache provides:

- ✅ **Memcached Backend**: Fast, distributed caching
- ✅ **Key Tracking**: Know what's in your cache
- ✅ **Atomic Dumps**: Corruption-free persistence
- ✅ **Auto-Dump**: Automatic backup scheduling
- ✅ **Environment Config**: Easy deployment configuration
- ✅ **Error Handling**: Robust operation with fallbacks
- ✅ **Monitoring**: Built-in statistics and health checks

Use this guide to implement efficient caching patterns in your Django application! 🚀 