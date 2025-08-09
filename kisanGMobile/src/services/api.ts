import axios from 'axios';

// IMPORTANT: Replace with your actual backend server address.
// If running the backend locally and the app on an Android emulator, use 'http://10.0.2.2:5001/api'
// If running on a physical device, use your computer's local IP address.
const API_BASE_URL = 'http://10.0.2.2:5001/api';

export const getWeather = () => {
  return axios.get(`${API_BASE_URL}/weather`);
};

export const getGovtSchemes = (query: string) => {
  return axios.get(`${API_BASE_URL}/govt-schemes`, {
    params: { query },
  });
};

export const getMarketTrends = (commodity: string, state: string, market: string) => {
  return axios.post(`${API_BASE_URL}/market-trends`, {
    commodity,
    state,
    market,
  });
};

export const analyzeCrop = (formData: FormData) => {
  return axios.post(`${API_BASE_URL}/crop-analysis`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const speechToText = (formData: FormData) => {
  return axios.post(`${API_BASE_URL}/speech-to-text`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Add other API functions from your web app here as needed...
