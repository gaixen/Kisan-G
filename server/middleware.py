"""
Middleware and error handlers for Flask application.

Implements request/response middleware, error handling, and logging.
"""

import time
import traceback
from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Any
import uuid


class RequestMiddleware:
    """Middleware for request processing and logging."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    @staticmethod
    def before_request():
        """Execute before each request."""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Log request
        from utils.logging import get_logger
        logger = get_logger('middleware')
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={'request_id': g.request_id}
        )
    
    @staticmethod
    def after_request(response):
        """Execute after each request."""
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Add CORS headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Log response
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            from utils.logging import get_logger
            logger = get_logger('middleware')
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"- Status: {response.status_code} - Time: {elapsed:.3f}s",
                extra={'request_id': getattr(g, 'request_id', 'unknown')}
            )
        
        return response
    
    @staticmethod
    def teardown_request(exception=None):
        """Execute at the end of request, even if exception occurred."""
        if exception:
            from utils.logging import get_logger
            logger = get_logger('middleware')
            logger.error(
                f"Request failed with exception: {str(exception)}",
                exc_info=True,
                extra={'request_id': getattr(g, 'request_id', 'unknown')}
            )


class ErrorHandler:
    """Centralized error handling for Flask application."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Register error handlers with Flask app."""
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(429, self.handle_rate_limit)
        app.register_error_handler(500, self.handle_internal_error)
        app.register_error_handler(503, self.handle_service_unavailable)
        app.register_error_handler(Exception, self.handle_generic_exception)
    
    @staticmethod
    def _create_error_response(status_code: int, message: str, details: str = None):
        """Create standardized error response."""
        error_response = {
            'error': True,
            'status_code': status_code,
            'message': message,
            'request_id': getattr(g, 'request_id', None),
            'path': request.path
        }
        if details:
            error_response['details'] = details
        
        return jsonify(error_response), status_code
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors."""
        return self._create_error_response(
            400,
            'Bad Request',
            str(error.description) if hasattr(error, 'description') else None
        )
    
    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized errors."""
        return self._create_error_response(401, 'Unauthorized')
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors."""
        return self._create_error_response(403, 'Forbidden')
    
    def handle_not_found(self, error):
        """Handle 404 Not Found errors."""
        return self._create_error_response(
            404,
            'Resource Not Found',
            f'The requested URL {request.path} was not found on the server.'
        )
    
    def handle_method_not_allowed(self, error):
        """Handle 405 Method Not Allowed errors."""
        return self._create_error_response(
            405,
            'Method Not Allowed',
            f'The method {request.method} is not allowed for {request.path}'
        )
    
    def handle_rate_limit(self, error):
        """Handle 429 Rate Limit errors."""
        return self._create_error_response(
            429,
            'Too Many Requests',
            'Rate limit exceeded. Please try again later.'
        )
    
    def handle_internal_error(self, error):
        """Handle 500 Internal Server errors."""
        from utils.logging import get_logger
        logger = get_logger('error_handler')
        logger.error(
            f"Internal server error: {str(error)}",
            exc_info=True,
            extra={'request_id': getattr(g, 'request_id', 'unknown')}
        )
        
        return self._create_error_response(
            500,
            'Internal Server Error',
            'An unexpected error occurred. Please try again later.'
        )
    
    def handle_service_unavailable(self, error):
        """Handle 503 Service Unavailable errors."""
        return self._create_error_response(
            503,
            'Service Unavailable',
            'The service is temporarily unavailable. Please try again later.'
        )
    
    def handle_generic_exception(self, error):
        """Handle any unhandled exceptions."""
        from utils.logging import get_logger
        logger = get_logger('error_handler')
        logger.error(
            f"Unhandled exception: {str(error)}",
            exc_info=True,
            extra={'request_id': getattr(g, 'request_id', 'unknown')}
        )
        
        # Return generic error in production, detailed in development
        import os
        if os.getenv('FLASK_ENV') == 'development':
            return self._create_error_response(
                500,
                'Internal Server Error',
                f'{type(error).__name__}: {str(error)}'
            )
        else:
            return self._create_error_response(
                500,
                'Internal Server Error',
                'An unexpected error occurred.'
            )


def require_api_key(func: Callable) -> Callable:
    """Decorator to require API key authentication."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        # In production, validate against stored API keys
        import os
        expected_key = os.getenv('API_KEY')
        
        if expected_key and api_key != expected_key:
            return jsonify({
                'error': 'Invalid or missing API key',
                'status_code': 401
            }), 401
        
        return func(*args, **kwargs)
    return wrapper


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator to implement rate limiting."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simple in-memory rate limiting
            # In production, use Redis or similar
            from collections import defaultdict
            import time
            
            if not hasattr(wrapper, '_rate_limit_data'):
                wrapper._rate_limit_data = defaultdict(list)
            
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old requests
            wrapper._rate_limit_data[client_ip] = [
                req_time for req_time in wrapper._rate_limit_data[client_ip]
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(wrapper._rate_limit_data[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'status_code': 429,
                    'retry_after': window_seconds
                }), 429
            
            # Add current request
            wrapper._rate_limit_data[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_request_data(*required_fields):
    """Decorator to validate required fields in request data."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields,
                    'status_code': 400
                }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
