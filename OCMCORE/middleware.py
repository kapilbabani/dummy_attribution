import logging
import time

logger = logging.getLogger('django.request')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        # Get user info
        user = getattr(request, 'user', None)
        if user and hasattr(user, 'is_authenticated'):
            user_str = user.username if user.is_authenticated else 'anon'
        else:
            user_str = 'anon'

        # Get IP address (prefer X-Forwarded-For if present)
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            if request.META.get('HTTP_X_FORWARDED_FOR')
            else request.META.get('REMOTE_ADDR')
        )

        logger.info(
            f"{request.method} {request.get_full_path()} "
            f"status={response.status_code} "
            f"user={user_str} "
            f"ip={ip} "
            f"duration={duration:.3f}s"
        )
        return response 