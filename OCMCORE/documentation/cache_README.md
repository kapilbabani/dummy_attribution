# Cache App

## Overview

The Cache app provides centralized cache management functionality for the OCMCORE project. It includes both the core cache implementation (`simple_cache.py` at root level) and cache management APIs.

## Architecture

### Root Level Components
- **`simple_cache.py`** - Core cache implementation using Memcached
- **`cache_utils.py`** - Cache utility functions and services

### Cache App Components
- **`cache/views.py`** - Cache management API endpoints
- **`cache/urls.py`** - Cache app URL routing
- **`cache/tests.py`** - Cache app tests

## Usage

### For Other Apps
All apps can use the cache by importing from the root level:

```python
from simple_cache import simple_cache

# Basic cache operations
simple_cache.set('key', 'value', timeout=3600)
value = simple_cache.get('key')
simple_cache.delete('key')
```

### Cache Management APIs

#### Read-Only Operations (Available in all environments)
- `GET /api/cache/stats/` - Get cache statistics
- `GET /api/cache/keys/` - Get all cache keys
- `GET /api/cache/pattern/?pattern=regex` - Get keys by pattern
- `GET /api/cache/pattern/stats/?pattern=regex` - Get pattern statistics

#### Management Operations (Development only)
- `DELETE /api/cache/` - Clear all cache
- `POST /api/cache/` - Dump cache to file
- `DELETE /api/cache/key/{key}/` - Delete specific key
- `PUT /api/cache/key/{key}/` - Refresh key timeout
- `DELETE /api/cache/pattern/manage/` - Delete keys by pattern
- `PUT /api/cache/pattern/manage/` - Refresh keys by pattern
- `POST /api/cache/auto-dump/` - Start auto-dump
- `PUT /api/cache/auto-dump/` - Change auto-dump interval
- `DELETE /api/cache/auto-dump/` - Stop auto-dump

## Features

- **Environment-based access control** - Read-only in production, full access in development
- **Pattern-based operations** - Use regex to manage multiple keys
- **Auto-dump functionality** - Automatic cache persistence
- **Key tracking** - Maintain list of all cache keys
- **Atomic operations** - Safe cache dump operations

## Configuration

Cache configuration is handled through environment variables:
- `MEMCACHED_HOST` - Memcached server host
- `MEMCACHED_PORT` - Memcached server port
- `CACHE_AUTO_DUMP_INTERVAL` - Auto-dump interval in seconds
- `CACHE_DUMP_FILE` - Cache dump file path

## Testing

Run cache app tests:
```bash
python manage.py test cache
```

## Integration

The cache app is automatically included in the OCMCORE project and provides shared cache functionality to all other apps. 