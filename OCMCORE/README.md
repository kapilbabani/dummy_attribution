# OCMCORE - Attribution and Analytics Platform

## 🚀 Overview

OCMCORE is a comprehensive Django-based platform for attribution analysis, caching, and securities analytics. It provides powerful tools for data analysis, visualization, and performance optimization.

## 📋 Features

### 🎯 Attribution Analysis
- **Multi-dimensional attribution** with configurable IDs and attributes
- **Web-based analyzer** with interactive data tables
- **Excel export** functionality
- **Real-time data processing**

### 📊 Securities Analytics
- **Interactive charts** (Line, Bar, Pie, Heatmap, Scatter)
- **Portfolio vs Benchmark** analysis
- **Daily and aggregate** level analysis
- **Web-based graphing interface**

### ⚡ Caching System
- **App-isolated caching** with automatic key namespacing
- **Pattern-based cache management**
- **Web-based cache viewer**
- **Performance optimization**

### 📝 Comprehensive Logging
- **Per-app log files** with daily rotation
- **Web-based log viewer**
- **Request logging middleware**
- **Docker integration**

## 🏗️ Architecture

```
OCMCORE/
├── attribution/          # Attribution analysis app
├── cache/               # Cache management app
├── logs/                # Logging and monitoring app
├── documentation/       # Project documentation
├── nginx/              # Web server configuration
└── terraform/          # Infrastructure as code
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- SQL Server (MSSQL)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OCMCORE
   ```

2. **Start development environment**
   ```bash
   # Windows
   .\start-dev.ps1
   
   # Linux/Mac
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Access the applications**
   - Main app: http://localhost:8000
   - Attribution analyzer: http://localhost:8000/attribution/analyzer/
   - Securities analyzer: http://localhost:8000/attribution/securities/
   - Cache viewer: http://localhost:8000/cache/
   - Log viewer: http://localhost:8000/logs/

## 📚 Documentation

### Core Documentation
- **[Architecture Guide](documentation/ARCHITECTURE_SEPARATION.md)** - System architecture and separation of concerns
- **[Project Structure](documentation/PROJECT_STRUCTURE.md)** - Detailed project organization
- **[Development Guide](documentation/DEV_GUIDE.md)** - Development setup and workflows
- **[Local Development Guide](documentation/LOCAL_DEVELOPMENT_GUIDE.md)** - Local development environment

### Feature Documentation
- **[Logging Guide](documentation/LOGGING_GUIDE.md)** - Comprehensive logging system usage
- **[Cache API Security](documentation/CACHE_API_SECURITY.md)** - Cache system security considerations
- **[Cache Quick Reference](documentation/CACHE_QUICK_REFERENCE.md)** - Quick cache operations guide
- **[Cache Usage Guide](documentation/CACHE_USAGE_GUIDE.md)** - Detailed cache system usage
- **[Multi-App Development](documentation/MULTI_APP_DEVELOPMENT_GUIDE.md)** - Multi-app development patterns

### Deployment Documentation
- **[Deployment Guide](documentation/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Docker Container Switching](documentation/README_SWITCH.md)** - Linux vs Windows containers
- **[VS Code Debugging](documentation/VSCODE_DEBUGGING_GUIDE.md)** - Development debugging setup

### API Documentation
- **[Swagger Documentation](documentation/SWAGGER.md)** - API documentation and testing

## 🔧 Configuration

### Environment Files
- `env.dev` - Development environment
- `env.linux` - Linux container environment
- `env.windows` - Windows container environment

### Docker Compose Files
- `docker-compose.dev.yml` - Development setup
- `docker-compose.linux.yml` - Linux container production
- `docker-compose.windows.yml` - Windows container production

## 📊 API Endpoints

### Attribution API
- `POST /attribution/api/generate/` - Generate attribution data
- `GET /attribution/api/config/` - Get attribution configuration
- `POST /attribution/api/securities/analyze/` - Analyze securities data
- `GET /attribution/api/securities/config/` - Get securities configuration

### Cache API
- `GET /cache/api/stats/` - Cache statistics
- `GET /cache/api/keys/` - List cache keys
- `POST /cache/api/clear/` - Clear cache
- `GET /cache/api/pattern/{pattern}/` - Pattern-based cache operations

### Logs API
- `GET /api/logs/files/` - List log files
- `GET /api/logs/content/{app}/{file}` - Get log content
- `GET /api/logs/app/{app}/` - App-specific logs
- `GET /api/logs/stats/` - Log statistics

## 🐳 Docker Support

### Container Types
- **Linux Containers** (Recommended) - SQL Authentication
- **Windows Containers** - Trusted Connection (Windows Authentication)

### Quick Commands
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Linux Production
docker-compose -f docker-compose.linux.yml --env-file env.linux up -d

# Windows Production
docker-compose -f docker-compose.windows.yml --env-file env.windows up -d
```

## 🔍 Monitoring and Debugging

### Logging
- **Per-app logs** with daily rotation
- **Web-based log viewer** at `/logs/`
- **Real-time log streaming**
- **Log analysis and statistics**

### Performance Monitoring
- **Request logging middleware**
- **Cache performance metrics**
- **Database query monitoring**
- **Application performance tracking**

## 🛠️ Development Tools

### VS Code Integration
- **Debug configurations** for Django
- **Task automation** scripts
- **Integrated terminal** support

### Testing
- **Unit tests** for all apps
- **Integration tests** for APIs
- **Performance tests** for caching

## 🔒 Security

- **App-isolated caching** prevents data leakage
- **Request logging** for security monitoring
- **Input validation** on all APIs
- **Error handling** without sensitive data exposure

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Follow the development guide**
4. **Add tests for new features**
5. **Submit a pull request**

## 📞 Support

For issues and questions:
1. Check the relevant documentation
2. Review the troubleshooting guides
3. Check the logs for error details
4. Contact the development team

## 📄 License

[Add your license information here]

---

*OCMCORE - Attribution and Analytics Platform*
*Last updated: January 2024* 