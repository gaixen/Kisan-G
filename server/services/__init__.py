"""
Service layer for Kisan-G application.

Implements business logic with dependency injection and service patterns.
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class ServiceRegistry:
    """Registry for managing service instances (Singleton pattern)."""
    
    _instance: Optional['ServiceRegistry'] = None
    _services: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, service_name: str, service_instance: Any):
        """Register a service instance."""
        self._services[service_name] = service_instance
    
    def get(self, service_name: str) -> Any:
        """Retrieve a service instance."""
        return self._services.get(service_name)
    
    def clear(self):
        """Clear all registered services (useful for testing)."""
        self._services.clear()


# Global service registry instance
service_registry = ServiceRegistry()


def inject_service(service_name: str):
    """Decorator for dependency injection of services."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            service = service_registry.get(service_name)
            if service is None:
                raise RuntimeError(f"Service '{service_name}' not registered")
            return func(*args, service=service, **kwargs)
        return wrapper
    return decorator
