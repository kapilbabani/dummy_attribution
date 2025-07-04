# Architecture Separation - Business Logic vs Cache Management

## 🏗️ Overview

The application has been refactored to separate **business logic** from **cache management** for better maintainability, testability, and code organization.

## 📁 File Structure

```
core/
├── views.py              # Business logic views (attribution generation)
├── services.py           # Business logic services
├── cache_views.py        # Cache management views
├── cache_services.py     # Cache management services
├── simple_cache.py       # Core cache implementation
├── models.py             # Database models
└── urls.py               # URL routing
```

## 🔄 Separation of Concerns

### **Business Logic Layer**
- **File**: `core/views.py` + `core/services.py`
- **Purpose**: Core business functionality (attribution generation)
- **Responsibilities**:
  - Attribution data generation
  - Excel file creation
  - Database interactions
  - Business rule enforcement

### **Cache Management Layer**
- **File**: `core/cache_views.py` + `core/cache_services.py`
- **Purpose**: Cache administration and monitoring
- **Responsibilities**:
  - Cache statistics and monitoring
  - Key management and pattern operations
  - Environment-based access control
  - Cache maintenance operations

### **Core Cache Layer**
- **File**: `core/simple_cache.py`
- **Purpose**: Low-level cache implementation
- **Responsibilities**:
  - Memcached integration
  - Key tracking and persistence
  - Atomic dump operations
  - Auto-dump functionality

## 🎯 Benefits of Separation

### **1. Maintainability**
- **Clear boundaries** between business and infrastructure code
- **Easier to locate** specific functionality
- **Reduced coupling** between different concerns
- **Simplified debugging** and troubleshooting

### **2. Testability**
- **Isolated testing** of business logic without cache dependencies
- **Mock cache services** for unit testing
- **Independent cache testing** without business logic interference
- **Better test coverage** with focused test suites

### **3. Scalability**
- **Independent scaling** of business and cache operations
- **Separate deployment** of cache management features
- **Modular development** by different teams
- **Easier feature additions** without affecting other layers

### **4. Security**
- **Environment-based access control** for cache operations
- **Isolated security concerns** for different layers
- **Clear permission boundaries** between read/write operations
- **Audit trail separation** for business vs infrastructure operations

## 🔧 Implementation Details

### **Business Logic Views** (`core/views.py`)
```python
class GenerateAttribution(APIView):
    """Business logic: Attribution generation"""
    def post(self, request):
        # Business logic for attribution generation
        # Uses cache internally but doesn't expose cache management
```

### **Cache Management Views** (`core/cache_views.py`)
```python
class CacheStats(APIView):
    """Cache management: Statistics viewing"""
    def get(self, request):
        # Cache monitoring and statistics
        # Environment-based access control

class CacheManagement(EnvironmentMixin, APIView):
    """Cache management: Administrative operations"""
    def delete(self, request):
        # Cache clearing (development only)
        # Environment-based restrictions
```

### **Business Services** (`core/services.py`)
```python
def generate_attribution_service(beg_date, end_date, id1, id2, attributes):
    """Business logic: Attribution data generation with caching"""
    # Business logic implementation
    # Internal cache usage for performance
    # No cache management operations exposed
```

### **Cache Services** (`core/cache_services.py`)
```python
def get_cache_stats():
    """Cache management: Statistics retrieval"""
    # Cache monitoring operations
    # Environment-aware access control

def clear_cache():
    """Cache management: Administrative operations"""
    # Cache maintenance operations
    # Development-only restrictions
```

## 🌐 API Organization

### **Business APIs** (Available in all environments)
```
POST /api/genrate_attribution/     # Attribution generation
```

### **Cache Viewing APIs** (Available in all environments)
```
GET  /api/cache/stats/             # Cache statistics
GET  /api/cache/keys/              # All cache keys
GET  /api/cache/pattern/           # Pattern-based viewing
GET  /api/cache/pattern/stats/     # Pattern statistics
```

### **Cache Management APIs** (Development only)
```
DELETE /api/cache/                 # Clear all cache
POST   /api/cache/                 # Dump cache to file
DELETE /api/cache/key/{key}/       # Delete specific key
PUT    /api/cache/key/{key}/       # Refresh key timeout
DELETE /api/cache/pattern/manage/  # Delete keys by pattern
PUT    /api/cache/pattern/manage/  # Refresh keys by pattern
POST   /api/cache/auto-dump/       # Start auto-dump
PUT    /api/cache/auto-dump/       # Change auto-dump interval
DELETE /api/cache/auto-dump/       # Stop auto-dump
```

## 🔒 Security Architecture

### **Environment-Based Access Control**
- **Development**: Full access to all cache operations
- **Production**: Read-only access to cache viewing
- **Automatic detection** of environment
- **Granular permissions** per operation type

### **Access Control Implementation**
```python
class EnvironmentMixin:
    def _check_development_only(self):
        """Environment-based access control"""
        if not self._is_development():
            return Response({
                'error': 'This operation is only available in development environment',
                'message': 'Modification operations are disabled in production for security reasons'
            }, status=status.HTTP_403_FORBIDDEN)
        return None
```

## 🧪 Testing Strategy

### **Business Logic Testing**
```python
# Test business logic without cache dependencies
def test_attribution_generation():
    # Mock cache service
    # Test attribution logic independently
    # Verify business rules
```

### **Cache Management Testing**
```python
# Test cache operations independently
def test_cache_operations():
    # Test cache statistics
    # Test pattern matching
    # Test environment restrictions
```

### **Integration Testing**
```python
# Test business logic with real cache
def test_attribution_with_cache():
    # Test full integration
    # Verify cache usage in business logic
    # Test performance improvements
```

## 📊 Monitoring and Observability

### **Business Metrics**
- Attribution generation performance
- Database query optimization
- Business rule compliance
- User activity patterns

### **Cache Metrics**
- Cache hit/miss ratios
- Memory usage patterns
- Key distribution analysis
- Performance bottlenecks

### **Infrastructure Metrics**
- Memcached server health
- Network latency
- Storage utilization
- Auto-dump effectiveness

## 🚀 Deployment Considerations

### **Development Environment**
- Full cache management capabilities
- Debugging and monitoring tools
- Flexible configuration options
- Rapid iteration support

### **Production Environment**
- Read-only cache monitoring
- Restricted administrative access
- Performance optimization
- Security hardening

### **Staging Environment**
- Mirror production restrictions
- Testing of cache operations
- Performance validation
- Security verification

## 🔄 Migration and Maintenance

### **Adding New Business Logic**
1. Add to `core/services.py` for business operations
2. Add to `core/views.py` for API endpoints
3. Update URL routing in `core/urls.py`
4. Add appropriate tests

### **Adding New Cache Features**
1. Add to `core/cache_services.py` for cache operations
2. Add to `core/cache_views.py` for API endpoints
3. Update URL routing in `core/urls.py`
4. Consider environment-based access control
5. Add appropriate tests

### **Modifying Core Cache**
1. Update `core/simple_cache.py` for core functionality
2. Update dependent services as needed
3. Maintain backward compatibility
4. Update documentation

## 📚 Related Documentation

- [Cache Usage Guide](CACHE_USAGE_GUIDE.md) - Complete cache usage documentation
- [Cache Quick Reference](CACHE_QUICK_REFERENCE.md) - Quick reference for cache operations
- [Cache API Security](CACHE_API_SECURITY.md) - Security and access control documentation
- [Development Guide](DEV_GUIDE.md) - Development environment setup
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions

## 🎯 Best Practices

1. **Keep business logic separate** from infrastructure concerns
2. **Use environment-based access control** for cache operations
3. **Maintain clear boundaries** between different layers
4. **Test each layer independently** for better coverage
5. **Document API changes** when adding new features
6. **Follow security best practices** for production deployments
7. **Monitor performance** across all layers
8. **Regular code reviews** to maintain separation of concerns 