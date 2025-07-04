"""
App configuration for attribution app.
"""

from django.apps import AppConfig


class AttributionConfig(AppConfig):
    """
    Configuration for attribution app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attribution'
    verbose_name = 'Attribution Management'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import attribution.signals
        except ImportError:
            pass 