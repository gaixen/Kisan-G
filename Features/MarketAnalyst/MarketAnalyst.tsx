import React, { useState } from 'react';
import { getMarketData } from '../../src/services/api';
import axios from 'axios';

const MarketAnalyst: React.FC = () => {
  const [marketData, setMarketData] = useState<any>(null);
  const [commodity, setCommodity] = useState('Wheat');
  const [state, setState] = useState('Karnataka');
  const [market, setMarket] = useState('Bangalore');
  const [loading, setLoading] = useState(false);

  const fetchMarketData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/market', {
        params: { commodity, state, market, days: 7 }
      });
      setMarketData(response.data.data);
    } catch (error) {
      console.error('Error fetching market data:', error);
      // Fallback to mock data
      const fallbackData = await getMarketData();
      setMarketData(fallbackData);
    }
    setLoading(false);
  };

  React.useEffect(() => {
    fetchMarketData();
  }, [commodity, state, market]);

  return (
    <div className="max-w-2xl mx-auto p-4 pb-20">
      <h2 className="text-xl font-bold mb-4">Market Insights</h2>
      
      <div className="mb-4 space-y-2">
        <div className="flex gap-2">
          <select 
            value={commodity} 
            onChange={(e) => setCommodity(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="Wheat">Wheat</option>
            <option value="Rice">Rice</option>
            <option value="Potato">Potato</option>
            <option value="Onion">Onion</option>
          </select>
          
          <select 
            value={state} 
            onChange={(e) => setState(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="Karnataka">Karnataka</option>
            <option value="Maharashtra">Maharashtra</option>
            <option value="Punjab">Punjab</option>
          </select>
          
          <select 
            value={market} 
            onChange={(e) => setMarket(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="Bangalore">Bangalore</option>
            <option value="Mysore">Mysore</option>
            <option value="Hubli">Hubli</option>
          </select>
        </div>
        
        <button 
          onClick={fetchMarketData}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Refresh Data
        </button>
      </div>
      {loading ? (
        <div>Loading market data...</div>
      ) : marketData ? (
        <table className="w-full bg-white rounded shadow">
          <thead className="bg-green-100">
            <tr>
              <th className="py-2 px-3">Date</th>
              <th>Min Price (₹/Q)</th>
              <th>Max Price (₹/Q)</th>
              <th>Modal Price (₹/Q)</th>
              <th>Arrivals</th>
            </tr>
          </thead>
          <tbody>
            {marketData.map((row: any, i: number) => (
              <tr key={i}>
                <td className="py-2 px-3">{row.date}</td>
                <td>{row.min_price}</td>
                <td>{row.max_price}</td>
                <td>{row.modal_price}</td>
                <td>{row.arrivals} {row.unit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div>No market data available</div>
      )}
      {/* Sell advice and trends can go here */}
    </div>
  );
};
export default MarketAnalyst;
