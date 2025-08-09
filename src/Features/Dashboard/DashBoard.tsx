import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getLocation, getWeather, sendWhatsappMessage } from '../../services/api';
import { FaStethoscope, FaChartBar, FaGift, FaFlask, FaCloudSun, FaWhatsapp, FaLanguage } from 'react-icons/fa';
import NavBar from '../../components/NavBar';

const Dashboard: React.FC = () => {
  const [weather, setWeather] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [whatsappStatus, setWhatsappStatus] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        setError(null);
        const weatherRes = await getWeather();
        setWeather(weatherRes.data);
      } catch (err) {
        console.error('Error fetching weather data:', err);
        setError('Failed to load weather data.');
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, []);

  const handleTestWhatsapp = async () => {
    setWhatsappStatus("Sending...");
    try {
      // NOTE: Replace with a real number for testing
      const testPhoneNumber = "1234567890"; 
      const testMessage = "Hello from Agri-Assist! Your crop analysis is ready.";
      const res = await sendWhatsappMessage(testPhoneNumber, testMessage);
      setWhatsappStatus(`Success: ${res.data.status}`);
    } catch (err: any) {
      console.error('Error sending WhatsApp message:', err);
      const errorMsg = err.response?.data?.error || 'Failed to send message.';
      setWhatsappStatus(`Error: ${errorMsg}`);
    }
  };

  const features = [
    { path: "/crop-doctor", label: "Crop Doctor", icon: <FaStethoscope className="text-3xl" />, description: "Diagnose crop diseases from images." },
    { path: "/market-analyst", label: "Market Analyst", icon: <FaChartBar className="text-3xl" />, description: "Get the latest market price trends." },
    { path: "/scheme-navigator", label: "Scheme Navigator", icon: <FaGift className="text-3xl" />, description: "Find relevant government schemes." },
    { path: "/soil-analysis", label: "Soil Analysis", icon: <FaFlask className="text-3xl" />, description: "Check current soil conditions." },
    { path: "/Language-select", label : "Language Select", icon: <FaLanguage className="text-3xl" />, description: "Select your preferred language." },
  ];

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="p-6">
        <h1 className="text-3xl font-bold text-gray-800">Kisan-G</h1>
        <p className="text-gray-600">Your AI Farming Assistant</p>
      </div>

      {/* Weather Widget */}
      <div className="px-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-bold flex items-center"><FaCloudSun className="mr-2" /> Weather</h2>
          {loading && <p>Loading weather...</p>}
          {error && <p className="text-red-200">{error}</p>}
          {weather && weather.weather_info && weather.weather_info.length > 0 && (
            <div className="mt-4 flex justify-between items-center">
              <div>
                <p className="text-4xl font-bold">{weather.weather_info[0].temperature_2m?.toFixed(1)}°C</p>
                <p>Humidity: {weather.weather_info[0].relative_humidity_2m?.toFixed(0)}%</p>
              </div>
              <div className="text-right">
                <p>Rain: {weather.weather_info[0].rain?.toFixed(1)} mm</p>
                <p className="text-xs">Lat: {weather.latitude.toFixed(2)}, Lon: {weather.longitude.toFixed(2)}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="p-6 grid grid-cols-2 gap-4">
        {features.map(feature => (
          <Link to={feature.path} key={feature.label} className="bg-white p-4 rounded-lg shadow-md flex flex-col items-center text-center hover:bg-gray-100 transition">
            <div className="text-blue-600 mb-2">{feature.icon}</div>
            <h3 className="font-semibold text-gray-800">{feature.label}</h3>
            <p className="text-xs text-gray-500">{feature.description}</p>
          </Link>
        ))}
      </div>
      
      {/* Test Button Section */}
      <div className="px-6 mt-2">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="font-semibold text-gray-800 mb-2">Test Features</h3>
          <button
            onClick={handleTestWhatsapp}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center"
          >
            <FaWhatsapp className="mr-2" /> Send Test WhatsApp
          </button>
          {whatsappStatus && <p className="text-xs text-center mt-2 text-gray-600">{whatsappStatus}</p>}
        </div>
      </div>

      <NavBar />
    </div>
  );
};

export default Dashboard;