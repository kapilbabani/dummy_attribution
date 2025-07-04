"""
URL configuration for attribution app.

The `urlpatterns` list routes URLs to views for the attribution app.
"""
from django.urls import path
from attribution.views import (
    AttributionView,
    GenerateAttributionView,
    GenerateAttributionExcelView,
    AttributionAnalyzerView,
    SecuritiesAnalyzerView,
    generate_attribution,
    get_attribution_config,
    analyze_securities,
    get_securities_config
)

urlpatterns = [
    # Main attribution endpoints
    path('', AttributionView.as_view(), name='attribution-main'),
    path('generate/', GenerateAttributionView.as_view(), name='generate-attribution'),
    path('generate-excel/', GenerateAttributionExcelView.as_view(), name='generate-attribution-excel'),
    
    # Web interfaces
    path('analyzer/', AttributionAnalyzerView.as_view(), name='attribution-analyzer'),
    path('securities/', SecuritiesAnalyzerView.as_view(), name='securities-analyzer'),
    
    # API endpoints for attribution
    path('api/generate/', generate_attribution, name='api-generate-attribution'),
    path('api/config/', get_attribution_config, name='api-attribution-config'),
    
    # API endpoints for securities analysis
    path('api/securities/analyze/', analyze_securities, name='api-analyze-securities'),
    path('api/securities/config/', get_securities_config, name='api-securities-config'),
]
