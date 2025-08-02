import React, { useState, useContext } from 'react';
import { searchSchemes, applyScheme } from '../../src/services/api';
import { AppContext } from '../../src/hooks/AppContext';

const SchemeNavigator: React.FC = () => {
  const { user } = useContext(AppContext);
  const [query, setQuery] = useState('');
  const [schemes, setSchemes] = useState<any[]>([]);
  const [message, setMessage] = useState('');
  const [applying, setApplying] = useState(false);

  const handleSearch = async () => {
    setMessage('');
    const results = await searchSchemes(query, user);
    setSchemes(results || []);
  };

  const handleApply = async (schemeId: string) => {
    setApplying(true);
    const result = await applyScheme(schemeId, user);
    setMessage(result?.message || "Application submitted!");
    setApplying(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-4 pb-20">
      <h2 className="text-xl font-bold mb-4">Government Schemes</h2>
      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search for subsidies, insurance, etc"
          className="border rounded px-4 py-2 flex-1"
        />
        <button onClick={handleSearch} className="bg-primary text-white px-4 py-2 rounded">Search</button>
      </div>
      {schemes.length === 0 && <div className="text-gray-600">Try searching for: Fertilizer, Drip Irrigation, PM-KISAN…</div>}
      {schemes.map((scheme: any) => (
        <div key={scheme.id} className="bg-white p-4 rounded-xl shadow mb-3 flex flex-col gap-1">
          <div className="font-semibold text-base">{scheme.title}</div>
          <div className="text-gray-700 text-sm">{scheme.description}</div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-primary font-bold">{scheme.eligibility}</span>
            {scheme.eligible && (
              <button
                className="bg-accent text-white px-3 py-1 rounded hover:bg-yellow-600"
                onClick={() => handleApply(scheme.id)}
                disabled={applying}
              >Apply Now</button>
            )}
          </div>
        </div>
      ))}
      {message && <div className="text-green-700 my-2 font-semibold">{message}</div>}
    </div>
  );
};
export default SchemeNavigator;
