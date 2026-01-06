/**
 * useLocation Hook
 * 
 * React hook for easy location access in components
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getCurrentLocation,
  watchLocation,
  stopWatchingLocation,
  getLocationPermissionStatus,
  Location,
  LocationError,
} from '../services/locationService';

interface UseLocationOptions {
  watch?: boolean;
  enableHighAccuracy?: boolean;
  timeout?: number;
  maximumAge?: number;
  distanceFilter?: number;
  interval?: number;
}

interface UseLocationReturn {
  location: Location | null;
  loading: boolean;
  error: LocationError | null;
  permissionStatus: 'granted' | 'denied' | 'never_ask_again' | 'unknown' | null;
  refetch: () => Promise<void>;
  clearError: () => void;
}

/**
 * Hook to access device location
 * 
 * @param options - Configuration options
 * @returns Location state and control functions
 * 
 * @example
 * ```tsx
 * const { location, loading, error, refetch } = useLocation();
 * 
 * if (loading) return <Text>Loading location...</Text>;
 * if (error) return <Text>Error: {error.message}</Text>;
 * if (location) return <Text>Lat: {location.latitude}, Lon: {location.longitude}</Text>;
 * ```
 * 
 * @example With watching
 * ```tsx
 * const { location, loading } = useLocation({ watch: true });
 * // Location will automatically update as user moves
 * ```
 */
export const useLocation = (options?: UseLocationOptions): UseLocationReturn => {
  const [location, setLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<LocationError | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<
    'granted' | 'denied' | 'never_ask_again' | 'unknown' | null
  >(null);

  const {
    watch = false,
    enableHighAccuracy = true,
    timeout = 15000,
    maximumAge = 10000,
    distanceFilter = 100,
    interval = 10000,
  } = options || {};

  /**
   * Fetch current location
   */
  const fetchLocation = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const loc = await getCurrentLocation({
        enableHighAccuracy,
        timeout,
        maximumAge,
      });
      setLocation(loc);
    } catch (err: any) {
      setError({
        code: err.code || -1,
        message: err.message || 'Failed to get location',
      });
    } finally {
      setLoading(false);
    }
  }, [enableHighAccuracy, timeout, maximumAge]);

  /**
   * Check permission status
   */
  const checkPermission = useCallback(async () => {
    const status = await getLocationPermissionStatus();
    setPermissionStatus(status);
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  useEffect(() => {
    checkPermission();

    if (watch) {
      // Watch location changes
      const cleanup = watchLocation(
        (loc) => {
          setLocation(loc);
          setLoading(false);
          setError(null);
        },
        (err) => {
          setError(err);
          setLoading(false);
        },
        {
          enableHighAccuracy,
          distanceFilter,
          interval,
        }
      );

      return cleanup;
    } else {
      // Get location once
      fetchLocation();
    }
  }, [watch, fetchLocation, checkPermission]);

  return {
    location,
    loading,
    error,
    permissionStatus,
    refetch: fetchLocation,
    clearError,
  };
};

/**
 * Hook to watch location changes
 * 
 * @param callback - Function to call on location change
 * @param options - Configuration options
 * 
 * @example
 * ```tsx
 * useLocationWatch((location) => {
 *   console.log('Location updated:', location);
 * });
 * ```
 */
export const useLocationWatch = (
  callback: (location: Location) => void,
  options?: {
    enableHighAccuracy?: boolean;
    distanceFilter?: number;
    interval?: number;
  }
): void => {
  useEffect(() => {
    const cleanup = watchLocation(
      callback,
      (error) => {
        console.error('Location watch error:', error);
      },
      options
    );

    return cleanup;
  }, [callback, options]);
};

export default useLocation;
