"""
App configuration for cache app.
"""

from django.apps import AppConfig


class CacheConfig(AppConfig):
    """
    Configuration for cache app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cache'
    verbose_name = 'Cache Management'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import cache.signals
        except ImportError:
            pass 