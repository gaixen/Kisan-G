import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { analyzeCrop } from '../../services/api';
import { FaUpload, FaPaperPlane } from 'react-icons/fa';

const CropDoctor: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload an image of the crop.');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('query', query);

    try {
      const res = await analyzeCrop(formData);
      setAnalysis(res.data);
    } catch (error) {
      console.error('Error analyzing crop:', error);
      setError('Failed to analyze crop. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">Crop Doctor</h2>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Upload Crop Image
            </label>
            <div className="flex items-center">
              <label className="w-full flex flex-col items-center px-4 py-6 bg-white text-blue rounded-lg shadow-lg tracking-wide uppercase border border-blue cursor-pointer hover:bg-blue-500 hover:text-white">
                <FaUpload className="w-8 h-8" />
                <span className="mt-2 text-base leading-normal">{file ? file.name : 'Select a file'}</span>
                <input type='file' className="hidden" onChange={handleFileChange} accept="image/*" />
              </label>
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="query">
              Describe the issue (optional)
            </label>
            <input
              id="query"
              type="text"
              value={query}
              onChange={handleQueryChange}
              placeholder="e.g., 'The leaves have yellow spots.'"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline disabled:bg-gray-400 flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                <FaPaperPlane className="mr-2" /> Analyze
              </>
            )}
          </button>
        </form>
      </div>

      {error && <p className="mt-6 text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

      {analysis && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold mb-4 text-gray-700">Analysis Report</h3>
          <div className="prose max-w-none">
            <ReactMarkdown>{analysis.final_report}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default CropDoctor;