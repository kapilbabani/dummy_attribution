# Cache API Security - Environment-Based Access Control

## 🔒 Security Overview

The cache APIs implement **environment-based access control** with different permission levels:

- **Development Environment**: Full access (view, read, delete, refresh, manage)
- **Production Environment**: Read-only access (view and read only)

This ensures that cache modification operations are only available in development while maintaining visibility for monitoring in production.

## 🛡️ Access Control Implementation

### Development Environment (✅ Full Access)
- **Local Development**: `DEBUG=True` or `DJANGO_ENV=development`
- **Development Servers**: Localhost with wildcard allowed hosts
- **Dev Containers**: Docker containers with development environment variables

### Production Environment (✅ Read-Only Access)
- **Production Servers**: `DEBUG=False` and `DJANGO_ENV=production`
- **Staging Servers**: Any non-development environment
- **Cloud Deployments**: Production deployments with restricted access

## 🔍 Environment Detection Logic

The system uses multiple indicators to determine the environment:

```python
def _is_development(self):
    # 1. Check Django DEBUG setting
    if getattr(settings, 'DEBUG', False):
        return True
    
    # 2. Check environment variable
    env = os.environ.get('DJANGO_ENV', '').lower()
    if env in ['dev', 'development', 'local']:
        return True
    
    # 3. Check if running locally
    if getattr(settings, 'ALLOWED_HOSTS', ['*']) == ['*']:
        return True
    
    return False
```

## 📋 Environment Configuration

### Development Environment (`env.dev`)
```bash
DJANGO_ENV=development
DJANGO_DEBUG=true
```

### Production Environment (`env.windows`, `env.linux`)
```bash
DJANGO_ENV=production
DJANGO_DEBUG=false
```

## 🔧 Available APIs by Environment

| Endpoint | Method | Development | Production | Purpose |
|----------|--------|-------------|------------|---------|
| `GET /api/cache/stats/` | GET | ✅ | ✅ | Cache statistics |
| `GET /api/cache/keys/` | GET | ✅ | ✅ | All cache keys |
| `GET /api/cache/pattern/` | GET | ✅ | ✅ | Pattern-based viewing |
| `GET /api/cache/pattern/stats/` | GET | ✅ | ✅ | Pattern statistics |
| `DELETE /api/cache/` | DELETE | ✅ | ❌ | Clear all cache |
| `POST /api/cache/` | POST | ✅ | ❌ | Dump cache to file |
| `DELETE /api/cache/key/{key}/` | DELETE | ✅ | ❌ | Delete specific key |
| `PUT /api/cache/key/{key}/` | PUT | ✅ | ❌ | Refresh key timeout |
| `DELETE /api/cache/pattern/manage/` | DELETE | ✅ | ❌ | Delete keys by pattern |
| `PUT /api/cache/pattern/manage/` | PUT | ✅ | ❌ | Refresh keys by pattern |
| `POST /api/cache/auto-dump/` | POST | ✅ | ❌ | Start auto-dump |
| `PUT /api/cache/auto-dump/` | PUT | ✅ | ❌ | Change auto-dump interval |
| `DELETE /api/cache/auto-dump/` | DELETE | ✅ | ❌ | Stop auto-dump |
| `POST /api/genrate_attribution/` | POST | ✅ | ✅ | Attribution generation |

## 🚫 Blocked Operations in Production

When modification operations are attempted in production, they return a `403 Forbidden` response:

### Production Response Example
```json
{
  "error": "This operation is only available in development environment",
  "message": "Modification operations are disabled in production for security reasons"
}
```

## 🛠️ Development Access (Full Access)

### Local Development
```bash
# Start development server
python manage.py runserver

# View operations (available everywhere)
curl http://localhost:8000/api/cache/stats/
curl http://localhost:8000/api/cache/keys/

# Management operations (development only)
curl -X DELETE http://localhost:8000/api/cache/
curl -X DELETE http://localhost:8000/api/cache/key/mykey/
curl -X PUT http://localhost:8000/api/cache/key/mykey/ -H "Content-Type: application/json" -d '{"timeout": 7200}'
```

### Docker Development
```bash
# Start development containers
docker-compose -f docker-compose.dev.yml up

# Full access to all operations
curl http://localhost:8000/api/cache/stats/
curl -X DELETE http://localhost:8000/api/cache/
```

## 🔍 Production Access (Read-Only)

### Production Operations
```bash
# ✅ Allowed in production
curl https://yourdomain.com/api/cache/stats/
curl https://yourdomain.com/api/cache/keys/
curl https://yourdomain.com/api/cache/pattern/?pattern=user:.*
curl https://yourdomain.com/api/cache/pattern/stats/?pattern=user:.*

# ❌ Blocked in production
curl -X DELETE https://yourdomain.com/api/cache/
curl -X DELETE https://yourdomain.com/api/cache/key/mykey/
curl -X PUT https://yourdomain.com/api/cache/key/mykey/ -d '{"timeout": 7200}'
```

## 🔐 Security Benefits

### 1. **Controlled Access Levels**
- Development teams have full control for debugging
- Production maintains read-only access for monitoring
- Prevents accidental cache modifications in production

### 2. **Information Disclosure Prevention**
- Cache viewing remains available for monitoring
- Modification operations are blocked to prevent attacks
- Maintains operational visibility without risk

### 3. **Operational Security**
- Clear separation between dev and prod capabilities
- Follows principle of least privilege
- Reduces attack surface in production

### 4. **Compliance**
- Helps meet security compliance requirements
- Maintains audit trails for cache operations
- Supports security best practices

## 🚨 Security Considerations

### What's Available in Production
- **Cache Viewing**: All read operations for monitoring
- **Statistics**: Cache performance and usage metrics
- **Pattern Matching**: View keys and values by patterns
- **Attribution API**: Core business functionality

### What's Blocked in Production
- **Cache Deletion**: All delete operations
- **Cache Modification**: Refresh and timeout changes
- **Cache Management**: Clear, dump, and auto-dump control
- **Pattern Management**: Bulk delete and refresh operations

## 🔍 Testing Environment Detection

### Test Development Access
```bash
# Set development environment
export DJANGO_ENV=development
export DJANGO_DEBUG=true

# Test full access
curl http://localhost:8000/api/cache/stats/
curl -X DELETE http://localhost:8000/api/cache/
```

### Test Production Restrictions
```bash
# Set production environment
export DJANGO_ENV=production
export DJANGO_DEBUG=false

# Test read-only access
curl http://localhost:8000/api/cache/stats/  # ✅ Works
curl -X DELETE http://localhost:8000/api/cache/  # ❌ Blocked
```

## 📝 Configuration Checklist

### Development Setup
- [ ] `DJANGO_ENV=development` in environment file
- [ ] `DJANGO_DEBUG=true` in environment file
- [ ] All cache operations accessible
- [ ] Development tools working

### Production Setup
- [ ] `DJANGO_ENV=production` in environment file
- [ ] `DJANGO_DEBUG=false` in environment file
- [ ] Read-only operations working
- [ ] Modification operations blocked
- [ ] Security headers configured

## 🔄 Emergency Override (Development Access in Production)

In emergency situations, you can temporarily enable full access in production by:

1. **Setting environment variable**:
   ```bash
   export DJANGO_ENV=development
   ```

2. **Modifying Django settings**:
   ```python
   DEBUG = True
   ```

3. **Restart the application**

⚠️ **Warning**: Only use this for legitimate debugging purposes and revert immediately after use.

## 📊 Monitoring and Logging

### Access Attempts
All access attempts are logged with:
- Timestamp
- IP address
- User agent
- Requested endpoint
- HTTP method
- Environment status
- Access granted/denied

### Security Alerts
Consider setting up alerts for:
- Multiple 403 responses from same IP
- Modification attempts in production
- Environment configuration changes
- Unusual access patterns

## 🎯 Best Practices

1. **Use development environment** for all cache management operations
2. **Monitor production cache** using read-only APIs
3. **Never enable modification APIs** in production for routine operations
4. **Monitor access logs** for unauthorized attempts
5. **Regular security reviews** of environment configurations
6. **Document emergency procedures** for legitimate debugging needs

## 🔗 Related Documentation

- [Cache Usage Guide](CACHE_USAGE_GUIDE.md) - Complete cache usage documentation
- [Cache Quick Reference](CACHE_QUICK_REFERENCE.md) - Quick reference for cache operations
- [Development Guide](DEV_GUIDE.md) - Development environment setup
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions 