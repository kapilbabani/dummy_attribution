# Logs

## Overview

This is the logs app for the OCMCORE project.

## Features

- Example API endpoints
- Database models with caching
- Admin interface configuration
- Comprehensive test coverage

## API Endpoints

- `GET /api/logs/health/` - Health check
- `GET /api/logs/example/` - Get example data
- `POST /api/logs/example/` - Create example data

## Models

- `ExampleModel` - Base model for logs functionality

## Services

- `get_example_data()` - Retrieve example data with caching
- `create_example_record()` - Create new example records
- `update_example_record()` - Update existing records
- `delete_example_record()` - Delete records

## Development

### Running Tests

```bash
python manage.py test logs
```

### Creating Migrations

```bash
python manage.py makemigrations logs
python manage.py migrate
```

### Admin Interface

Access the admin interface at `/admin/` to manage logs data.

## Caching

This app uses the shared cache system from the attribution app for performance optimization.
