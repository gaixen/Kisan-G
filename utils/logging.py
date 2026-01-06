"""Centralized logging utility for the Kisan-G application.

Provides structured logging with file rotation, custom formatting,
and multiple log levels for consistent logging across the application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
import functools
import traceback


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging output."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
            
        return json.dumps(log_data)


class AppLogger:
    """Singleton logger factory for the application."""
    
    _instance: Optional['AppLogger'] = None
    _loggers: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup the root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with simple formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation (10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            self.log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_format)
        root_logger.addHandler(file_handler)
        
        # Error file handler for ERROR and CRITICAL logs
        error_handler = RotatingFileHandler(
            self.log_dir / 'error.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(console_format)
        root_logger.addHandler(error_handler)
        
        # Structured JSON log handler
        json_handler = TimedRotatingFileHandler(
            self.log_dir / 'structured.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(json_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name.
        
        Args:
            name: Name of the logger (typically __name__ of the module)
            
        Returns:
            Configured logger instance
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        return self._loggers[name]


# Singleton instance
_app_logger = AppLogger()


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance for the given module.
    
    Args:
        name: Name of the module (use __name__)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> from utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return _app_logger.get_logger(name)


def log_exception(logger: Optional[logging.Logger] = None):
    """Decorator to automatically log exceptions from functions.
    
    Args:
        logger: Optional logger instance. If None, creates one based on function module.
        
    Example:
        >>> @log_exception()
        >>> def my_function():
        >>>     raise ValueError("Something went wrong")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={
                        'function': func.__name__,
                        'args': str(args)[:200],  # Limit length
                        'kwargs': str(kwargs)[:200]
                    }
                )
                raise
        return wrapper
    return decorator


def log_execution_time(logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """Decorator to log function execution time.
    
    Args:
        logger: Optional logger instance
        level: Logging level for the execution time message
        
    Example:
        >>> @log_execution_time()
        >>> def slow_function():
        >>>     time.sleep(2)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.log(
                    level,
                    f"{func.__name__} executed in {execution_time:.3f}s"
                )
                return result
            except Exception:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f}s"
                )
                raise
        return wrapper
    return decorator


class RequestLogger:
    """Context manager for logging API requests."""
    
    def __init__(self, endpoint: str, method: str, logger: Optional[logging.Logger] = None):
        self.endpoint = endpoint
        self.method = method
        self.logger = logger or get_logger('api')
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Request started: {self.method} {self.endpoint}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"Request completed: {self.method} {self.endpoint} "
                f"({execution_time:.3f}s)"
            )
        else:
            self.logger.error(
                f"Request failed: {self.method} {self.endpoint} "
                f"({execution_time:.3f}s) - {exc_val}",
                exc_info=True
            )
        return False  # Don't suppress exceptions


# Convenience function for backward compatibility
def setup_logging(log_level: int = logging.INFO):
    """Initialize application logging.
    
    Args:
        log_level: Default logging level
        
    Note:
        This is called automatically when the module is imported,
        but can be called explicitly to change the log level.
    """
    logging.getLogger().setLevel(log_level)


if __name__ == '__main__':
    # Demo usage
    logger = get_logger(__name__)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Demo decorator
    @log_exception()
    @log_execution_time()
    def test_function():
        import time
        time.sleep(0.1)
        return "Success"
    
    result = test_function()
    print(f"Result: {result}")
    
    # Demo context manager
    with RequestLogger("/api/test", "GET"):
        import time
        time.sleep(0.05)
        print("Processing request...")
