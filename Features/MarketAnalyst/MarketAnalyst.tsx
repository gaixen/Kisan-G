import React, { useState } from 'react';
import { getMarketData } from '../../src/services/api';

const MarketAnalyst: React.FC = () => {
  const [marketData, setMarketData] = useState<any>(null);

  React.useEffect(() => {
    getMarketData().then(setMarketData);
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4 pb-20">
      <h2 className="text-xl font-bold mb-4">Market Insights</h2>
      {marketData ? (
        <table className="w-full bg-white rounded shadow">
          <thead className="bg-green-100">
            <tr>
              <th className="py-2 px-3">Commodity</th>
              <th>Date</th>
              <th>Price (₹/kg)</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {marketData.map((row: any, i: number) => (
              <tr key={i}>
                <td className="py-2 px-3">{row.commodity}</td>
                <td>{row.date}</td>
                <td>{row.price}</td>
                <td>{row.trend > 0 ? "↑" : row.trend < 0 ? "↓" : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div>Loading market data...</div>
      )}
      {/* Sell advice and trends can go here */}
    </div>
  );
};
export default MarketAnalyst;
