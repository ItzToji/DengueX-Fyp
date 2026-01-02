import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
});

export const sendQuestion = async (question) => {
  const res = await api.post("chat/", { question });
  return res.data;
};
