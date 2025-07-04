# SimpleCache Quick Reference

## 🚀 Basic Operations

```python
from core.simple_cache import simple_cache

# Set value
simple_cache.set("key", value, timeout=3600)

# Get value
value = simple_cache.get("key")

# Delete key
simple_cache.delete("key")

# Refresh timeout
simple_cache.refresh("key", timeout=3600)

# Clear all
simple_cache.clear()
```

## 📊 Monitoring

```python
# Get stats
stats = simple_cache.get_stats()

# Get size
size = simple_cache.size()

# Get all keys
keys = simple_cache.get_all_keys()
```

## 🔍 Pattern-Based Operations

```python
# Get keys by regex pattern
keys = simple_cache.get_keys_by_pattern(r"user:profile:\d+")

# Get values by regex pattern
values = simple_cache.get_values_by_pattern(r"user:.*")

# Delete keys by pattern
deleted_count = simple_cache.delete_keys_by_pattern(r"temp:.*")

# Refresh keys by pattern
refreshed_count = simple_cache.refresh_keys_by_pattern(r"user:session:\d+", timeout=7200)

# Get pattern statistics
stats = simple_cache.get_pattern_stats(r"user:.*")
```

## 🔄 Dump Operations

```python
# Manual dump (sync)
success = simple_cache.dump_cache_sync()

# Manual dump (async)
success = await simple_cache.dump_cache()

# Control auto-dump
simple_cache.stop_auto_dump()
simple_cache.start_auto_dump()
simple_cache.set_auto_dump_interval(600)  # 10 minutes
```

## ⚙️ Environment Variables

```bash
CACHE_DUMP_FILE=/tmp/cache_dump.json
CACHE_MAX_SIZE=1000
CACHE_AUTO_DUMP_INTERVAL=300
```

## 🎯 Common Patterns

### User Session
```python
# Store session
simple_cache.set(f"session:{user_id}", session_data, timeout=3600)

# Get session
session = simple_cache.get(f"session:{user_id}")

# Refresh session
simple_cache.refresh(f"session:{user_id}", timeout=3600)

# Get all user sessions
all_sessions = simple_cache.get_values_by_pattern(r"session:\d+")
```

### API Response Caching
```python
# Cache key pattern
cache_key = f"api:{endpoint}:{hash(params)}"
cached = simple_cache.get(cache_key)
if not cached:
    cached = expensive_operation()
    simple_cache.set(cache_key, cached, timeout=1800)

# Get all API responses
api_responses = simple_cache.get_values_by_pattern(r"api:.*")
```

### Configuration
```python
# Store config
simple_cache.set("config:app", config_data, timeout=86400)

# Get config
config = simple_cache.get("config:app")

# Get all configs
all_configs = simple_cache.get_values_by_pattern(r"config:.*")
```

### Rate Limiting
```python
# Check rate limit
key = f"rate_limit:{user_id}:{action}"
count = simple_cache.get(key) or 0
if count < limit:
    simple_cache.set(key, count + 1, timeout=window)

# Get all rate limits
rate_limits = simple_cache.get_values_by_pattern(r"rate_limit:.*")
```

## 🔍 Health Check

```python
def cache_health_check():
    test_key = "health_check"
    test_value = {"test": True}
    
    simple_cache.set(test_key, test_value, timeout=60)
    result = simple_cache.get(test_key)
    
    if result and result["test"]:
        print("✅ Cache healthy")
        return True
    else:
        print("❌ Cache unhealthy")
        return False
```

## 🚨 Error Handling

```python
def safe_cache_get(key, default=None):
    try:
        return simple_cache.get(key) or default
    except Exception as e:
        print(f"Cache error: {e}")
        return default
```

## 📝 Key Naming Convention

```
user:profile:123          # User data
session:user:456          # Session data
config:app:production     # Configuration
rate_limit:api:user:789   # Rate limiting
api:response:hash         # API responses
```

## ⏱️ Timeout Strategy

```python
# Short-lived (sessions, rate limits)
timeout=1800    # 30 minutes

# Medium-lived (API responses, user data)
timeout=3600    # 1 hour

# Long-lived (configurations, static data)
timeout=86400   # 24 hours
```

## 🔧 Troubleshooting

### Cache Not Working
```python
# Test basic operations
simple_cache.set("test", "value")
result = simple_cache.get("test")
print("Working" if result == "value" else "Broken")
```

### Keys Missing
```python
# Check registry
all_keys = simple_cache.get_all_keys()
print("Your key in registry:", "your_key" in all_keys)

# Check if expired
value = simple_cache.get("your_key")
print("Key exists:", value is not None)
```

### Auto-Dump Issues
```python
# Check status
stats = simple_cache.get_stats()
print(f"Auto-dump: {stats['auto_dump_enabled']}")
print(f"Interval: {stats['auto_dump_interval']}s")

# Manual dump
success = simple_cache.dump_cache_sync()
print(f"Dump: {'Success' if success else 'Failed'}")
```

### Pattern Issues
```python
# Test pattern matching
keys = simple_cache.get_keys_by_pattern(r"your:pattern")
print(f"Pattern matched {len(keys)} keys")

# Check pattern syntax
try:
    simple_cache.get_keys_by_pattern(r"invalid[pattern")
except Exception as e:
    print(f"Invalid regex: {e}")
```

## 🌐 API Endpoints (READ-ONLY)

### Cache Viewing
```bash
# Get cache statistics
GET /api/cache/stats/

# Get all cache keys
GET /api/cache/keys/

# Get keys by pattern
GET /api/cache/pattern/?pattern=user:profile:\d+

# Get values by pattern
GET /api/cache/pattern/?pattern=user:.*&values=true

# Get pattern statistics
GET /api/cache/pattern/stats/?pattern=user:.*
```

### API Response Examples

#### Cache Statistics
```json
{
  "size": 15,
  "max_size": 1000,
  "keys": ["user:profile:123", "config:app", ...],
  "cache_backend": "memcached",
  "auto_dump_enabled": true,
  "auto_dump_interval": 300
}
```

#### Pattern Keys
```json
{
  "pattern": "user:profile:\\d+",
  "keys": ["user:profile:123", "user:profile:456"],
  "count": 2
}
```

#### Pattern Values
```json
{
  "pattern": "user:profile:\\d+",
  "values": {
    "user:profile:123": {"name": "John", "email": "john@example.com"},
    "user:profile:456": {"name": "Jane", "email": "jane@example.com"}
  },
  "count": 2
}
```

#### Pattern Statistics
```json
{
  "pattern": "user:.*",
  "total_matching_keys": 4,
  "active_keys": 3,
  "expired_keys": 1,
  "matching_keys": ["user:profile:123", "user:session:456", ...],
  "active_values": {...}
}
```

## 🎯 Best Practices

1. **Use descriptive key names** with colons for hierarchy
2. **Set appropriate timeouts** based on data volatility
3. **Handle cache misses gracefully** with fallbacks
4. **Monitor cache performance** regularly
5. **Use atomic operations** for critical data
6. **Implement error handling** for all cache operations
7. **Use regex patterns** for bulk operations
8. **Test regex patterns** before using in production
9. **API is read-only** - use direct cache methods for modifications 