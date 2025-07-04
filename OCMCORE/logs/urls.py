"""
URL configuration for logs app.
"""

from django.urls import path
from logs.views import (
    LogFilesView,
    LogContentView,
    AppLogsView,
    LogStatsView,
    RealTimeLogsView,
    LogHealthView,
    LogWebView
)

urlpatterns = [
    # API endpoints
    path('files/', LogFilesView.as_view(), name='log-files'),
    path('content/<str:filename>/', LogContentView.as_view(), name='log-content'),
    path('app/<str:app_name>/', AppLogsView.as_view(), name='app-logs'),
    path('stats/', LogStatsView.as_view(), name='log-stats'),
    path('realtime/', RealTimeLogsView.as_view(), name='realtime-logs'),
    path('health/', LogHealthView.as_view(), name='log-health'),
    
    # Web interface
    path('view/', LogWebView.as_view(), name='log-web-view'),
]
