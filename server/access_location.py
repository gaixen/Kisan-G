"""
Geolocation service for accessing device location with consent handling.

Provides server-side geolocation utilities with caching, fallback locations,
and IP-based geolocation. Client-side implementation should use Geolocation API.
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import lru_cache
import json
from pathlib import Path
from utils.logging import get_logger

logger = get_logger(__name__)


class LocationCache:
    """Simple file-based cache for location data."""
    
    def __init__(self, cache_file: str = 'location_cache.json', ttl_minutes: int = 60):
        self.cache_file = Path(cache_file)
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached location data if not expired."""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            if key in cache_data:
                entry = cache_data[key]
                cached_time = datetime.fromisoformat(entry['timestamp'])
                
                if datetime.now() - cached_time < self.ttl:
                    return entry['data']
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        
        return None
    
    def set(self, key: str, data: Dict[str, Any]):
        """Store location data in cache."""
        cache_data = {}
        
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        cache_data[key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)


class GeolocationService:
    """Service for obtaining device geolocation.
    
    Provides multiple strategies for obtaining location:
    1. Cached location (fast)
    2. IP-based geolocation (fallback)
    3. Default location (last resort)
    """
    
    # Default fallback location (Berlin, Germany - from original hardcoded values)
    DEFAULT_LOCATION = {
        "latitude": 52.52,
        "longitude": 13.41,
        "source": "default",
        "accuracy": None,
        "city": "Berlin",
        "country": "Germany"
    }
    
    def __init__(self):
        self.cache = LocationCache()
        self.ip_geolocation_apis = [
            'http://ip-api.com/json/',  # Free, no API key required
            'https://ipapi.co/json/',    # Free tier available
        ]
    
    def get_location_from_ip(self, ip_address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get approximate location from IP address.
        
        Args:
            ip_address: Optional IP address. If None, uses caller's IP.
            
        Returns:
            Location dictionary or None if failed
        """
        # Try ip-api.com (no API key required)
        try:
            url = 'http://ip-api.com/json/'
            if ip_address:
                url += ip_address
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    location = {
                        "latitude": data.get('lat'),
                        "longitude": data.get('lon'),
                        "city": data.get('city'),
                        "region": data.get('regionName'),
                        "country": data.get('country'),
                        "country_code": data.get('countryCode'),
                        "timezone": data.get('timezone'),
                        "source": "ip_geolocation",
                        "accuracy": "city_level",
                        "ip": data.get('query')
                    }
                    
                    # Cache the result
                    cache_key = ip_address or 'default_ip'
                    self.cache.set(cache_key, location)
                    
                    return location
        except requests.RequestException:
            pass
        
        # Fallback to ipapi.co
        try:
            url = 'https://ipapi.co/json/'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('error'):
                    location = {
                        "latitude": data.get('latitude'),
                        "longitude": data.get('longitude'),
                        "city": data.get('city'),
                        "region": data.get('region'),
                        "country": data.get('country_name'),
                        "country_code": data.get('country_code'),
                        "timezone": data.get('timezone'),
                        "source": "ip_geolocation",
                        "accuracy": "city_level",
                        "ip": data.get('ip')
                    }
                    
                    cache_key = ip_address or 'default_ip'
                    self.cache.set(cache_key, location)
                    
                    return location
        except requests.RequestException:
            pass
        
        return None
    
    def get_location(
        self, 
        ip_address: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get device location using available strategies.
        
        Args:
            ip_address: Optional IP address for IP-based geolocation
            use_cache: Whether to use cached location
            
        Returns:
            Location dictionary with latitude, longitude, and metadata
        """
        cache_key = ip_address or 'default_ip'
        
        # Try cache first
        if use_cache:
            cached_location = self.cache.get(cache_key)
            if cached_location:
                return cached_location
        
        # Try IP-based geolocation
        location = self.get_location_from_ip(ip_address)
        if location:
            return location
        
        # Return default location as last resort
        return self.DEFAULT_LOCATION.copy()


# Singleton instance
_geolocation_service = GeolocationService()


def access_location(ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Get device location (backward compatible function).
    
    Args:
        ip_address: Optional IP address for IP-based geolocation
        
    Returns:
        Dictionary containing location information:
        - latitude: float
        - longitude: float
        - source: str ("ip_geolocation", "default", etc.)
        - Additional metadata depending on source
        
    Note:
        For browser-based client applications, use the Geolocation API directly:
        
        JavaScript example:
        ```javascript
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                // Send to backend
            },
            (error) => console.error(error),
            { enableHighAccuracy: true }
        );
        ```
        
        React Native example (KisanGMobile):
        ```javascript
        import Geolocation from '@react-native-community/geolocation';
        
        Geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                // Send to backend
            },
            (error) => console.error(error),
            { enableHighAccuracy: true, timeout: 15000 }
        );
        ```
    """
    return _geolocation_service.get_location(ip_address=ip_address)


def get_location_from_request(request) -> Dict[str, Any]:
    """Extract location from Flask/FastAPI request object.
    
    Args:
        request: Flask or FastAPI request object
        
    Returns:
        Location dictionary
    """
    # Try to get IP from request
    ip_address = None
    
    # Handle X-Forwarded-For header (proxy/load balancer)
    if hasattr(request, 'headers'):
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.headers.get('X-Real-IP')
    
    # Fallback to remote_addr
    if not ip_address and hasattr(request, 'remote_addr'):
        ip_address = request.remote_addr
    
    # Filter out local/private IPs for better geolocation
    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        ip_address = None
    
    return access_location(ip_address=ip_address)


if __name__ == '__main__':
    # Demo usage
    logger.info("Testing Geolocation Service")
    logger.info("" + ("=" * 50))
    
    # Test 1: Default location
    location = access_location()
    logger.info("\n1. Location (auto-detect):")
    logger.info(json.dumps(location, indent=2))
    
    # Test 2: Specific IP (Google DNS)
    logger.info("\n2. Location from specific IP (8.8.8.8):")
    location_ip = access_location(ip_address='8.8.8.8')
    logger.info(json.dumps(location_ip, indent=2))
    
    # Test 3: Cached location
    logger.info("\n3. Cached location (should be instant):")
    import time
    start = time.time()
    cached_location = access_location()
    elapsed = time.time() - start
    logger.info(f"Retrieved in {elapsed*1000:.2f}ms")
    logger.info(json.dumps(cached_location, indent=2))
