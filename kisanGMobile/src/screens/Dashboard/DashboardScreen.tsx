import React from 'react';
import { ScrollView, View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import FeatureCard from '../../components/FeatureCard';
import WeatherWidget from '../../components/WeatherWidget';

import VoiceAssistantUI from '../../components/VoiceAssistantUI';

const features = [
  {
    title: 'Crop Doctor',
    description: 'Diagnose crop diseases',
    icon: 'leaf',
    screen: 'CropDoctor',
  },
  {
    title: 'Market Analyst',
    description: 'Get market price trends',
    icon: 'chart-line',
    screen: 'MarketAnalyst',
  },
  {
    title: 'Scheme Navigator',
    description: 'Find government schemes',
    icon: 'gift',
    screen: 'SchemeNavigator',
  },
  {
    title: 'Profile',
    description: 'View your profile',
    icon: 'account',
    screen: 'Profile',
  },
];

const DashboardScreen = ({ navigation }: any) => {
  return (
    <View style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Kisan-G</Text>
        <Text style={styles.subtitle}>Your AI Farming Assistant</Text>
        
        <WeatherWidget />

        <View style={styles.grid}>
          {features.map((feature) => (
            <FeatureCard
              key={feature.title}
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              onPress={() => navigation.navigate(feature.screen)}
            />
          ))}
        </View>
      </ScrollView>
      <VoiceAssistantUI />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginHorizontal: 16,
    marginTop: 16,
  },
  subtitle: {
    fontSize: 18,
    marginHorizontal: 16,
    marginBottom: 8,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
});

export default DashboardScreen;
