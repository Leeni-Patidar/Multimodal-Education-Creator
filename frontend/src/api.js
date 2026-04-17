import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export const generateContent = async (payload) => {
  const res = await axios.post(`${BASE_URL}/generate`, payload);
  return res.data;
};

export const getHistory = async (limit = 10) => {
  const res = await axios.get(`${BASE_URL}/history?limit=${limit}`);
  return res.data;
};

export const searchHistory = async (query = "", category = "", level = "", limit = 10) => {
  const params = new URLSearchParams({
    query,
    category,
    level,
    limit
  });
  const res = await axios.get(`${BASE_URL}/history/search?${params}`);
  return res.data;
};

export const getVectorDBStats = async () => {
  const res = await axios.get(`${BASE_URL}/vector-db/stats`);
  return res.data;
};