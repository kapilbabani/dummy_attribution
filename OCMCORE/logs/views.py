"""
Log viewing views for logs app.
"""

import os
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from django.conf import settings
from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from logs.services import LogViewerService


class LogFilesView(APIView):
    """
    API view for listing available log files.
    """
    
    @swagger_auto_schema(
        operation_description="List all available log files",
        responses={
            200: openapi.Response(
                description="List of log files",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'log_files': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'size': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'modified': openapi.Schema(type=openapi.TYPE_STRING),
                                    'app_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
                        'total_files': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'log_directory': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request):
        """List all available log files."""
        try:
            service = LogViewerService()
            log_files = service.get_all_log_files()
            return Response(log_files)
        except Exception as e:
            return Response(
                {'error': f'Failed to list log files: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogContentView(APIView):
    """
    API view for viewing log file content.
    """
    
    @swagger_auto_schema(
        operation_description="View log file content with optional filtering",
        manual_parameters=[
            openapi.Parameter(
                'filename',
                openapi.IN_PATH,
                description="Log file name",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'lines',
                openapi.IN_QUERY,
                description="Number of lines to return (default: 100, max: 1000)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'level',
                openapi.IN_QUERY,
                description="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search term in log messages",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date filter (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date filter (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Log file content",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'filename': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_lines': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'filtered_lines': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'content': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'line_number': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                                    'level': openapi.Schema(type=openapi.TYPE_STRING),
                                    'logger': openapi.Schema(type=openapi.TYPE_STRING),
                                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                                    'raw_line': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
                        'filters_applied': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'lines': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'level': openapi.Schema(type=openapi.TYPE_STRING),
                                'search': openapi.Schema(type=openapi.TYPE_STRING),
                                'start_date': openapi.Schema(type=openapi.TYPE_STRING),
                                'end_date': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                    }
                )
            ),
            404: openapi.Response(description="Log file not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def get(self, request, filename):
        """View log file content with optional filtering."""
        try:
            service = LogViewerService()
            
            # Get query parameters
            lines = int(request.query_params.get('lines', 100))
            level = request.query_params.get('level', '').upper()
            search = request.query_params.get('search', '')
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            
            # Validate lines parameter
            if lines > 1000:
                lines = 1000
            elif lines < 1:
                lines = 100
            
            content = service.get_log_content(
                filename=filename,
                lines=lines,
                level=level,
                search=search,
                start_date=start_date,
                end_date=end_date
            )
            
            return Response(content)
            
        except FileNotFoundError:
            return Response(
                {'error': f'Log file "{filename}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to read log file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AppLogsView(APIView):
    """
    API view for viewing logs for specific apps.
    """
    
    @swagger_auto_schema(
        operation_description="View logs for a specific app",
        manual_parameters=[
            openapi.Parameter(
                'app_name',
                openapi.IN_PATH,
                description="App name (e.g., attribution, cache)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'lines',
                openapi.IN_QUERY,
                description="Number of lines to return (default: 100, max: 1000)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'level',
                openapi.IN_QUERY,
                description="Filter by log level",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Specific date (YYYY-MM-DD) or 'latest' for most recent",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(description="App logs content"),
            404: openapi.Response(description="App logs not found"),
        }
    )
    def get(self, request, app_name):
        """View logs for a specific app."""
        try:
            service = LogViewerService()
            
            # Get query parameters
            lines = int(request.query_params.get('lines', 100))
            level = request.query_params.get('level', '').upper()
            date = request.query_params.get('date', 'latest')
            
            # Validate lines parameter
            if lines > 1000:
                lines = 1000
            elif lines < 1:
                lines = 100
            
            content = service.get_app_logs(
                app_name=app_name,
                lines=lines,
                level=level,
                date=date
            )
            
            return Response(content)
            
        except FileNotFoundError:
            return Response(
                {'error': f'No logs found for app "{app_name}"'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to read app logs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogStatsView(APIView):
    """
    API view for log statistics and analytics.
    """
    
    @swagger_auto_schema(
        operation_description="Get log statistics and analytics",
        manual_parameters=[
            openapi.Parameter(
                'app_name',
                openapi.IN_QUERY,
                description="Filter by app name",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Number of days to analyze (default: 7)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Log statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_log_files': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_log_entries': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'level_distribution': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'DEBUG': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'INFO': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'WARNING': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'ERROR': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'CRITICAL': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        ),
                        'app_distribution': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER)
                        ),
                        'daily_stats': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                    'total_entries': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'errors': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'warnings': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        ),
                    }
                )
            )
        }
    )
    def get(self, request):
        """Get log statistics and analytics."""
        try:
            service = LogViewerService()
            
            app_name = request.query_params.get('app_name', '')
            days = int(request.query_params.get('days', 7))
            
            stats = service.get_log_statistics(app_name=app_name, days=days)
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get log statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RealTimeLogsView(APIView):
    """
    API view for real-time log streaming.
    """
    
    @swagger_auto_schema(
        operation_description="Stream real-time logs",
        manual_parameters=[
            openapi.Parameter(
                'app_name',
                openapi.IN_QUERY,
                description="Filter by app name",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'level',
                openapi.IN_QUERY,
                description="Filter by log level",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(description="Real-time log stream"),
        }
    )
    def get(self, request):
        """Stream real-time logs."""
        try:
            service = LogViewerService()
            
            app_name = request.query_params.get('app_name', '')
            level = request.query_params.get('level', '').upper()
            
            response = StreamingHttpResponse(
                service.stream_logs(app_name=app_name, level=level),
                content_type='text/plain'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Failed to stream logs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogHealthView(APIView):
    """
    Health check view for logs app.
    """
    
    @swagger_auto_schema(
        operation_description="Health check for logs app",
        responses={
            200: openapi.Response(
                description="Logs app health status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'log_directory': openapi.Schema(type=openapi.TYPE_STRING),
                        'available_apps': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'total_log_files': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        }
    )
    def get(self, request):
        """Health check for logs app."""
        try:
            service = LogViewerService()
            health = service.get_health_status()
            return Response(health)
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': f'Logs app health check failed: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogWebView(APIView):
    """
    Web interface view for log viewing.
    """
    
    def get(self, request):
        """Render the log viewer web interface."""
        from django.shortcuts import render
        
        # Get available apps for the dropdown
        service = LogViewerService()
        try:
            all_files = service.get_all_log_files()
            available_apps = list(set(f['app_name'] for f in all_files['log_files'] if f['app_name']))
        except:
            available_apps = []
        
        context = {
            'available_apps': available_apps,
            'api_base_url': '/api/logs/'
        }
        
        return render(request, 'logs/log_viewer.html', context)
