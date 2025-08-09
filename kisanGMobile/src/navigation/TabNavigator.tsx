import React from 'react';
import { createMaterialBottomTabNavigator } from '@react-navigation/material-bottom-tabs';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import DashboardScreen from '../screens/Dashboard/DashboardScreen';
import CropDoctorScreen from '../screens/CropDoctor/CropDoctorScreen';
import MarketAnalystScreen from '../screens/MarketAnalyst/MarketAnalystScreen';
import ProfileScreen from '../screens/Profile/ProfileScreen';

import SchemeNavigatorScreen from '../screens/SchemeNavigator/SchemeNavigatorScreen';

const Tab = createMaterialBottomTabNavigator();

const TabNavigator = () => {
  return (
    <Tab.Navigator initialRouteName="Dashboard" activeColor="#fff">
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="home" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="CropDoctor"
        component={CropDoctorScreen}
        options={{
          tabBarLabel: 'Crop Doctor',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="leaf" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="MarketAnalyst"
        component={MarketAnalystScreen}
        options={{
          tabBarLabel: 'Market',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="chart-line" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="SchemeNavigator"
        component={SchemeNavigatorScreen}
        options={{
          tabBarLabel: 'Schemes',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="gift" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="account" color={color} size={26} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

export default TabNavigator;
