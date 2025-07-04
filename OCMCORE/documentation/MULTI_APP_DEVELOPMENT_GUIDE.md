# Multi-App Development Guide

## 🎯 Overview

This guide explains how to create and develop new Django apps within the OCMCORE project. The project follows a modular architecture where each app handles specific business functionality.

## 📁 App Structure Pattern

Each app in OCMCORE follows this structure:

```
app_name/
├── __init__.py              # App package
├── apps.py                  # App configuration
├── models.py                # Database models
├── views.py                 # API views and business logic
├── services.py              # Business logic services
├── urls.py                  # App URL routing
├── admin.py                 # Django admin configuration
├── tests.py                 # App tests
└── README.md                # App documentation (optional)
```

## 🚀 Creating a New App

### Automated App Creation (Recommended)

OCMCORE includes an automated script that creates new apps with all necessary files and configurations:

```bash
# Navigate to project root
cd OCMCORE

# Create new app using the automated script
python create_app.py your_app_name
```

This script will automatically:
- ✅ Create the app directory structure
- ✅ Generate all necessary files (`models.py`, `views.py`, `services.py`, `urls.py`, `admin.py`, `apps.py`, `tests.py`)
- ✅ Register the app in `settings.py`
- ✅ Add app URLs to main `urls.py`
- ✅ Create migrations directory
- ✅ Generate a README file
- ✅ Set up caching integration
- ✅ Create example models and views

### Manual App Creation (Alternative)

If you prefer to create apps manually, follow these steps:

#### Step 1: Create the App

```bash
# Navigate to project root
cd OCMCORE

# Create new app
python manage.py startapp your_app_name
```

#### Step 2: Register the App

Add your app to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    
    # Local apps
    'attribution',
    'cache',
    'your_app_name',  # Add your new app here
]
```

#### Step 3: Create App Configuration

Create or update `your_app_name/apps.py`:

```python
"""
App configuration for your_app_name app.
"""

from django.apps import AppConfig


class YourAppNameConfig(AppConfig):
    """
    Configuration for your_app_name app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'
    verbose_name = 'Your App Display Name'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import your_app_name.signals
        except ImportError:
            pass
```

#### Step 4: Create URL Configuration

Create `your_app_name/urls.py`:

```python
"""
URL configuration for your_app_name app.

The `urlpatterns` list routes URLs to views for the your_app_name app.
"""
from django.urls import path
from your_app_name.views import YourMainView, YourDetailView

urlpatterns = [
    # Your app endpoints
    path('', YourMainView.as_view(), name='your-app-main'),
    path('<int:pk>/', YourDetailView.as_view(), name='your-app-detail'),
    path('custom-endpoint/', YourCustomView.as_view(), name='your-custom-endpoint'),
]
```

#### Step 5: Include App URLs in Main URLs

Add your app URLs to the main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Attribution app URLs
    path('api/attribution/', include('attribution.urls')),
    
    # Cache app URLs
    path('api/cache/', include('cache.urls')),
    
    # Your new app URLs
    path('api/your-app/', include('your_app_name.urls')),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

## 🔧 App Development Patterns

### Models (`models.py`)

```python
from django.db import models
from django.utils import timezone


class YourModel(models.Model):
    """Your model description."""
    
    # Basic fields
    name = models.CharField(max_length=100, help_text="Name of the item")
    description = models.TextField(blank=True, help_text="Description of the item")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'your_app_yourmodel'
        ordering = ['-created_at']
        verbose_name = 'Your Model'
        verbose_name_plural = 'Your Models'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Custom save logic here
        super().save(*args, **kwargs)
```

### Views (`views.py`)

```python
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from your_app_name.models import YourModel
from your_app_name.services import your_business_logic_service
from your_app_name.serializers import YourModelSerializer


class YourMainView(APIView):
    """Main view for your app functionality."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of items."""
        try:
            # Use service layer for business logic
            items = your_business_logic_service.get_items(request.user)
            
            serializer = YourModelSerializer(items, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': len(items)
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create new item."""
        try:
            serializer = YourModelSerializer(data=request.data)
            if serializer.is_valid():
                # Use service layer for business logic
                item = your_business_logic_service.create_item(
                    user=request.user,
                    data=serializer.validated_data
                )
                
                return Response({
                    'success': True,
                    'data': YourModelSerializer(item).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class YourDetailView(APIView):
    """Detail view for specific item."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get specific item."""
        try:
            item = get_object_or_404(YourModel, pk=pk, user=request.user)
            serializer = YourModelSerializer(item)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Services (`services.py`)

```python
"""
Business logic services for your_app_name app.
"""

from django.db import transaction
from your_app_name.models import YourModel


def your_business_logic_service(user, data=None):
    """Main business logic service."""
    
    if data is None:
        # Get items logic
        return YourModel.objects.filter(user=user, is_active=True)
    else:
        # Create item logic
        with transaction.atomic():
            item = YourModel.objects.create(
                user=user,
                **data
            )
            return item


def validate_item_data(data):
    """Validate item data."""
    errors = []
    
    if not data.get('name'):
        errors.append('Name is required')
    
    if len(data.get('name', '')) > 100:
        errors.append('Name must be less than 100 characters')
    
    return errors
```

### Serializers (create `serializers.py`)

```python
from rest_framework import serializers
from your_app_name.models import YourModel


class YourModelSerializer(serializers.ModelSerializer):
    """Serializer for YourModel."""
    
    class Meta:
        model = YourModel
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate name field."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value.strip()
```

### Admin (`admin.py`)

```python
from django.contrib import admin
from your_app_name.models import YourModel


@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    """Admin configuration for YourModel."""
    
    list_display = ['name', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('User Information', {
            'fields': ('user',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

## 🧪 Testing Your App

### Create Tests (`tests.py`)

```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from your_app_name.models import YourModel
from your_app_name.services import your_business_logic_service


class YourModelTestCase(TestCase):
    """Test cases for YourModel."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_model_creation(self):
        """Test model creation."""
        item = YourModel.objects.create(
            user=self.user,
            name='Test Item',
            description='Test Description'
        )
        
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.user, self.user)
        self.assertTrue(item.is_active)


class YourAppAPITestCase(APITestCase):
    """Test cases for your app API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_items(self):
        """Test getting items."""
        # Create test items
        YourModel.objects.create(user=self.user, name='Item 1')
        YourModel.objects.create(user=self.user, name='Item 2')
        
        # Make request
        response = self.client.get('/api/your-app/')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        self.assertTrue(response.data['success'])
    
    def test_create_item(self):
        """Test creating item."""
        data = {
            'name': 'New Item',
            'description': 'New Description'
        }
        
        response = self.client.post('/api/your-app/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'New Item')
```

## 🔄 Database Migrations

### Create and Apply Migrations

```bash
# Create migrations for your app
python manage.py makemigrations your_app_name

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations your_app_name
```

## 🚀 Running Your App

### Development

```bash
# Start development server
python manage.py runserver

# Or use VS Code debugging (F5)
# Select "Django Debug" configuration
```

### Testing

```bash
# Run all tests
python manage.py test

# Run your app tests only
python manage.py test your_app_name

# Run specific test
python manage.py test your_app_name.tests.YourModelTestCase
```

## 📚 Best Practices

### 1. **Separation of Concerns**
- Keep business logic in `services.py`
- Keep API logic in `views.py`
- Keep data models in `models.py`

### 2. **Error Handling**
- Always use try-catch blocks in views
- Return consistent error responses
- Log errors appropriately

### 3. **Security**
- Use proper permissions in views
- Validate all input data
- Use Django's built-in security features

### 4. **Performance**
- Use caching where appropriate
- Optimize database queries
- Use pagination for large datasets

### 5. **Documentation**
- Add docstrings to all functions
- Document API endpoints
- Keep README files updated

## 🔗 Integration with Existing Apps

### Using Cache Service

```python
from simple_cache import simple_cache

def your_cached_function():
    """Example of using cache in your app."""
    
    # Check cache first
    cache_key = "your_app:data:123"
    cached_data = simple_cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # If not cached, compute and cache
    data = expensive_computation()
    simple_cache.set(cache_key, data, timeout=3600)
    
    return data
```

### Using Attribution App

```python
from attribution.services import generate_attribution_service

def your_attribution_integration():
    """Example of integrating with attribution app."""
    
    # Use attribution service
    result = generate_attribution_service(
        beg_date='2024-01-01',
        end_date='2024-01-31',
        id1=1,
        id2=2,
        attributes=['attr1', 'attr2']
    )
    
    return result
```

## 📋 Checklist for New Apps

- [ ] Create app with `python manage.py startapp`
- [ ] Register app in `INSTALLED_APPS`
- [ ] Create `apps.py` configuration
- [ ] Create `urls.py` with app routes
- [ ] Include app URLs in main `urls.py`
- [ ] Create models in `models.py`
- [ ] Create views in `views.py`
- [ ] Create services in `services.py`
- [ ] Create serializers in `serializers.py`
- [ ] Configure admin in `admin.py`
- [ ] Write tests in `tests.py`
- [ ] Create and apply migrations
- [ ] Test the app thoroughly
- [ ] Update documentation

## 🎯 Example: Complete App Creation

Here's a complete example of creating a "reports" app using the automated script:

```bash
# 1. Create app with automated script
python create_app.py reports

# 2. Apply migrations
python manage.py makemigrations reports
python manage.py migrate

# 3. Test the app
python manage.py test reports

# 4. Run the server
python manage.py runserver
```

Your new app will be available at `/api/reports/` and fully integrated with the OCMCORE project!

### What the Script Creates

The `create_app.py` script generates:

- **`reports/models.py`** - Example model with caching integration
- **`reports/views.py`** - API views with serializers and error handling
- **`reports/services.py`** - Business logic with cache integration
- **`reports/urls.py`** - URL routing for the app
- **`reports/admin.py`** - Django admin configuration
- **`reports/apps.py`** - App configuration
- **`reports/tests.py`** - Test cases
- **`reports/README.md`** - App documentation
- **Updated `settings.py`** - App registration
- **Updated `urls.py`** - URL inclusion

The generated app includes:
- ✅ REST API endpoints
- ✅ Caching integration with `simple_cache`
- ✅ Error handling and validation
- ✅ Django admin interface
- ✅ Test cases
- ✅ Health check endpoint
- ✅ Example models and views 

## 📝 Logging for Each App

Every app in OCMCORE can have its own dedicated log file, rotated daily, for easier debugging and monitoring.

### How Per-App Logging Works
- Each app (e.g., `attribution`, `cache`) has its own logger and log file (e.g., `logs/attribution.log.YYYY-MM-DD`).
- Logs are also sent to the main project log and the console.
- Log files are rotated daily and kept for 14 days.

### How to Add Logging for a New App
1. **Add a handler and logger in `settings.py`:**
   - Copy the pattern for `attribution_file` and `attribution` logger.
   - Example for a new app called `reports`:

```python
'reports_file': {
    'class': 'logging.handlers.TimedRotatingFileHandler',
    'filename': os.path.join(LOG_DIR, 'reports.log'),
    'when': 'midnight',
    'backupCount': 14,
    'formatter': 'verbose',
    'encoding': 'utf8',
    'suffix': '%Y-%m-%d',
},
...
'reports': {
    'handlers': ['console', 'file', 'reports_file'],
    'level': 'INFO',
    'propagate': False,
},
```

2. **Use the logger in your app code:**

```python
import logging
logger = logging.getLogger(__name__)

# In your views, services, etc.
logger.info("This is an info message from reports app.")
logger.error("This is an error message.", exc_info=True)
```

- All logs from your app will now appear in `logs/reports.log.YYYY-MM-DD` as well as the main log.

### Where to Find Logs
- All logs are stored in the `logs/` directory (persisted on the host if using Docker Compose as described above).
- Each app has its own log file, rotated daily. 