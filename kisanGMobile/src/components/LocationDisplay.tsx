/**
 * LocationDisplay Component
 * 
 * Example component demonstrating location service usage
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useLocation } from '../hooks/useLocation';

interface LocationDisplayProps {
  watch?: boolean;
}

const LocationDisplay: React.FC<LocationDisplayProps> = ({ watch = false }) => {
  const { location, loading, error, permissionStatus, refetch } = useLocation({
    watch,
  });

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Getting your location...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>❌ {error.message}</Text>
        <TouchableOpacity style={styles.button} onPress={refetch}>
          <Text style={styles.buttonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!location) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>No location available</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📍 Your Location</Text>
      
      <View style={styles.infoRow}>
        <Text style={styles.label}>Latitude:</Text>
        <Text style={styles.value}>{location.latitude.toFixed(6)}</Text>
      </View>
      
      <View style={styles.infoRow}>
        <Text style={styles.label}>Longitude:</Text>
        <Text style={styles.value}>{location.longitude.toFixed(6)}</Text>
      </View>
      
      {location.accuracy && (
        <View style={styles.infoRow}>
          <Text style={styles.label}>Accuracy:</Text>
          <Text style={styles.value}>±{location.accuracy.toFixed(0)}m</Text>
        </View>
      )}
      
      <View style={styles.infoRow}>
        <Text style={styles.label}>Source:</Text>
        <Text style={[styles.value, styles.sourceTag]}>
          {location.source.toUpperCase()}
        </Text>
      </View>
      
      {permissionStatus && (
        <View style={styles.infoRow}>
          <Text style={styles.label}>Permission:</Text>
          <Text
            style={[
              styles.value,
              permissionStatus === 'granted'
                ? styles.permissionGranted
                : styles.permissionDenied,
            ]}
          >
            {permissionStatus.toUpperCase()}
          </Text>
        </View>
      )}
      
      {!watch && (
        <TouchableOpacity style={styles.button} onPress={refetch}>
          <Text style={styles.buttonText}>🔄 Refresh Location</Text>
        </TouchableOpacity>
      )}
      
      {watch && (
        <View style={styles.watchIndicator}>
          <View style={styles.pulseDot} />
          <Text style={styles.watchText}>Live tracking enabled</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  value: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  sourceTag: {
    backgroundColor: '#e3f2fd',
    color: '#1976d2',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
  },
  permissionGranted: {
    color: '#4CAF50',
  },
  permissionDenied: {
    color: '#f44336',
  },
  button: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginTop: 16,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  errorText: {
    fontSize: 14,
    color: '#f44336',
    textAlign: 'center',
    marginBottom: 16,
  },
  text: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  watchIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  pulseDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#4CAF50',
    marginRight: 8,
  },
  watchText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
  },
});

export default LocationDisplay;
