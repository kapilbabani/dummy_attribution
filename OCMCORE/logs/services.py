"""
Log viewing services for logs app.
"""

import os
import glob
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Generator
from collections import defaultdict, Counter

from django.conf import settings


class LogViewerService:
    """
    Service for viewing and analyzing log files.
    """
    
    def __init__(self):
        """Initialize the log viewer service."""
        self.log_dir = getattr(settings, 'LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
        self.log_pattern = re.compile(
            r'^\[(?P<timestamp>.*?)\] (?P<level>\w+) (?P<logger>\w+) (?P<process>\d+) (?P<thread>\d+) (?P<message>.*)$'
        )
    
    def get_all_log_files(self) -> Dict:
        """
        Get all available log files in the log directory.
        
        Returns:
            Dict containing log files information
        """
        log_files = []
        total_size = 0
        
        if not os.path.exists(self.log_dir):
            return {
                'log_files': [],
                'total_files': 0,
                'log_directory': self.log_dir,
                'error': 'Log directory does not exist'
            }
        
        # Get all log files (including rotated ones)
        for file_path in glob.glob(os.path.join(self.log_dir, '*.log*')):
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                file_name = os.path.basename(file_path)
                
                # Extract app name and date from filename
                app_name, date = self._parse_log_filename(file_name)
                
                log_files.append({
                    'name': file_name,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'app_name': app_name,
                    'date': date,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2)
                })
                total_size += stat.st_size
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            'log_files': log_files,
            'total_files': len(log_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'log_directory': self.log_dir
        }
    
    def get_log_content(
        self,
        filename: str,
        lines: int = 100,
        level: str = '',
        search: str = '',
        start_date: str = '',
        end_date: str = ''
    ) -> Dict:
        """
        Get log file content with optional filtering.
        
        Args:
            filename: Name of the log file
            lines: Number of lines to return
            level: Filter by log level
            search: Search term in log messages
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            Dict containing filtered log content
        """
        file_path = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Log file '{filename}' not found")
        
        content = []
        total_lines = 0
        filtered_lines = 0
        
        # Parse date filters
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                pass
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Read and filter log file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                line = line.strip()
                
                if not line:
                    continue
                
                # Parse log line
                parsed = self._parse_log_line(line)
                if not parsed:
                    continue
                
                # Apply filters
                if not self._apply_filters(parsed, level, search, start_dt, end_dt):
                    continue
                
                content.append({
                    'line_number': line_num,
                    'timestamp': parsed['timestamp'],
                    'level': parsed['level'],
                    'logger': parsed['logger'],
                    'message': parsed['message'],
                    'raw_line': line
                })
                
                filtered_lines += 1
                
                # Limit number of lines
                if len(content) >= lines:
                    break
        
        # Reverse to show newest first
        content.reverse()
        
        return {
            'filename': filename,
            'total_lines': total_lines,
            'filtered_lines': filtered_lines,
            'content': content,
            'filters_applied': {
                'lines': lines,
                'level': level,
                'search': search,
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    def get_app_logs(
        self,
        app_name: str,
        lines: int = 100,
        level: str = '',
        date: str = 'latest'
    ) -> Dict:
        """
        Get logs for a specific app.
        
        Args:
            app_name: Name of the app (e.g., 'attribution', 'cache')
            lines: Number of lines to return
            level: Filter by log level
            date: Specific date (YYYY-MM-DD) or 'latest'
            
        Returns:
            Dict containing app logs
        """
        # Find the appropriate log file for the app
        if date == 'latest':
            # Find the most recent log file for this app
            pattern = os.path.join(self.log_dir, f'{app_name}.log*')
            log_files = glob.glob(pattern)
            if not log_files:
                raise FileNotFoundError(f"No logs found for app '{app_name}'")
            
            # Sort by modification time and get the latest
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            filename = os.path.basename(log_files[0])
        else:
            # Look for specific date
            filename = f'{app_name}.log.{date}'
            if not os.path.exists(os.path.join(self.log_dir, filename)):
                raise FileNotFoundError(f"No logs found for app '{app_name}' on date '{date}'")
        
        # Get log content using the existing method
        content = self.get_log_content(
            filename=filename,
            lines=lines,
            level=level
        )
        
        # Add app-specific information
        content['app_name'] = app_name
        content['date'] = date
        
        return content
    
    def get_log_statistics(self, app_name: str = '', days: int = 7) -> Dict:
        """
        Get log statistics and analytics.
        
        Args:
            app_name: Filter by app name (empty for all apps)
            days: Number of days to analyze
            
        Returns:
            Dict containing log statistics
        """
        stats = {
            'total_log_files': 0,
            'total_log_entries': 0,
            'level_distribution': defaultdict(int),
            'app_distribution': defaultdict(int),
            'daily_stats': [],
            'analyzed_days': days
        }
        
        # Get all log files
        all_files = self.get_all_log_files()
        
        # Filter by app if specified
        log_files = all_files['log_files']
        if app_name:
            log_files = [f for f in log_files if f['app_name'] == app_name]
        
        stats['total_log_files'] = len(log_files)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Initialize daily stats
        daily_stats = defaultdict(lambda: {'total_entries': 0, 'errors': 0, 'warnings': 0})
        
        # Process each log file
        for log_file in log_files:
            file_path = log_file['path']
            app = log_file['app_name']
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        parsed = self._parse_log_line(line)
                        if not parsed:
                            continue
                        
                        # Check if within date range
                        try:
                            log_dt = datetime.strptime(parsed['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                            if log_dt < start_date or log_dt > end_date:
                                continue
                        except ValueError:
                            continue
                        
                        # Update statistics
                        stats['total_log_entries'] += 1
                        stats['level_distribution'][parsed['level']] += 1
                        stats['app_distribution'][app] += 1
                        
                        # Update daily stats
                        date_key = log_dt.strftime('%Y-%m-%d')
                        daily_stats[date_key]['total_entries'] += 1
                        
                        if parsed['level'] in ['ERROR', 'CRITICAL']:
                            daily_stats[date_key]['errors'] += 1
                        elif parsed['level'] == 'WARNING':
                            daily_stats[date_key]['warnings'] += 1
                            
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Convert daily stats to list
        for date in sorted(daily_stats.keys()):
            stats['daily_stats'].append({
                'date': date,
                **daily_stats[date]
            })
        
        # Convert defaultdict to regular dict for JSON serialization
        stats['level_distribution'] = dict(stats['level_distribution'])
        stats['app_distribution'] = dict(stats['app_distribution'])
        
        return stats
    
    def stream_logs(self, app_name: str = '', level: str = '') -> Generator[str, None, None]:
        """
        Stream real-time logs.
        
        Args:
            app_name: Filter by app name
            level: Filter by log level
            
        Yields:
            Log lines as they are written
        """
        # Find the current log file for the app
        if app_name:
            pattern = os.path.join(self.log_dir, f'{app_name}.log*')
            log_files = glob.glob(pattern)
            if not log_files:
                yield f"data: No logs found for app '{app_name}'\n\n"
                return
            
            # Get the most recent file
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            file_path = log_files[0]
        else:
            # Stream from main log file
            file_path = os.path.join(self.log_dir, 'ocmcore.log')
            if not os.path.exists(file_path):
                yield f"data: No main log file found\n\n"
                return
        
        # Get initial file size
        initial_size = os.path.getsize(file_path)
        
        # Stream new log entries
        while True:
            try:
                current_size = os.path.getsize(file_path)
                
                if current_size > initial_size:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(initial_size)
                        new_content = f.read()
                        
                        for line in new_content.splitlines():
                            if line.strip():
                                parsed = self._parse_log_line(line.strip())
                                if parsed and self._apply_filters(parsed, level, '', None, None):
                                    yield f"data: {line}\n\n"
                    
                    initial_size = current_size
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                yield f"data: Error streaming logs: {str(e)}\n\n"
                break
    
    def get_health_status(self) -> Dict:
        """
        Get health status of the logs app.
        
        Returns:
            Dict containing health status
        """
        try:
            all_files = self.get_all_log_files()
            
            # Get available apps from log files
            available_apps = list(set(f['app_name'] for f in all_files['log_files'] if f['app_name']))
            
            return {
                'status': 'healthy',
                'message': 'Logs app is working correctly',
                'log_directory': self.log_dir,
                'directory_exists': os.path.exists(self.log_dir),
                'available_apps': available_apps,
                'total_log_files': all_files['total_files'],
                'total_size_mb': all_files.get('total_size_mb', 0)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Logs app health check failed: {str(e)}',
                'log_directory': self.log_dir,
                'directory_exists': os.path.exists(self.log_dir) if self.log_dir else False
            }
    
    def _parse_log_filename(self, filename: str) -> tuple:
        """
        Parse log filename to extract app name and date.
        
        Args:
            filename: Log filename
            
        Returns:
            Tuple of (app_name, date)
        """
        # Handle rotated log files with date suffix
        if '.log.' in filename:
            parts = filename.split('.log.')
            app_name = parts[0]
            date = parts[1] if len(parts) > 1 else ''
        else:
            # Handle regular log files
            app_name = filename.replace('.log', '')
            date = ''
        
        return app_name, date
    
    def _parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse a log line to extract components.
        
        Args:
            line: Raw log line
            
        Returns:
            Dict with parsed components or None if parsing fails
        """
        match = self.log_pattern.match(line)
        if match:
            return match.groupdict()
        return None
    
    def _apply_filters(
        self,
        parsed: Dict,
        level: str = '',
        search: str = '',
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> bool:
        """
        Apply filters to a parsed log entry.
        
        Args:
            parsed: Parsed log entry
            level: Level filter
            search: Search term filter
            start_dt: Start date filter
            end_dt: End date filter
            
        Returns:
            True if entry passes all filters
        """
        # Level filter
        if level and parsed['level'] != level:
            return False
        
        # Search filter
        if search and search.lower() not in parsed['message'].lower():
            return False
        
        # Date filters
        if start_dt or end_dt:
            try:
                log_dt = datetime.strptime(parsed['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                
                if start_dt and log_dt < start_dt:
                    return False
                if end_dt and log_dt > end_dt:
                    return False
            except ValueError:
                # If we can't parse the timestamp, skip date filtering
                pass
        
        return True 