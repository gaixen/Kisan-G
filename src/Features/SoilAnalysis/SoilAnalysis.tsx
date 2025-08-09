
import React, { useState, useEffect } from 'react';
import { getSoilAnalysis, getLocation } from '../../services/api'; // Assuming these functions exist in api.ts

const SoilAnalysis: React.FC = () => {
  const [soilData, setSoilData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSoilData = async () => {
      try {
        setLoading(true);
        setError(null);

        // 1. Get location
        const locationRes = await getLocation();
        const { latitude, longitude } = locationRes.data.location;

        // 2. Get soil data for that location
        const soilRes = await getSoilAnalysis(latitude, longitude);
        setSoilData(soilRes.data);

      } catch (err) {
        console.error('Error fetching soil data:', err);
        setError('Failed to fetch soil analysis data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSoilData();
  }, []);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">Soil Analysis</h2>
      {loading && <p className="text-center text-gray-600">Loading Soil Data...</p>}
      {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}
      {soilData && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold mb-4 text-gray-700">Current Soil Conditions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-medium text-gray-600">Soil Temperature (0-7cm)</h4>
              <p className="text-4xl font-bold text-blue-600">
                {soilData.soil_temperature_0_to_7cm[0]?.toFixed(2) ?? 'N/A'} °C
              </p>
              <p className="text-sm text-gray-500">Latest reading</p>
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-600">Soil Moisture (0-7cm)</h4>
              <p className="text-4xl font-bold text-green-600">
                {soilData.soil_moisture_0_to_7cm[0]?.toFixed(3) ?? 'N/A'} m³/m³
              </p>
              <p className="text-sm text-gray-500">Latest reading</p>
            </div>
          </div>
          <div className="mt-6">
            <h4 className="text-lg font-medium text-gray-600 mb-2">Hourly Forecast</h4>
            {/* Here you could add a chart to visualize the hourly data */}
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border">
                    <thead className="bg-gray-200">
                        <tr>
                            <th className="py-2 px-4 border-b">Time</th>
                            <th className="py-2 px-4 border-b">Temperature (°C)</th>
                            <th className="py-2 px-4 border-b">Moisture (m³/m³)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {soilData.time.slice(0, 24).map((time: string, index: number) => (
                            <tr key={time} className="hover:bg-gray-100">
                                <td className="py-2 px-4 border-b">{new Date(time).toLocaleTimeString()}</td>
                                <td className="py-2 px-4 border-b">{soilData.soil_temperature_0_to_7cm[index]?.toFixed(2)}</td>
                                <td className="py-2 px-4 border-b">{soilData.soil_moisture_0_to_7cm[index]?.toFixed(3)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SoilAnalysis;
