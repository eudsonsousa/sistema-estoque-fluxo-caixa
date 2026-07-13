import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptar requisições para adicionar o token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptar respostas para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirou ou inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (name, email, password) =>
    api.post('/auth/register', { name, email, password }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  getCurrentUser: () =>
    api.get('/auth/me'),
};

// Products
export const productsAPI = {
  list: (page = 1, perPage = 10, activeOnly = true) =>
    api.get('/products', { params: { page, per_page: perPage, active_only: activeOnly } }),
  get: (productId) =>
    api.get(`/products/${productId}`),
  create: (productData) =>
    api.post('/products', productData),
  update: (productId, productData) =>
    api.put(`/products/${productId}`, productData),
  duplicate: (productId, newSku, newName) =>
    api.post(`/products/${productId}/duplicate`, { new_sku: newSku, new_name: newName }),
  delete: (productId) =>
    api.delete(`/products/${productId}`),
};

// Inventory
export const inventoryAPI = {
  list: (page = 1, perPage = 10, warehouse = 'Principal') =>
    api.get('/inventory', { params: { page, per_page: perPage, warehouse } }),
  get: (inventoryId) =>
    api.get(`/inventory/${inventoryId}`),
  listMovements: (page = 1, perPage = 10, type = null) =>
    api.get('/inventory/movements', { params: { page, per_page: perPage, type } }),
  createMovement: (movementData) =>
    api.post('/inventory/movements', movementData),
};

// CashFlow
export const cashflowAPI = {
  list: (page = 1, perPage = 10, type = null, status = null) =>
    api.get('/cashflow', { params: { page, per_page: perPage, type, status } }),
  getSummary: () =>
    api.get('/cashflow/summary'),
  create: (cashflowData) =>
    api.post('/cashflow', cashflowData),
  update: (cashflowId, cashflowData) =>
    api.put(`/cashflow/${cashflowId}`, cashflowData),
};

// Reports
export const reportsAPI = {
  inventorySummary: (warehouse = 'Principal') =>
    api.get('/reports/inventory-summary', { params: { warehouse } }),
  cashflowSummary: (period = '30') =>
    api.get('/reports/cashflow-summary', { params: { period } }),
  movementsReport: (period = '30', type = null) =>
    api.get('/reports/movements', { params: { period, type } }),
};

export default api;
