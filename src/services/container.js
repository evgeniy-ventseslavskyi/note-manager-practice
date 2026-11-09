import { ApiClient } from './apiClient.js';

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000';

// Простий DI-контейнер: компоненти отримують залежності через props, а не створюють їх самі.
export const services = {
  api: new ApiClient(apiUrl),
  storage: window.localStorage
};
