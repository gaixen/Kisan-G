import React, { useState } from 'react';
import { getGovtSchemes } from '../../services/api';
import { FaSearch, FaExternalLinkAlt } from 'react-icons/fa';

const SchemeNavigator: React.FC = () => {
  const [query, setQuery] = useState('');
  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) {
      setError('Please enter a search query.');
      return;
    }

    setLoading(true);
    setError(null);
    setSchemes([]);

    try {
      const res = await getGovtSchemes(query);
      if (res.data.schemes && res.data.schemes.length > 0) {
        setSchemes(res.data.schemes);
      } else {
        setError('No schemes found matching your query.');
      }
    } catch (error) {
      console.error('Error fetching government schemes:', error);
      setError('Failed to fetch schemes. Please try again later.');
    }
    setLoading(false);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">Scheme Navigator</h2>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <form onSubmit={handleSubmit}>
          <div className="flex">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for schemes like 'crop insurance' or 'PM KISAN'"
              className="shadow appearance-none border rounded-l w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-r focus:outline-none focus:shadow-outline disabled:bg-gray-400 flex items-center"
            >
              {loading ? '...' : <FaSearch />}
            </button>
          </div>
        </form>
      </div>

      {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

      <div className="space-y-4">
        {schemes.map((scheme, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-800">{scheme.source.title}</h3>
            <p className="text-sm text-gray-500 mb-2">From: {scheme.source.organization}</p>
            <p className="text-gray-700 mb-4">{scheme.content}</p>
            <a
              href={scheme.source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              Learn More <FaExternalLinkAlt className="ml-2" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SchemeNavigator;