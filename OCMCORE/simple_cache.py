"""
Simple Memcached Cache with Docker support, key tracking, and async dump/load functionality
"""

import json
import time
import asyncio
import os
import pickle
import threading
import shutil
import re
from typing import Any, Dict, Optional, List
from datetime import datetime
from django.core.cache import cache
import inspect
import importlib

# Dynamically load local apps from settings.py
try:
    settings = importlib.import_module('settings')
    INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])
    # Filter out Django and third-party apps
    LOCAL_APPS = [app for app in INSTALLED_APPS if app not in [
        'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
        'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
        'rest_framework', 'drf_yasg', 'corsheaders']]
except Exception:
    LOCAL_APPS = ['attribution', 'cache']  # fallback


def _get_calling_app():
    for frame_info in inspect.stack():
        module = inspect.getmodule(frame_info.frame)
        if not module or not hasattr(module, '__file__'):
            continue
        path = module.__file__
        for app in LOCAL_APPS:
            if f'/{app}/' in path.replace('\\', '/'):  # works for both Windows and Linux
                return app
    return None


def _app_scoped_key(key):
    app = _get_calling_app()
    if app and app != 'cache':
        return f"{app}:{key}"
    return key


# Helper to get the app-scoped registry key
def _app_scoped_registry_key():
    app = _get_calling_app()
    if app and app != 'cache':
        return f"{app}:cache_key_registry"
    return "cache_key_registry"


class SimpleCache:
    """Simple Memcached cache with key tracking and async dump/load functionality"""
    
    def __init__(self, dump_file: str = None, max_size: int = None, auto_dump_interval: int = None):
        # Get configuration from environment variables with defaults
        self.dump_file = dump_file or os.environ.get('CACHE_DUMP_FILE', '/tmp/cache_dump.json')
        self.max_size = max_size or int(os.environ.get('CACHE_MAX_SIZE', '1000'))
        self.auto_dump_interval = auto_dump_interval or int(os.environ.get('CACHE_AUTO_DUMP_INTERVAL', '300'))
        
        self.key_registry = set()  # Track all keys in memory
        self.dump_thread = None
        self.stop_dump_thread = False
        
        # Load cache and key registry on startup
        self.load_cache()
        
        # Start automatic periodic dumping
        self.start_auto_dump()
    
    def _get_temp_dump_file(self) -> str:
        """Get temporary dump file path"""
        return f"{self.dump_file}.tmp"
    
    def _atomic_dump_to_file(self, dump_data: Dict) -> bool:
        """Atomically dump data to file to prevent corruption"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.dump_file), exist_ok=True)
            
            # Create temporary file path
            temp_file = self._get_temp_dump_file()
            
            # Write to temporary file first
            with open(temp_file, 'w') as f:
                json.dump(dump_data, f, indent=2)
            
            # Ensure the file is written to disk
            f.flush()
            os.fsync(f.fileno())
            
            # Verify the temporary file was written correctly
            with open(temp_file, 'r') as f:
                # Try to load the JSON to verify it's valid
                json.load(f)
            
            # If we get here, the temporary file is valid
            # Now atomically replace the old file with the new one
            if os.path.exists(self.dump_file):
                # Create backup of old file
                backup_file = f"{self.dump_file}.backup"
                shutil.copy2(self.dump_file, backup_file)
                
                # Remove old backup if it exists
                old_backup = f"{self.dump_file}.backup.old"
                if os.path.exists(old_backup):
                    os.remove(old_backup)
                
                # Rename current backup to old backup
                if os.path.exists(backup_file):
                    os.rename(backup_file, old_backup)
            
            # Move temporary file to final location
            shutil.move(temp_file, self.dump_file)
            
            # Clean up old backup
            old_backup = f"{self.dump_file}.backup.old"
            if os.path.exists(old_backup):
                os.remove(old_backup)
            
            return True
            
        except Exception as e:
            print(f"Error in atomic dump: {e}")
            # Clean up temporary file if it exists
            temp_file = self._get_temp_dump_file()
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get keys matching a regex pattern"""
        try:
            regex = re.compile(pattern)
            matching_keys = [key for key in self.key_registry if regex.search(key)]
            return matching_keys
        except re.error as e:
            print(f"Invalid regex pattern '{pattern}': {e}")
            return []
    
    def get_values_by_pattern(self, pattern: str) -> Dict[str, Any]:
        """Get key-value pairs for keys matching a regex pattern"""
        try:
            matching_keys = self.get_keys_by_pattern(pattern)
            result = {}
            
            for key in matching_keys:
                value = self.get(key)
                if value is not None:  # Only include non-expired keys
                    result[key] = value
            
            return result
        except Exception as e:
            print(f"Error getting values by pattern '{pattern}': {e}")
            return {}
    
    def delete_keys_by_pattern(self, pattern: str) -> int:
        """Delete all keys matching a regex pattern. Returns number of deleted keys."""
        try:
            matching_keys = self.get_keys_by_pattern(pattern)
            deleted_count = 0
            
            for key in matching_keys:
                if self.delete(key):
                    deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Error deleting keys by pattern '{pattern}': {e}")
            return 0
    
    def refresh_keys_by_pattern(self, pattern: str, timeout: int = 3600) -> int:
        """Refresh timeout for all keys matching a regex pattern. Returns number of refreshed keys."""
        try:
            matching_keys = self.get_keys_by_pattern(pattern)
            refreshed_count = 0
            
            for key in matching_keys:
                if self.refresh(key, timeout):
                    refreshed_count += 1
            
            return refreshed_count
        except Exception as e:
            print(f"Error refreshing keys by pattern '{pattern}': {e}")
            return 0
    
    def get_pattern_stats(self, pattern: str) -> Dict:
        """Get statistics for keys matching a pattern"""
        try:
            matching_keys = self.get_keys_by_pattern(pattern)
            values = self.get_values_by_pattern(pattern)
            
            return {
                'pattern': pattern,
                'total_matching_keys': len(matching_keys),
                'active_keys': len(values),  # Non-expired keys
                'expired_keys': len(matching_keys) - len(values),
                'matching_keys': matching_keys,
                'active_values': values
            }
        except Exception as e:
            print(f"Error getting pattern stats for '{pattern}': {e}")
            return {'error': str(e)}
    
    def start_auto_dump(self):
        """Start automatic periodic dumping"""
        def dump_worker():
            while not self.stop_dump_thread:
                try:
                    time.sleep(self.auto_dump_interval)
                    if not self.stop_dump_thread:  # Check again after sleep
                        success = self.dump_cache_sync()
                        if success:
                            print(f"🔄 Auto-dumped cache at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {len(self.key_registry)} keys")
                        else:
                            print(f"❌ Auto-dump failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    print(f"❌ Auto-dump error: {e}")
        
        if self.auto_dump_interval > 0:
            self.dump_thread = threading.Thread(target=dump_worker, daemon=True)
            self.dump_thread.start()
            print(f"🚀 Auto-dump started with {self.auto_dump_interval}s interval (from env: CACHE_AUTO_DUMP_INTERVAL)")
        else:
            print("🛑 Auto-dump disabled (CACHE_AUTO_DUMP_INTERVAL=0)")
    
    def stop_auto_dump(self):
        """Stop automatic periodic dumping"""
        self.stop_dump_thread = True
        if self.dump_thread and self.dump_thread.is_alive():
            self.dump_thread.join(timeout=5)
        print("🛑 Auto-dump stopped")
    
    def set_auto_dump_interval(self, interval_seconds: int):
        """Change auto-dump interval"""
        old_interval = self.auto_dump_interval
        self.auto_dump_interval = interval_seconds
        
        if old_interval != interval_seconds:
            # Restart auto-dump with new interval
            self.stop_auto_dump()
            self.stop_dump_thread = False
            self.start_auto_dump()
            print(f"⏰ Auto-dump interval changed to {interval_seconds}s")
    
    def set(self, key: str, value: Any, timeout: int = 3600) -> None:
        """Set a key-value pair in Memcached cache"""
        try:
            # Serialize value for storage
            serialized_value = pickle.dumps(value)
            cache.set(key, serialized_value, timeout)
            
            # Add to key registry
            self.key_registry.add(key)
            self._save_key_registry()
            
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key from Memcached cache"""
        try:
            serialized_value = cache.get(key)
            if serialized_value is not None:
                # Deserialize value
                return pickle.loads(serialized_value)
            else:
                # Key doesn't exist or expired, remove from registry
                self.key_registry.discard(key)
                self._save_key_registry()
            return None
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Memcached cache"""
        try:
            cache.delete(key)
            # Remove from key registry
            self.key_registry.discard(key)
            self._save_key_registry()
            return True
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")
            return False
    
    def refresh(self, key: str, timeout: int = 3600) -> bool:
        """Refresh timeout for a key in Memcached cache"""
        try:
            # Get current value
            serialized_value = cache.get(key)
            if serialized_value is not None:
                # Set with new timeout
                cache.set(key, serialized_value, timeout)
                return True
            else:
                # Key doesn't exist, remove from registry
                self.key_registry.discard(key)
                self._save_key_registry()
            return False
        except Exception as e:
            print(f"Error refreshing cache key {key}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all Memcached cache"""
        try:
            cache.clear()
            # Clear key registry
            self.key_registry.clear()
            self._save_key_registry()
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.key_registry)
    
    def get_all_keys(self) -> List[str]:
        """Get list of all tracked keys"""
        return list(self.key_registry)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            return {
                'size': self.size(),
                'max_size': self.max_size,
                'keys': self.get_all_keys(),
                'dump_file': self.dump_file,
                'cache_backend': 'memcached',
                'auto_dump_interval': self.auto_dump_interval,
                'auto_dump_enabled': self.auto_dump_interval > 0,
                'env_config': {
                    'CACHE_DUMP_FILE': os.environ.get('CACHE_DUMP_FILE', '/tmp/cache_dump.json'),
                    'CACHE_MAX_SIZE': os.environ.get('CACHE_MAX_SIZE', '1000'),
                    'CACHE_AUTO_DUMP_INTERVAL': os.environ.get('CACHE_AUTO_DUMP_INTERVAL', '300')
                }
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def _save_key_registry(self) -> None:
        """Save key registry to Memcached"""
        try:
            cache.set(self.registry_key, list(self.key_registry), timeout=None)
        except Exception as e:
            print(f"Error saving key registry: {e}")
    
    def _load_key_registry(self) -> None:
        """Load key registry from Memcached"""
        try:
            serialized_registry = cache.get(self.registry_key)
            if serialized_registry is not None:
                self.key_registry = pickle.loads(serialized_registry)
            else:
                self.key_registry = set()
        except Exception as e:
            print(f"Error loading key registry: {e}")
            self.key_registry = set()
    
    def _cleanup_expired_keys(self) -> None:
        """Remove expired keys from registry by checking each key"""
        try:
            expired_keys = set()
            for key in self.key_registry:
                if cache.get(key) is None:  # Key doesn't exist or expired
                    expired_keys.add(key)
            
            # Remove expired keys from registry
            self.key_registry -= expired_keys
            self._save_key_registry()
            
            if expired_keys:
                print(f"Cleaned up {len(expired_keys)} expired keys from registry")
                
        except Exception as e:
            print(f"Error cleaning up expired keys: {e}")
    
    async def dump_cache(self) -> bool:
        """Async dump cache to file"""
        try:
            # Clean up expired keys first
            self._cleanup_expired_keys()
            
            dump_data = {
                'timestamp': datetime.now().isoformat(),
                'cache_backend': 'memcached',
                'key_registry': list(self.key_registry),
                'total_keys': len(self.key_registry),
                'auto_dump_interval': self.auto_dump_interval,
                'env_config': {
                    'CACHE_DUMP_FILE': os.environ.get('CACHE_DUMP_FILE', '/tmp/cache_dump.json'),
                    'CACHE_MAX_SIZE': os.environ.get('CACHE_MAX_SIZE', '1000'),
                    'CACHE_AUTO_DUMP_INTERVAL': os.environ.get('CACHE_AUTO_DUMP_INTERVAL', '300')
                }
            }
            
            # Use atomic dump
            return self._atomic_dump_to_file(dump_data)
            
        except Exception as e:
            print(f"Error dumping cache: {e}")
            return False
    
    def load_cache(self) -> bool:
        """Load cache from file on startup"""
        try:
            # Load key registry from Memcached
            self._load_key_registry()
            
            if os.path.exists(self.dump_file):
                with open(self.dump_file, 'r') as f:
                    dump_data = json.load(f)
                
                print(f"Cache metadata loaded from {self.dump_file}")
                print(f"Key registry loaded: {len(self.key_registry)} keys")
                return True
            else:
                print(f"No cache dump file found at {self.dump_file}")
                print(f"Memcached cache will start fresh")
                return False
        except Exception as e:
            print(f"Error loading cache: {e}")
            return False
    
    def dump_cache_sync(self) -> bool:
        """Synchronous dump cache to file"""
        try:
            # Clean up expired keys first
            self._cleanup_expired_keys()
            
            dump_data = {
                'timestamp': datetime.now().isoformat(),
                'cache_backend': 'memcached',
                'key_registry': list(self.key_registry),
                'total_keys': len(self.key_registry),
                'auto_dump_interval': self.auto_dump_interval,
                'env_config': {
                    'CACHE_DUMP_FILE': os.environ.get('CACHE_DUMP_FILE', '/tmp/cache_dump.json'),
                    'CACHE_MAX_SIZE': os.environ.get('CACHE_MAX_SIZE', '1000'),
                    'CACHE_AUTO_DUMP_INTERVAL': os.environ.get('CACHE_AUTO_DUMP_INTERVAL', '300')
                }
            }
            
            # Use atomic dump
            return self._atomic_dump_to_file(dump_data)
            
        except Exception as e:
            print(f"Error dumping cache: {e}")
            return False

    @property
    def registry_key(self):
        return _app_scoped_registry_key()

# Global cache instance with environment-based configuration
simple_cache = SimpleCache() 

# Patch all public cache operations to use app-scoped keys
class SimpleCache(SimpleCache):
    def set(self, key: str, value: Any, timeout: int = 3600) -> None:
        return super().set(_app_scoped_key(key), value, timeout)

    def get(self, key: str) -> Optional[Any]:
        return super().get(_app_scoped_key(key))

    def delete(self, key: str) -> bool:
        return super().delete(_app_scoped_key(key))

    def refresh(self, key: str, timeout: int = 3600) -> bool:
        return super().refresh(_app_scoped_key(key), timeout)

    def _save_key_registry(self) -> None:
        # Save the key registry to Memcached under the app-scoped registry key
        cache.set(self.registry_key, list(self.key_registry), timeout=None)

    def _load_key_registry(self) -> None:
        # Load the key registry from Memcached under the app-scoped registry key
        keys = cache.get(self.registry_key)
        if keys:
            self.key_registry = set(keys)
        else:
            self.key_registry = set()

    # Optionally, add a method for the cache app to get all registries
    def get_all_registries(self):
        registries = {}
        for app in LOCAL_APPS:
            key = f"{app}:cache_key_registry"
            keys = cache.get(key)
            if keys:
                registries[app] = set(keys)
        # Also include the global registry if present
        global_keys = cache.get("cache_key_registry")
        if global_keys:
            registries['global'] = set(global_keys)
        return registries

# Global cache instance with environment-based configuration
simple_cache = SimpleCache() 