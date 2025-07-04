# OCMCORE Project Structure

## 🏗️ Project Overview

**OCMCORE** is a Django project that supports multiple apps for different business functionalities.

## 📁 Directory Structure

```
OCMCORE/                          # Project root
├── __init__.py                   # Django project package
├── settings.py                   # Main project settings
├── urls.py                       # Main URL routing
├── wsgi.py                       # WSGI configuration
├── asgi.py                       # ASGI configuration
├── manage.py                     # Django management script
├── requirements.txt              # Project dependencies
│
├── attribution/                  # Attribution app
│   ├── __init__.py
│   ├── models.py                 # Attribution models
│   ├── views.py                  # Attribution business logic views
│   ├── services.py               # Attribution business logic
│   └── urls.py                   # Attribution app URLs
│
├── cache/                        # Cache app
│   ├── __init__.py
│   ├── apps.py                   # Cache app configuration
│   ├── models.py                 # Cache models (empty)
│   ├── views.py                  # Cache management API views
│   ├── urls.py                   # Cache app URLs
│   ├── tests.py                  # Cache app tests
│   └── README.md                 # Cache app documentation
│
├── simple_cache.py               # Core cache implementation (root level)
├── cache_utils.py                # Cache utility functions (root level)
│
├── index/                        # Index app (future)
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   └── urls.py
│
├── venv/                         # Virtual environment
├── nginx/                        # Nginx configuration
├── terraform/                    # Infrastructure as Code
├── .github/                      # GitHub Actions workflows
│
├── docker-compose.yml            # Docker Compose configuration
├── docker-compose.dev.yml        # Development Docker Compose
├── docker-compose.linux.yml      # Linux Docker Compose
├── docker-compose.windows.yml    # Windows Docker Compose
├── Dockerfile                    # Docker configuration
├── Dockerfile.linux              # Linux Docker configuration
├── Dockerfile.windows            # Windows Docker configuration
│
├── env                           # Production environment variables
├── env.dev                       # Development environment variables
├── env.linux                     # Linux environment variables
├── env.windows                   # Windows environment variables
│
├── start-dev.ps1                 # Development startup script
├── stop-dev.ps1                  # Development stop script
├── setup_onprem_windows.ps1      # Windows setup script
│
├── .gitignore                    # Git ignore rules
├── MULTI_APP_DEVELOPMENT_GUIDE.md # Development guide
├── ARCHITECTURE_SEPARATION.md    # Architecture documentation
├── CACHE_USAGE_GUIDE.md          # Cache usage guide
├── CACHE_QUICK_REFERENCE.md      # Cache quick reference
├── CACHE_API_SECURITY.md         # Cache security documentation
├── DEV_GUIDE.md                  # Development guide
├── DEPLOYMENT_GUIDE.md           # Deployment guide
├── LOCAL_DEVELOPMENT_GUIDE.md    # Local development guide
├── MEMCACHED_MIGRATION.md        # Memcached migration guide
├── SWAGGER.md                    # API documentation guide
├── README_SWITCH.md              # README switch guide
├── WINDOWS_SSO_GUIDE.docx        # Windows SSO guide
│
├── test_pattern_cache.py         # Cache pattern tests
├── test_caching_strategies.py    # Caching strategy tests
└── test_memcached.py             # Memcached tests
```

## 🎯 Key Components

### **Project Configuration**
- **`settings.py`**: Main Django settings with database, cache, and app configurations
- **`urls.py`**: Main URL routing that includes all app URLs
- **`wsgi.py`** & **`asgi.py`**: Web server gateway interfaces
- **`manage.py`**: Django management script

### **Apps**
- **`attribution/`**: Attribution generation
- **`cache/`**: Cache management and APIs
- **`index/`**: Future app for index functionality
- **Additional apps**: Can be added following the same pattern

### **Infrastructure**
- **`docker-compose*.yml`**: Container orchestration for different environments
- **`Dockerfile*`**: Container definitions for different platforms
- **`terraform/`**: Infrastructure as Code for deployment
- **`nginx/`**: Web server configuration

### **Environment Management**
- **`env*`**: Environment-specific configuration files
- **`venv/`**: Python virtual environment
- **`requirements.txt`**: Python dependencies

### **Documentation**
- **`MULTI_APP_DEVELOPMENT_GUIDE.md`**: Complete guide for creating new apps
- **`ARCHITECTURE_SEPARATION.md`**: Architecture and separation of concerns
- **`CACHE_*`**: Cache-related documentation
- **`DEV_GUIDE.md`**: Development setup and workflow

## 🔧 URL Structure

```
/api/attribution/generate/        # Attribution generation
/api/attribution/cache/stats/     # Cache statistics
/api/attribution/cache/keys/      # Cache keys
/api/attribution/cache/           # Cache management
/api/index/                       # Index app endpoints (future)
/swagger/                         # API documentation
/redoc/                          # Alternative API documentation
/admin/                          # Django admin
```

## 🚀 Getting Started

1. **Navigate to project directory**:
   ```bash
   cd OCMCORE
   ```

2. **Activate virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Django checks**:
   ```bash
   python manage.py check
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## 📚 Documentation

- **Development**: See `MULTI_APP_DEVELOPMENT_GUIDE.md`
- **Architecture**: See `ARCHITECTURE_SEPARATION.md`
- **Cache Usage**: See `CACHE_USAGE_GUIDE.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`

## 🔄 Adding New Apps

1. **Create app**:
   ```bash
   python manage.py startapp your_app_name
   ```

2. **Register in settings**:
   Add `'your_app_name'` to `INSTALLED_APPS` in `settings.py`

3. **Create URLs**:
   Create `your_app_name/urls.py` and add to main `urls.py`

4. **Follow patterns**:
   See `MULTI_APP_DEVELOPMENT_GUIDE.md` for detailed instructions

## 🎯 Best Practices

- **App isolation**: Each app should be self-contained
- **Shared resources**: Use common patterns for shared functionality
- **Environment separation**: Use environment-specific configurations
- **Documentation**: Keep documentation updated with code changes
- **Testing**: Write tests for each app independently 