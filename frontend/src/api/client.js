const API_BASE = import.meta.env.VITE_API_URL || ''

function getToken() {
  return localStorage.getItem('token')
}

function authHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.message || data.error || `Request failed (${res.status})`)
  }
  return data
}

export const api = {
  health: () => request('/health'),

  register: (body) =>
    request('/api/v1/auth/register', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(body),
    }),

  login: (body) =>
    request('/api/v1/auth/login', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(body),
    }),

  getProducts: () =>
    request('/api/v1/products', { headers: authHeaders() }),

  getCart: () =>
    request('/api/v1/cart', { headers: authHeaders() }),

  addToCart: (item) =>
    request('/api/v1/cart/add', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(item),
    }),

  removeFromCart: (productId) =>
    request('/api/v1/cart/remove', {
      method: 'DELETE',
      headers: authHeaders(),
      body: JSON.stringify({ product_id: productId }),
    }),

  createOrder: (payload) =>
    request('/api/v1/orders/create', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    }),

  processPayment: (payload) =>
    request('/api/v1/payments/process', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    }),

  sendNotification: (payload) =>
    request('/api/v1/notifications/send', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    }),
}
