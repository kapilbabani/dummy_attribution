"""
Cache-specific services for managing Memcached cache operations
"""

from simple_cache import simple_cache

# Read-only cache operations (Available in all environments)
def get_cache_stats():
    """Get cache statistics (Available in all environments)"""
    return simple_cache.get_stats()

def get_all_cache_keys():
    """Get list of all cache keys (Available in all environments)"""
    return {
        'keys': simple_cache.get_all_keys(),
        'total_keys': len(simple_cache.get_all_keys())
    }

# Pattern-based cache viewing operations (Available in all environments)
def get_keys_by_pattern(pattern):
    """Get keys matching a regex pattern (Available in all environments)"""
    keys = simple_cache.get_keys_by_pattern(pattern)
    return {
        'pattern': pattern,
        'keys': keys,
        'count': len(keys)
    }

def get_values_by_pattern(pattern):
    """Get key-value pairs for keys matching a regex pattern (Available in all environments)"""
    values = simple_cache.get_values_by_pattern(pattern)
    return {
        'pattern': pattern,
        'values': values,
        'count': len(values)
    }

def get_pattern_stats(pattern):
    """Get statistics for keys matching a pattern (Available in all environments)"""
    return simple_cache.get_pattern_stats(pattern)

# Cache management operations (Development only)
def clear_cache():
    """Clear all cache (Development only)"""
    simple_cache.clear()
    return {"message": "Cache cleared successfully"}

def delete_cache_key(key):
    """Delete a specific cache key (Development only)"""
    success = simple_cache.delete(key)
    return {"message": f"Key '{key}' {'deleted' if success else 'not found'}"}

def refresh_cache_key(key, timeout=3600):
    """Refresh timeout for a cache key (Development only)"""
    success = simple_cache.refresh(key, timeout)
    return {"message": f"Key '{key}' {'refreshed' if success else 'not found'}"}

def dump_cache_sync():
    """Synchronous dump cache to file (Development only)"""
    success = simple_cache.dump_cache_sync()
    return {"message": f"Cache {'dumped' if success else 'failed to dump'} to {simple_cache.dump_file}"}

def set_auto_dump_interval(interval_seconds):
    """Set auto-dump interval (Development only)"""
    simple_cache.set_auto_dump_interval(interval_seconds)
    return {
        "message": f"Auto-dump interval set to {interval_seconds} seconds",
        "interval_seconds": interval_seconds
    }

def stop_auto_dump():
    """Stop auto-dump (Development only)"""
    simple_cache.stop_auto_dump()
    return {"message": "Auto-dump stopped"}

def start_auto_dump(interval_seconds=300):
    """Start auto-dump with specified interval (Development only)"""
    simple_cache.set_auto_dump_interval(interval_seconds)
    return {
        "message": f"Auto-dump started with {interval_seconds}s interval",
        "interval_seconds": interval_seconds
    }

# Pattern-based cache management operations (Development only)
def delete_keys_by_pattern(pattern):
    """Delete all keys matching a regex pattern (Development only)"""
    deleted_count = simple_cache.delete_keys_by_pattern(pattern)
    return deleted_count

def refresh_keys_by_pattern(pattern, timeout=3600):
    """Refresh timeout for all keys matching a regex pattern (Development only)"""
    refreshed_count = simple_cache.refresh_keys_by_pattern(pattern, timeout)
    return refreshed_count

# App-specific cache operations (Available in all environments)
def get_all_app_registries():
    """Get all app cache registries (Available in all environments)"""
    registries = simple_cache.get_all_registries()
    return {
        'registries': registries,
        'total_apps': len(registries),
        'app_names': list(registries.keys())
    }

def get_app_cache_stats(app_name):
    """Get cache statistics for a specific app (Available in all environments)"""
    registries = simple_cache.get_all_registries()
    if app_name not in registries:
        return {
            'error': f'App "{app_name}" not found',
            'available_apps': list(registries.keys())
        }
    
    app_keys = registries[app_name]
    active_keys = []
    expired_keys = []
    
    for key in app_keys:
        value = simple_cache.get(key)
        if value is not None:
            active_keys.append(key)
        else:
            expired_keys.append(key)
    
    return {
        'app_name': app_name,
        'total_keys': len(app_keys),
        'active_keys': len(active_keys),
        'expired_keys': len(expired_keys),
        'active_key_list': active_keys,
        'expired_key_list': expired_keys
    }

def get_all_apps_cache_stats():
    """Get cache statistics for all apps (Available in all environments)"""
    registries = simple_cache.get_all_registries()
    all_stats = {}
    
    for app_name in registries.keys():
        all_stats[app_name] = get_app_cache_stats(app_name)
    
    return {
        'apps_stats': all_stats,
        'total_apps': len(all_stats)
    }

def clear_app_cache(app_name):
    """Clear cache for a specific app (Development only)"""
    registries = simple_cache.get_all_registries()
    if app_name not in registries:
        return {
            'error': f'App "{app_name}" not found',
            'available_apps': list(registries.keys())
        }
    
    app_keys = registries[app_name]
    deleted_count = 0
    
    for key in app_keys:
        if simple_cache.delete(key):
            deleted_count += 1
    
    return {
        'message': f'Cleared {deleted_count} keys for app "{app_name}"',
        'app_name': app_name,
        'deleted_count': deleted_count,
        'total_keys': len(app_keys)
    }

def get_app_keys_by_pattern(app_name, pattern):
    """Get keys matching a pattern for a specific app (Available in all environments)"""
    registries = simple_cache.get_all_registries()
    if app_name not in registries:
        return {
            'error': f'App "{app_name}" not found',
            'available_apps': list(registries.keys())
        }
    
    app_keys = registries[app_name]
    import re
    
    try:
        regex = re.compile(pattern)
        matching_keys = [key for key in app_keys if regex.search(key)]
        return {
            'app_name': app_name,
            'pattern': pattern,
            'matching_keys': matching_keys,
            'count': len(matching_keys)
        }
    except re.error as e:
        return {
            'error': f'Invalid regex pattern "{pattern}": {e}',
            'app_name': app_name
        } 