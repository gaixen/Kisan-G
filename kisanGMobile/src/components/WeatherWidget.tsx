import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, ActivityIndicator } from 'react-native-paper';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { getWeather } from '../services/api';

const WeatherWidget = () => {
  const [weather, setWeather] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const res = await getWeather();
        setWeather(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load weather.');
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, []);

  return (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.header}>
          <MaterialCommunityIcons name="weather-cloudy" size={24} color="#fff" />
          <Text style={styles.headerText}>Weather</Text>
        </View>
        
        {loading ? (
          <ActivityIndicator animating={true} color="#fff" style={styles.loader} />
        ) : error ? (
          <Text style={styles.errorText}>{error}</Text>
        ) : weather && weather.weather_info && weather.weather_info.length > 0 ? (
          <View style={styles.content}>
            <View>
              <Text style={styles.tempText}>{weather.weather_info[0].temperature_2m?.toFixed(1)}°C</Text>
              <Text style={styles.detailText}>Humidity: {weather.weather_info[0].relative_humidity_2m?.toFixed(0)}%</Text>
            </View>
            <View style={styles.rightContent}>
              <Text style={styles.detailText}>Rain: {weather.weather_info[0].rain?.toFixed(1)} mm</Text>
            </View>
          </View>
        ) : (
          <Text style={styles.errorText}>No weather data available.</Text>
        )}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    margin: 16,
    backgroundColor: '#42A5F5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  loader: {
    marginVertical: 20,
  },
  errorText: {
    color: '#fff',
    textAlign: 'center',
    marginVertical: 20,
  },
  tempText: {
    color: '#fff',
    fontSize: 48,
    fontWeight: 'bold',
  },
  detailText: {
    color: '#fff',
  },
  rightContent: {
    justifyContent: 'flex-end',
  },
});

export default WeatherWidget;
