// src/components/WeatherWidget.tsx
import React from 'react';
import { WiDaySunny, WiCloudy, WiRain } from 'react-icons/wi';

type WeatherWidgetProps = {
  location?: string;
  temperature?: number;
  condition?: 'Sunny' | 'Cloudy' | 'Rainy' | string;
};

const WeatherWidget: React.FC<WeatherWidgetProps> = ({
  location = 'Bengaluru, Karnataka',
  temperature = 30,
  condition = 'Partly Sunny',
}) => {
  // Map condition to icon component
  const icon = (() => {
    if (condition.toLowerCase().includes('sunny')) return <WiDaySunny size={48} color="#f6ad55" />;
    if (condition.toLowerCase().includes('cloudy')) return <WiCloudy size={48} color="#718096" />;
    if (condition.toLowerCase().includes('rain')) return <WiRain size={48} color="#4299e1" />;
    return <WiDaySunny size={48} color="#f6ad55" />;
  })();

  return (
    <div className="bg-blue-100 rounded-xl p-4 flex items-center gap-4 shadow-sm">
      <div>{icon}</div>
      <div>
        <p className="font-semibold text-lg">{location}</p>
        <p className="text-3xl font-bold">{temperature}°C</p>
        <p className="text-sm text-gray-700">{condition}</p>
      </div>
    </div>
  );
};

export default WeatherWidget;
