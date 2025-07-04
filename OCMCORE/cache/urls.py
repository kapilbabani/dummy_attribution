"""
URL configuration for cache app.
"""

from django.urls import path
from cache.views import (
    CacheStats, 
    CacheKeys, 
    CacheManagement,
    CacheKeyManagement,
    CachePatternView,
    CachePatternManagement,
    CachePatternStats,
    AutoDumpControl,
    AppCacheStats,
    AppCacheRegistry,
    SingleAppCacheStats,
    SingleAppCacheManagement,
    AppPatternView
)

urlpatterns = [
    # Cache statistics and monitoring
    path('stats/', CacheStats.as_view(), name='cache-stats'),
    path('keys/', CacheKeys.as_view(), name='cache-keys'),
    
    # Cache management operations
    path('', CacheManagement.as_view(), name='cache-management'),
    path('key/<str:key>/', CacheKeyManagement.as_view(), name='cache-key-management'),
    
    # Pattern-based operations
    path('pattern/', CachePatternView.as_view(), name='cache-pattern-view'),
    path('pattern/manage/', CachePatternManagement.as_view(), name='cache-pattern-management'),
    path('pattern/stats/', CachePatternStats.as_view(), name='cache-pattern-stats'),
    
    # Auto-dump control
    path('auto-dump/', AutoDumpControl.as_view(), name='auto-dump-control'),
    
    # App-specific cache operations
    path('apps/stats/', AppCacheStats.as_view(), name='app-cache-stats'),
    path('apps/registry/', AppCacheRegistry.as_view(), name='app-cache-registry'),
    path('apps/<str:app_name>/stats/', SingleAppCacheStats.as_view(), name='single-app-cache-stats'),
    path('apps/<str:app_name>/', SingleAppCacheManagement.as_view(), name='single-app-cache-management'),
    path('apps/<str:app_name>/pattern/', AppPatternView.as_view(), name='app-pattern-view'),
] 