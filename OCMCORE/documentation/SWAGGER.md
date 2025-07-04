# API Documentation (Swagger / OpenAPI)

## Interactive API Docs

After running the Django server, access the following URLs:

- **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

These pages provide interactive documentation for all available API endpoints.

## Raw OpenAPI Schema

- **JSON:** [http://127.0.0.1:8000/swagger.json](http://127.0.0.1:8000/swagger.json)
- **YAML:** [http://127.0.0.1:8000/swagger.yaml](http://127.0.0.1:8000/swagger.yaml)

## How to Add Your API to Swagger

- All Django REST Framework views and viewsets are automatically included.
- Use DRF serializers and viewsets for best results.
- You can add docstrings to your views and serializers for better documentation.

## Authentication

- If your API requires authentication, use the "Authorize" button in Swagger UI to provide your token or credentials.

## References

- [drf-yasg documentation](https://drf-yasg.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/) 