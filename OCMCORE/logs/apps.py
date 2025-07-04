"""
App configuration for logs app.
"""

from django.apps import AppConfig


class LogsConfig(AppConfig):
    """
    Configuration for logs app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    verbose_name = 'Logs'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import logs.signals
        except ImportError:
            pass
