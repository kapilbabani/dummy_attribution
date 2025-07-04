"""
Cache management views for cache app.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from cache_utils import (
    get_cache_stats, 
    get_all_cache_keys,
    get_keys_by_pattern,
    get_values_by_pattern,
    get_pattern_stats,
    clear_cache,
    delete_cache_key,
    refresh_cache_key,
    dump_cache_sync,
    set_auto_dump_interval,
    stop_auto_dump,
    start_auto_dump,
    delete_keys_by_pattern,
    refresh_keys_by_pattern,
    get_all_app_registries,
    get_app_cache_stats,
    get_all_apps_cache_stats,
    clear_app_cache,
    get_app_keys_by_pattern
)

class EnvironmentMixin:
    """Mixin to check environment and restrict operations accordingly"""
    
    def _is_development(self):
        """Check if we're in development environment"""
        # Check Django DEBUG setting
        if getattr(settings, 'DEBUG', False):
            return True
        
        # Check environment variable
        import os
        env = os.environ.get('DJANGO_ENV', '').lower()
        if env in ['dev', 'development', 'local']:
            return True
        
        # Check if we're running locally (common development indicators)
        if getattr(settings, 'ALLOWED_HOSTS', ['*']) == ['*']:
            return True
        
        return False
    
    def _check_development_only(self):
        """Check if operation is allowed in current environment"""
        if not self._is_development():
            return Response(
                {
                    'error': 'This operation is only available in development environment',
                    'message': 'Modification operations are disabled in production for security reasons'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return None

class CacheStats(APIView):
    """
    Get cache statistics (Available in all environments)
    """
    def get(self, request):
        stats = get_cache_stats()
        return Response(stats, status=status.HTTP_200_OK)

class CacheKeys(APIView):
    """
    Get all cache keys (Available in all environments)
    """
    def get(self, request):
        keys_data = get_all_cache_keys()
        return Response(keys_data, status=status.HTTP_200_OK)

class CacheManagement(EnvironmentMixin, APIView):
    """
    Cache management operations (Development only)
    """
    def delete(self, request):
        """Clear all cache - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        result = clear_cache()
        return Response(result, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Dump cache to file - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        result = dump_cache_sync()
        return Response(result, status=status.HTTP_200_OK)

class CacheKeyManagement(EnvironmentMixin, APIView):
    """
    Manage individual cache keys (Development only)
    """
    def delete(self, request, key):
        """Delete a specific cache key - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        result = delete_cache_key(key)
        return Response(result, status=status.HTTP_200_OK)
    
    def put(self, request, key):
        """Refresh timeout for a cache key - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        timeout = request.data.get('timeout', 3600)
        result = refresh_cache_key(key, timeout)
        return Response(result, status=status.HTTP_200_OK)

class CachePatternView(APIView):
    """
    View cache keys and values by pattern (Available in all environments)
    """
    def get(self, request):
        """Get keys and values by pattern"""
        pattern = request.query_params.get('pattern')
        if not pattern:
            return Response(
                {'error': 'Pattern parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if we want just keys or values
        get_values = request.query_params.get('values', 'false').lower() == 'true'
        
        if get_values:
            result = get_values_by_pattern(pattern)
        else:
            result = get_keys_by_pattern(pattern)
        
        return Response(result, status=status.HTTP_200_OK)

class CachePatternManagement(EnvironmentMixin, APIView):
    """
    Manage cache keys by pattern using regex (Development only)
    """
    def delete(self, request):
        """Delete keys by pattern - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        pattern = request.data.get('pattern')
        if not pattern:
            return Response(
                {'error': 'Pattern parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = delete_keys_by_pattern(pattern)
        return Response({
            'message': f'Deleted {deleted_count} keys matching pattern',
            'deleted_count': deleted_count,
            'pattern': pattern
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Refresh timeout for keys by pattern - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        pattern = request.data.get('pattern')
        timeout = request.data.get('timeout', 3600)
        
        if not pattern:
            return Response(
                {'error': 'Pattern parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refreshed_count = refresh_keys_by_pattern(pattern, timeout)
        return Response({
            'message': f'Refreshed {refreshed_count} keys matching pattern',
            'refreshed_count': refreshed_count,
            'pattern': pattern,
            'timeout': timeout
        }, status=status.HTTP_200_OK)

class CachePatternStats(APIView):
    """
    Get statistics for keys matching a pattern (Available in all environments)
    """
    def get(self, request):
        """Get pattern statistics"""
        pattern = request.query_params.get('pattern')
        if not pattern:
            return Response(
                {'error': 'Pattern parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stats = get_pattern_stats(pattern)
        return Response(stats, status=status.HTTP_200_OK)

class AutoDumpControl(EnvironmentMixin, APIView):
    """
    Control auto-dump functionality (Development only)
    """
    def post(self, request):
        """Start auto-dump with specified interval - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        interval_seconds = request.data.get('interval_seconds', 300)
        result = start_auto_dump(interval_seconds)
        return Response(result, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Change auto-dump interval - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        interval_seconds = request.data.get('interval_seconds', 300)
        result = set_auto_dump_interval(interval_seconds)
        return Response(result, status=status.HTTP_200_OK)
    
    def delete(self, request):
        """Stop auto-dump - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        result = stop_auto_dump()
        return Response(result, status=status.HTTP_200_OK)

class AppCacheStats(APIView):
    """
    Get cache statistics for all apps (Available in all environments)
    """
    def get(self, request):
        """Get cache statistics for all apps"""
        stats = get_all_apps_cache_stats()
        return Response(stats, status=status.HTTP_200_OK)

class AppCacheRegistry(APIView):
    """
    Get all app cache registries (Available in all environments)
    """
    def get(self, request):
        """Get all app cache registries"""
        registries = get_all_app_registries()
        return Response(registries, status=status.HTTP_200_OK)

class SingleAppCacheStats(APIView):
    """
    Get cache statistics for a specific app (Available in all environments)
    """
    def get(self, request, app_name):
        """Get cache statistics for a specific app"""
        stats = get_app_cache_stats(app_name)
        return Response(stats, status=status.HTTP_200_OK)

class SingleAppCacheManagement(EnvironmentMixin, APIView):
    """
    Manage cache for a specific app (Development only)
    """
    def delete(self, request, app_name):
        """Clear cache for a specific app - Development only"""
        check = self._check_development_only()
        if check:
            return check
        
        result = clear_app_cache(app_name)
        return Response(result, status=status.HTTP_200_OK)

class AppPatternView(APIView):
    """
    View cache keys by pattern for a specific app (Available in all environments)
    """
    def get(self, request, app_name):
        """Get keys by pattern for a specific app"""
        pattern = request.query_params.get('pattern')
        if not pattern:
            return Response(
                {'error': 'Pattern parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = get_app_keys_by_pattern(app_name, pattern)
        return Response(result, status=status.HTTP_200_OK) 