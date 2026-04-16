import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export const generateContent = async (payload) => {
  const res = await axios.post(`${BASE_URL}/generate`, payload);
  return res.data;
};