/**
 * Location Service for Kisan-G Mobile Application
 * 
 * Provides device location access with:
 * - Permission handling
 * - Caching
 * - Error handling
 * - Fallback strategies
 */

import Geolocation from '@react-native-community/geolocation';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Types
export interface Location {
  latitude: number;
  longitude: number;
  accuracy?: number;
  altitude?: number | null;
  heading?: number | null;
  speed?: number | null;
  timestamp: number;
  source: 'gps' | 'network' | 'cached' | 'fallback';
}

export interface LocationError {
  code: number;
  message: string;
}

// Constants
const LOCATION_CACHE_KEY = '@kisan_g_location';
const LOCATION_CACHE_DURATION = 60 * 60 * 1000; // 1 hour in milliseconds

// Default fallback location (same as backend)
const FALLBACK_LOCATION: Location = {
  latitude: 52.52,
  longitude: 13.41,
  accuracy: undefined,
  timestamp: Date.now(),
  source: 'fallback',
};

/**
 * Location Service Class
 * Singleton pattern for managing location access
 */
class LocationService {
  private static instance: LocationService;
  private cachedLocation: Location | null = null;
  private watchId: number | null = null;

  private constructor() {
    this.loadCachedLocation();
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): LocationService {
    if (!LocationService.instance) {
      LocationService.instance = new LocationService();
    }
    return LocationService.instance;
  }

  /**
   * Request location permissions (Android)
   */
  private async requestLocationPermission(): Promise<boolean> {
    if (Platform.OS === 'ios') {
      // iOS permissions are handled via Info.plist
      return true;
    }

    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: 'Kisan-G Location Permission',
          message:
            'Kisan-G needs access to your location to provide weather updates, ' +
            'soil analysis, and location-specific farming information.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        }
      );

      return granted === PermissionsAndroid.RESULTS.GRANTED;
    } catch (err) {
      console.error('Error requesting location permission:', err);
      return false;
    }
  }

  /**
   * Check if location permission is granted
   */
  private async checkLocationPermission(): Promise<boolean> {
    if (Platform.OS === 'ios') {
      return true; // iOS handles this differently
    }

    try {
      const granted = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      return granted;
    } catch (err) {
      console.error('Error checking location permission:', err);
      return false;
    }
  }

  /**
   * Load cached location from storage
   */
  private async loadCachedLocation(): Promise<void> {
    try {
      const cached = await AsyncStorage.getItem(LOCATION_CACHE_KEY);
      if (cached) {
        const location: Location = JSON.parse(cached);
        
        // Check if cache is still valid
        if (Date.now() - location.timestamp < LOCATION_CACHE_DURATION) {
          this.cachedLocation = location;
        } else {
          // Clear expired cache
          await AsyncStorage.removeItem(LOCATION_CACHE_KEY);
        }
      }
    } catch (error) {
      console.error('Error loading cached location:', error);
    }
  }

  /**
   * Save location to cache
   */
  private async saveLocationToCache(location: Location): Promise<void> {
    try {
      await AsyncStorage.setItem(LOCATION_CACHE_KEY, JSON.stringify(location));
      this.cachedLocation = location;
    } catch (error) {
      console.error('Error saving location to cache:', error);
    }
  }

  /**
   * Get current location
   */
  public async getCurrentLocation(options?: {
    useCache?: boolean;
    timeout?: number;
    maximumAge?: number;
    enableHighAccuracy?: boolean;
  }): Promise<Location> {
    const {
      useCache = true,
      timeout = 15000,
      maximumAge = 10000,
      enableHighAccuracy = true,
    } = options || {};

    // Return cached location if valid and cache is enabled
    if (useCache && this.cachedLocation) {
      const age = Date.now() - this.cachedLocation.timestamp;
      if (age < LOCATION_CACHE_DURATION) {
        console.log('Returning cached location');
        return this.cachedLocation;
      }
    }

    // Check and request permissions
    let hasPermission = await this.checkLocationPermission();
    if (!hasPermission) {
      hasPermission = await this.requestLocationPermission();
    }

    if (!hasPermission) {
      console.warn('Location permission denied, using fallback');
      return FALLBACK_LOCATION;
    }

    // Get current position
    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        (position) => {
          const location: Location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            heading: position.coords.heading,
            speed: position.coords.speed,
            timestamp: position.timestamp,
            source: 'gps',
          };

          // Cache the location
          this.saveLocationToCache(location);

          resolve(location);
        },
        (error) => {
          console.error('Error getting location:', error);
          
          // Try to return cached location if available
          if (this.cachedLocation) {
            console.log('Returning cached location after error');
            resolve({ ...this.cachedLocation, source: 'cached' });
          } else {
            // Use fallback location
            console.log('Using fallback location');
            resolve(FALLBACK_LOCATION);
          }
        },
        {
          enableHighAccuracy,
          timeout,
          maximumAge,
        }
      );
    });
  }

  /**
   * Watch location changes
   */
  public watchLocation(
    onLocationChange: (location: Location) => void,
    onError?: (error: LocationError) => void,
    options?: {
      enableHighAccuracy?: boolean;
      distanceFilter?: number;
      interval?: number;
    }
  ): () => void {
    const {
      enableHighAccuracy = true,
      distanceFilter = 100, // 100 meters
      interval = 10000, // 10 seconds
    } = options || {};

    // Request permission first
    this.checkLocationPermission().then((hasPermission) => {
      if (!hasPermission) {
        this.requestLocationPermission().then((granted) => {
          if (!granted && onError) {
            onError({
              code: 1,
              message: 'Location permission denied',
            });
          }
        });
      }
    });

    // Start watching
    this.watchId = Geolocation.watchPosition(
      (position) => {
        const location: Location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          heading: position.coords.heading,
          speed: position.coords.speed,
          timestamp: position.timestamp,
          source: 'gps',
        };

        this.saveLocationToCache(location);
        onLocationChange(location);
      },
      (error) => {
        console.error('Watch location error:', error);
        if (onError) {
          onError({
            code: error.code,
            message: error.message,
          });
        }
      },
      {
        enableHighAccuracy,
        distanceFilter,
        interval,
        fastestInterval: interval / 2,
      }
    );

    // Return cleanup function
    return () => {
      if (this.watchId !== null) {
        Geolocation.clearWatch(this.watchId);
        this.watchId = null;
      }
    };
  }

  /**
   * Stop watching location
   */
  public stopWatching(): void {
    if (this.watchId !== null) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }

  /**
   * Clear cached location
   */
  public async clearCache(): Promise<void> {
    try {
      await AsyncStorage.removeItem(LOCATION_CACHE_KEY);
      this.cachedLocation = null;
    } catch (error) {
      console.error('Error clearing location cache:', error);
    }
  }

  /**
   * Get location permission status
   */
  public async getPermissionStatus(): Promise<
    'granted' | 'denied' | 'never_ask_again' | 'unknown'
  > {
    if (Platform.OS === 'ios') {
      return 'unknown'; // iOS doesn't provide this info directly
    }

    try {
      const result = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      return result ? 'granted' : 'denied';
    } catch (error) {
      return 'unknown';
    }
  }

  /**
   * Show location settings alert
   */
  public showLocationSettingsAlert(): void {
    Alert.alert(
      'Location Permission Required',
      'Kisan-G needs your location to provide accurate weather, soil analysis, and farming information. Please enable location access in settings.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Open Settings',
          onPress: () => {
            if (Platform.OS === 'android') {
              PermissionsAndroid.request(
                PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
              );
            }
            // For iOS, you'd typically use Linking.openSettings()
          },
        },
      ]
    );
  }
}

// Export singleton instance
export default LocationService.getInstance();

// Helper functions for easy use
export const getCurrentLocation = (options?: {
  useCache?: boolean;
  timeout?: number;
  maximumAge?: number;
  enableHighAccuracy?: boolean;
}): Promise<Location> => {
  return LocationService.getInstance().getCurrentLocation(options);
};

export const watchLocation = (
  onLocationChange: (location: Location) => void,
  onError?: (error: LocationError) => void,
  options?: {
    enableHighAccuracy?: boolean;
    distanceFilter?: number;
    interval?: number;
  }
): (() => void) => {
  return LocationService.getInstance().watchLocation(
    onLocationChange,
    onError,
    options
  );
};

export const stopWatchingLocation = (): void => {
  LocationService.getInstance().stopWatching();
};

export const clearLocationCache = (): Promise<void> => {
  return LocationService.getInstance().clearCache();
};

export const getLocationPermissionStatus = (): Promise<
  'granted' | 'denied' | 'never_ask_again' | 'unknown'
> => {
  return LocationService.getInstance().getPermissionStatus();
};

export const showLocationSettingsAlert = (): void => {
  LocationService.getInstance().showLocationSettingsAlert();
};
