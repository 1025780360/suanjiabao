import axios from 'axios'

function getDefaultBaseUrl() {
  const { protocol, hostname } = window.location
  if (protocol === 'capacitor:') return 'http://192.168.1.7:8000/api'
  if (hostname === 'localhost' || hostname === '127.0.0.1') return 'http://127.0.0.1:8000/api'
  return `${protocol}//${hostname}:8000/api`
}

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || getDefaultBaseUrl(),
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('garment_token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export async function getHealth() {
  const response = await http.get('/health/')
  return response.data
}

export async function registerAccount(data: unknown) {
  const response = await http.post('/auth/register/', data)
  return response.data
}

export async function loginAccount(data: unknown) {
  const response = await http.post('/auth/login/', data)
  return response.data
}

export async function getMe() {
  const response = await http.get('/auth/me/')
  return response.data
}

export async function updateProfile(data: unknown) {
  const response = await http.put('/auth/profile/', data)
  return response.data
}

export async function getQuickCategories() {
  const response = await http.get('/costing/quick-categories/')
  return response.data
}

export async function createQuickCategory(data: unknown) {
  const response = await http.post('/costing/quick-categories/', data)
  return response.data
}

export async function getQuickStyles() {
  const response = await http.get('/costing/quick-styles/')
  return response.data
}

export async function createQuickStyle(data: unknown) {
  // axios auto-detects FormData and sets Content-Type multipart/form-data with boundary
  const response = await http.post('/costing/quick-styles/', data)
  return response.data
}

export async function costingChat(data: unknown) {
  const response = await http.post('/ai/costing-chat/', data)
  return response.data
}

export async function getAiChatHistory() {
  const response = await http.get('/costing/ai/chat-history/')
  return response.data
}

export async function deleteQuickStyle(id: number) {
  const response = await http.delete(`/costing/quick-styles/${id}/`)
  return response.data
}

export async function deleteQuickCategory(key: string) {
  const response = await http.delete(`/costing/quick-categories/${key}/`)
  return response.data
}

export async function getMembershipInfo() {
  const response = await http.get('/auth/membership/')
  return response.data
}

export async function upgradePlan(data: { plan?: string; billing?: string; extension?: { type: string; amount: number } }) {
  const response = await http.post('/auth/upgrade/', data)
  return response.data
}

// 客服 API
export async function getSupportChat() {
  const response = await http.get('/auth/support/chat/')
  return response.data
}
export async function sendSupportMessage(content: string) {
  const response = await http.post('/auth/support/chat/', { content })
  return response.data
}
export async function getSupportPayments() {
  const response = await http.get('/auth/support/payments/')
  return response.data
}
export async function confirmPayment(id: number) {
  const response = await http.post('/auth/support/payments/', { id })
  return response.data
}
export async function getSupportRooms() {
  const response = await http.get('/auth/support/rooms/')
  return response.data
}
export async function getStaffRoomChat(roomId: number) {
  const response = await http.get(`/auth/support/rooms/${roomId}/`)
  return response.data
}
export async function sendStaffMessage(roomId: number, content: string) {
  const response = await http.post(`/auth/support/rooms/${roomId}/`, { content })
  return response.data
}
