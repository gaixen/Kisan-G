import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export const getLocation = () => {
  return axios.get(`${API_BASE_URL}/location`);
};

export const analyzeCrop = (formData: FormData) => {
  return axios.post(`${API_BASE_URL}/crop-analysis`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getMarketTrends = (commodity: string, state: string, market: string) => {
  return axios.post(`${API_BASE_URL}/market-trends`, {
    commodity,
    state,
    market,
  });
};

export const getGovtSchemes = (query: string) => {
  return axios.get(`${API_BASE_URL}/govt-schemes`, {
    params: { query },
  });
};

export const speechToText = (formData: FormData) => {
  return axios.post(`${API_BASE_URL}/speech-to-text`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getWeather = () => {
  return axios.get(`${API_BASE_URL}/weather`);
};



export const getSoilAnalysis = (latitude: number, longitude: number) => {
  return axios.get(`${API_BASE_URL}/soil-analysis`, {
    params: { latitude, longitude },
  });
};

export const sendWhatsappMessage = (phoneNumber: string, message: string) => {
  return axios.post(`${API_BASE_URL}/whatsapp/send`, {
    to_phone_number: phoneNumber,
    message,
  });
};

