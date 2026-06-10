import axios from 'axios'
import { useAuthStore } from '../store/auth.js'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const { state } = useAuthStore()
  if (state.token) {
    config.headers.Authorization = `Bearer ${state.token}`
  }
  if (state.currentParkId) {
    config.headers['X-Park-Id'] = state.currentParkId
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      const { logout } = useAuthStore()
      logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth
export const authApi = {
  login: (data) => api.post('/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  me: () => api.get('/auth/me'),
  changePassword: (data) => api.put('/auth/password', data),
}

// Admin
export const adminApi = {
  listParks: () => api.get('/admin/parks'),
  createPark: (data) => api.post('/admin/parks', data),
  updatePark: (id, data) => api.put(`/admin/parks/${id}`, data),
  deletePark: (id) => api.delete(`/admin/parks/${id}`),
  listUsers: (params) => api.get('/admin/users', { params }),
  createUser: (data) => api.post('/admin/users', data),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  resetPassword: (id, data) => api.put(`/admin/users/${id}/reset-password`, data),
}

// Cycles
export const cycleApi = {
  list: () => api.get('/cycles'),
  create: (data) => api.post('/cycles', data),
  update: (id, data) => api.put(`/cycles/${id}`, data),
  delete: (id) => api.delete(`/cycles/${id}`),
  activate: (id) => api.put(`/cycles/${id}/activate`)
}

// Job Types
export const jobTypeApi = {
  list: () => api.get('/job-types'),
  create: (data) => api.post('/job-types', data),
  update: (id, data) => api.put(`/job-types/${id}`, data),
  delete: (id) => api.delete(`/job-types/${id}`)
}

// Wages
export const wageApi = {
  list: (params) => api.get('/wages', { params }),
  create: (data) => api.post('/wages', data),
  update: (id, data) => api.put(`/wages/${id}`, data),
  delete: (id) => api.delete(`/wages/${id}`)
}

// Expenses
export const expenseApi = {
  list: (params) => api.get('/expenses', { params }),
  create: (data) => api.post('/expenses', data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`)
}

// Expense Categories
export const expenseCategoryApi = {
  list: () => api.get('/expense-categories'),
  create: (data) => api.post('/expense-categories', data),
  delete: (id) => api.delete(`/expense-categories/${id}`)
}

// Reports
export const reportApi = {
  summary: (params) => api.get('/report/summary', { params })
}

// Investments
export const investmentApi = {
  list: (params) => api.get('/investments', { params }),
  create: (data) => api.post('/investments', data),
  delete: (id) => api.delete(`/investments/${id}`),
  balance: (params) => api.get('/investments/balance', { params })
}

// Grape Grades
export const grapeGradeApi = {
  list: () => api.get('/grape-grades'),
  create: (data) => api.post('/grape-grades', data),
  update: (id, data) => api.put(`/grape-grades/${id}`, data),
  delete: (id) => api.delete(`/grape-grades/${id}`)
}

// Incomes
export const incomeApi = {
  list: (params) => api.get('/incomes', { params }),
  create: (data) => api.post('/incomes', data),
  delete: (id) => api.delete(`/incomes/${id}`)
}

// Grape Bunch Config
export const grapeBunchApi = {
  get: (params) => api.get('/grape-bunch-config', { params }),
  update: (params, data) => api.put('/grape-bunch-config', data, { params })
}

// Dividends
export const dividendApi = {
  list: (params) => api.get('/dividends', { params }),
  summary: (params) => api.get('/dividends/summary', { params })
}

export default api
