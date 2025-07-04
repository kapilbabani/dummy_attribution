#!/usr/bin/env python
"""
OCMCORE App Creation Script

This script automates the creation of new Django apps with all necessary files,
configurations, and boilerplate code.

Usage:
    python create_app.py app_name

Example:
    python create_app.py user_management
"""

import os
import sys
import re
from pathlib import Path

def validate_app_name(app_name):
    """Validate the app name follows Django conventions"""
    if not app_name:
        return False, "App name cannot be empty"
    
    if not re.match(r'^[a-z][a-z0-9_]*$', app_name):
        return False, "App name must be lowercase, start with a letter, and contain only letters, numbers, and underscores"
    
    if app_name in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
        return False, f"'{app_name}' is a reserved Django app name"
    
    return True, "Valid app name"

def create_app_directory(app_name):
    """Create the app directory structure"""
    app_dir = Path(app_name)
    
    if app_dir.exists():
        print(f"❌ Error: App directory '{app_name}' already exists")
        return False
    
    # Create app directory
    app_dir.mkdir()
    print(f"✅ Created app directory: {app_name}/")
    
    # Create __init__.py
    (app_dir / "__init__.py").touch()
    print(f"✅ Created: {app_name}/__init__.py")
    
    return True

def create_models_file(app_name):
    """Create models.py with basic structure"""
    models_content = f'''"""
Models for {app_name} app.
"""

from django.db import models


class {app_name.title().replace('_', '')}Model(models.Model):
    """
    Base model for {app_name} app.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Add your models here
class ExampleModel({app_name.title().replace('_', '')}Model):
    """
    Example model for {app_name} app.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = '{app_name}_example'
    
    def __str__(self):
        return self.name
'''
    
    with open(f"{app_name}/models.py", "w") as f:
        f.write(models_content)
    print(f"✅ Created: {app_name}/models.py")

def create_views_file(app_name):
    """Create views.py with basic API structure"""
    views_content = f'''"""
Views for {app_name} app.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.http import HttpResponse
from {app_name}.services import get_example_data


class ExampleInputSerializer(serializers.Serializer):
    """Serializer for example input data"""
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)


class ExampleView(APIView):
    """
    Example API endpoint for {app_name} app.
    """
    
    def get(self, request):
        """Handle GET requests"""
        try:
            data = get_example_data()
            return Response({{'data': data}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({{'error': str(e)}}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """Handle POST requests"""
        serializer = ExampleInputSerializer(data=request.data)
        if serializer.is_valid():
            # Process the data
            return Response({{'message': 'Data processed successfully'}}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """
    Health check endpoint for {app_name} app.
    """
    
    def get(self, request):
        """Health check"""
        return Response({{'status': 'healthy', 'app': '{app_name}'}}, status=status.HTTP_200_OK)
'''
    
    with open(f"{app_name}/views.py", "w") as f:
        f.write(views_content)
    print(f"✅ Created: {app_name}/views.py")

def create_services_file(app_name):
    """Create services.py with business logic structure"""
    services_content = f'''"""
Business logic services for {app_name} app.
"""

from {app_name}.models import ExampleModel
from simple_cache import simple_cache
import hashlib
import json


def _generate_cache_key(*args, **kwargs):
    """Generate cache key from parameters"""
    params = {{
        'args': args,
        'kwargs': sorted(kwargs.items())
    }}
    sorted_params = json.dumps(params, sort_keys=True)
    return hashlib.md5(sorted_params.encode()).hexdigest()


def get_example_data():
    """
    Get example data with caching.
    """
    cache_key = f"{app_name}_example_data"
    
    # Try to get from cache first
    cached_data = simple_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # If not in cache, fetch from database
    data = list(ExampleModel.objects.filter(is_active=True).values())
    
    # Cache the results for 1 hour
    simple_cache.set(cache_key, data, timeout=3600)
    
    return data


def create_example_record(name, description=""):
    """
    Create a new example record.
    """
    record = ExampleModel.objects.create(
        name=name,
        description=description
    )
    
    # Clear cache to force refresh
    cache_key = f"{app_name}_example_data"
    simple_cache.delete(cache_key)
    
    return record


def update_example_record(record_id, **kwargs):
    """
    Update an example record.
    """
    try:
        record = ExampleModel.objects.get(id=record_id)
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        record.save()
        
        # Clear cache to force refresh
        cache_key = f"{app_name}_example_data"
        simple_cache.delete(cache_key)
        
        return record
    except ExampleModel.DoesNotExist:
        return None


def delete_example_record(record_id):
    """
    Delete an example record.
    """
    try:
        record = ExampleModel.objects.get(id=record_id)
        record.delete()
        
        # Clear cache to force refresh
        cache_key = f"{app_name}_example_data"
        simple_cache.delete(cache_key)
        
        return True
    except ExampleModel.DoesNotExist:
        return False
'''
    
    with open(f"{app_name}/services.py", "w") as f:
        f.write(services_content)
    print(f"✅ Created: {app_name}/services.py")

def create_urls_file(app_name):
    """Create urls.py with URL patterns"""
    urls_content = f'''"""
URL configuration for {app_name} app.
"""

from django.urls import path
from {app_name}.views import ExampleView, HealthCheckView

urlpatterns = [
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='{app_name}-health'),
    
    # Example endpoints
    path('example/', ExampleView.as_view(), name='{app_name}-example'),
    
    # Add more URL patterns here as needed
]
'''
    
    with open(f"{app_name}/urls.py", "w") as f:
        f.write(urls_content)
    print(f"✅ Created: {app_name}/urls.py")

def create_admin_file(app_name):
    """Create admin.py with admin configuration"""
    admin_content = f'''"""
Django admin configuration for {app_name} app.
"""

from django.contrib import admin
from {app_name}.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExampleModel.
    """
    list_display = ('name', 'description', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {{
            'fields': ('name', 'description')
        }}),
        ('Status', {{
            'fields': ('is_active',)
        }}),
        ('Timestamps', {{
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }}),
    )
'''
    
    with open(f"{app_name}/admin.py", "w") as f:
        f.write(admin_content)
    print(f"✅ Created: {app_name}/admin.py")

def create_apps_file(app_name):
    """Create apps.py with app configuration"""
    apps_content = f'''"""
App configuration for {app_name} app.
"""

from django.apps import AppConfig


class {app_name.title().replace('_', '')}Config(AppConfig):
    """
    Configuration for {app_name} app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_name.replace("_", " ").title()}'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import {app_name}.signals
        except ImportError:
            pass
'''
    
    with open(f"{app_name}/apps.py", "w") as f:
        f.write(apps_content)
    print(f"✅ Created: {app_name}/apps.py")

def create_tests_file(app_name):
    """Create tests.py with basic test structure"""
    tests_content = f'''"""
Tests for {app_name} app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from {app_name}.models import ExampleModel
from {app_name}.services import create_example_record, get_example_data


class {app_name.title().replace('_', '')}ModelTests(TestCase):
    """
    Tests for {app_name} models.
    """
    
    def setUp(self):
        """Set up test data"""
        self.example = ExampleModel.objects.create(
            name="Test Example",
            description="Test Description"
        )
    
    def test_example_creation(self):
        """Test example model creation"""
        self.assertEqual(self.example.name, "Test Example")
        self.assertEqual(self.example.description, "Test Description")
        self.assertTrue(self.example.is_active)
    
    def test_example_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.example), "Test Example")


class {app_name.title().replace('_', '')}APITests(APITestCase):
    """
    Tests for {app_name} API endpoints.
    """
    
    def setUp(self):
        """Set up test data"""
        self.example = create_example_record("API Test Example", "API Test Description")
    
    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('{app_name}-health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app'], '{app_name}')
    
    def test_example_get(self):
        """Test example GET endpoint"""
        url = reverse('{app_name}-example')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_example_post_valid(self):
        """Test example POST endpoint with valid data"""
        url = reverse('{app_name}-example')
        data = {{
            'name': 'New Example',
            'description': 'New Description'
        }}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_example_post_invalid(self):
        """Test example POST endpoint with invalid data"""
        url = reverse('{app_name}-example')
        data = {{}}  # Empty data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class {app_name.title().replace('_', '')}ServiceTests(TestCase):
    """
    Tests for {app_name} services.
    """
    
    def test_create_example_record(self):
        """Test creating example record"""
        record = create_example_record("Service Test", "Service Description")
        self.assertEqual(record.name, "Service Test")
        self.assertEqual(record.description, "Service Description")
    
    def test_get_example_data(self):
        """Test getting example data"""
        create_example_record("Data Test", "Data Description")
        data = get_example_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
'''
    
    with open(f"{app_name}/tests.py", "w") as f:
        f.write(tests_content)
    print(f"✅ Created: {app_name}/tests.py")

def create_migrations_directory(app_name):
    """Create migrations directory"""
    migrations_dir = Path(app_name) / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "__init__.py").touch()
    print(f"✅ Created: {app_name}/migrations/")

def update_settings_file(app_name):
    """Update settings.py to include the new app"""
    settings_file = "settings.py"
    
    if not os.path.exists(settings_file):
        print(f"❌ Error: settings.py not found")
        return False
    
    with open(settings_file, "r") as f:
        content = f.read()
    
    # Find the INSTALLED_APPS section and add the new app
    if f"'{app_name}'," in content:
        print(f"⚠️  Warning: App '{app_name}' already in INSTALLED_APPS")
        return True
    
    # Add the app to INSTALLED_APPS
    pattern = r'(\s+# Local apps\n\s*)(\[.*?\])'
    replacement = f'\\1\\2,\n    \'{app_name}\','
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # If pattern not found, add before the closing bracket
        pattern = r'(\s*)(\]\s*$)'
        replacement = f'\\1    \'{app_name}\',\n\\2'
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(settings_file, "w") as f:
        f.write(new_content)
    
    print(f"✅ Updated: settings.py - added '{app_name}' to INSTALLED_APPS")
    return True

def update_main_urls_file(app_name):
    """Update main urls.py to include the new app URLs"""
    urls_file = "urls.py"
    
    if not os.path.exists(urls_file):
        print(f"❌ Error: urls.py not found")
        return False
    
    with open(urls_file, "r") as f:
        content = f.read()
    
    # Check if app URLs are already included
    if f"path('api/{app_name}/', include('{app_name}.urls'))," in content:
        print(f"⚠️  Warning: App '{app_name}' URLs already in main urls.py")
        return True
    
    # Add the app URLs
    pattern = r'(\s+# Attribution app URLs\n\s*path\(''api/attribution/'', include\(''attribution\.urls''\)\),\n)'
    replacement = f'\\1    # {app_name} app URLs\n    path(\'api/{app_name}/\', include(\'{app_name}.urls\')),\n'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # If pattern not found, add before API documentation
        pattern = r'(\s+# API documentation\n)'
        replacement = f'    # {app_name} app URLs\n    path(\'api/{app_name}/\', include(\'{app_name}.urls\')),\n\n\\1'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(urls_file, "w") as f:
        f.write(new_content)
    
    print(f"✅ Updated: urls.py - added '{app_name}' URLs")
    return True

def create_readme_file(app_name):
    """Create a README file for the app"""
    readme_content = f'''# {app_name.title().replace('_', ' ')}

## Overview

This is the {app_name} app for the OCMCORE project.

## Features

- Example API endpoints
- Database models with caching
- Admin interface configuration
- Comprehensive test coverage

## API Endpoints

- `GET /api/{app_name}/health/` - Health check
- `GET /api/{app_name}/example/` - Get example data
- `POST /api/{app_name}/example/` - Create example data

## Models

- `ExampleModel` - Base model for {app_name} functionality

## Services

- `get_example_data()` - Retrieve example data with caching
- `create_example_record()` - Create new example records
- `update_example_record()` - Update existing records
- `delete_example_record()` - Delete records

## Development

### Running Tests

```bash
python manage.py test {app_name}
```

### Creating Migrations

```bash
python manage.py makemigrations {app_name}
python manage.py migrate
```

### Admin Interface

Access the admin interface at `/admin/` to manage {app_name} data.

## Caching

This app uses the shared cache system from the attribution app for performance optimization.
'''
    
    with open(f"{app_name}/README.md", "w") as f:
        f.write(readme_content)
    print(f"✅ Created: {app_name}/README.md")

def print_next_steps(app_name):
    """Print next steps for the developer"""
    print("\n" + "="*60)
    print(f"🎉 Successfully created '{app_name}' app!")
    print("="*60)
    print("\n📋 Next Steps:")
    print(f"1. Create database migrations:")
    print(f"   python manage.py makemigrations {app_name}")
    print(f"   python manage.py migrate")
    print(f"\n2. Test the app:")
    print(f"   python manage.py test {app_name}")
    print(f"\n3. Start the development server:")
    print(f"   python manage.py runserver")
    print(f"\n4. Access your new endpoints:")
    print(f"   http://localhost:8000/api/{app_name}/health/")
    print(f"   http://localhost:8000/api/{app_name}/example/")
    print(f"\n5. Customize the app:")
    print(f"   - Edit {app_name}/models.py to add your models")
    print(f"   - Edit {app_name}/views.py to add your API endpoints")
    print(f"   - Edit {app_name}/services.py to add your business logic")
    print(f"   - Edit {app_name}/urls.py to add your URL patterns")
    print(f"\n6. Check the admin interface:")
    print(f"   http://localhost:8000/admin/")
    print("\n" + "="*60)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("❌ Usage: python create_app.py <app_name>")
        print("Example: python create_app.py user_management")
        sys.exit(1)
    
    app_name = sys.argv[1].lower()
    
    # Validate app name
    is_valid, message = validate_app_name(app_name)
    if not is_valid:
        print(f"❌ Error: {message}")
        sys.exit(1)
    
    print(f"🚀 Creating Django app: {app_name}")
    print("="*50)
    
    # Create app structure
    if not create_app_directory(app_name):
        sys.exit(1)
    
    # Create all necessary files
    create_models_file(app_name)
    create_views_file(app_name)
    create_services_file(app_name)
    create_urls_file(app_name)
    create_admin_file(app_name)
    create_apps_file(app_name)
    create_tests_file(app_name)
    create_migrations_directory(app_name)
    create_readme_file(app_name)
    
    # Update project files
    update_settings_file(app_name)
    update_main_urls_file(app_name)
    
    # Print next steps
    print_next_steps(app_name)

if __name__ == "__main__":
    main() 