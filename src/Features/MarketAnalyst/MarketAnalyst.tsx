import React, { useState } from 'react';
import { getMarketTrends } from '../../services/api';
import { FaSearch, FaChartLine, FaArrowUp, FaArrowDown, FaMinus } from 'react-icons/fa';

const MarketAnalyst: React.FC = () => {
  const [commodity, setCommodity] = useState('Onion');
  const [state, setState] = useState('Maharashtra');
  const [market, setMarket] = useState('Pune');
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commodity || !state || !market) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError(null);
    setTrends(null);

    try {
      const res = await getMarketTrends(commodity, state, market);
      if (res.data && Object.keys(res.data).length > 0) {
        setTrends(res.data);
      } else {
        setError('No market data found for the selected criteria. Please try different options.');
      }
    } catch (error) {
      console.error('Error fetching market trends:', error);
      setError('Failed to fetch market trends. The data source may be unavailable.');
    }
    setLoading(false);
  };

  const TrendIcon = ({ trend }: { trend: string }) => {
    if (trend === 'upward') return <FaArrowUp className="text-green-500" />;
    if (trend === 'downward') return <FaArrowDown className="text-red-500" />;
    return <FaMinus className="text-gray-500" />;
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">Market Analyst</h2>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="commodity">
                Commodity
              </label>
              <input
                id="commodity"
                type="text"
                value={commodity}
                onChange={(e) => setCommodity(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
              />
            </div>
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="state">
                State
              </label>
              <input
                id="state"
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
              />
            </div>
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="market">
                Market
              </label>
              <input
                id="market"
                type="text"
                value={market}
                onChange={(e) => setMarket(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline disabled:bg-gray-400 flex items-center justify-center"
          >
            {loading ? 'Fetching...' : <><FaSearch className="mr-2" /> Get Trends</>}
          </button>
        </form>
      </div>

      {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

      {trends && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold mb-4 text-gray-700 flex items-center">
            <FaChartLine className="mr-3 text-blue-600" />
            Price Trends for {trends.commodity} in {trends.market}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600">Latest Price</p>
              <p className="text-2xl font-bold">₹{trends.latest_price}</p>
            </div>
            <div className="p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600">Trend</p>
              <div className="flex items-center justify-center text-2xl font-bold">
                <TrendIcon trend={trends.trend} />
                <span className="ml-2 capitalize">{trends.trend}</span>
              </div>
            </div>
            <div className="p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600">Change</p>
              <p className={`text-2xl font-bold ${trends.percentage_change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                {trends.percentage_change.toFixed(2)}%
              </p>
            </div>
            <div className="p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="text-2xl font-bold">{trends.data_points_found}</p>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div className="p-4">
              <p className="text-sm text-gray-600">Avg. Price</p>
              <p className="text-xl font-semibold">₹{trends.average_price}</p>
            </div>
            <div className="p-4">
              <p className="text-sm text-gray-600">Highest Price</p>
              <p className="text-xl font-semibold">₹{trends.highest_price}</p>
            </div>
            <div className="p-4">
              <p className="text-sm text-gray-600">Lowest Price</p>
              <p className="text-xl font-semibold">₹{trends.lowest_price}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketAnalyst;