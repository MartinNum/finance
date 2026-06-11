import { reactive } from 'vue'

const state = reactive({
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  currentParkId: localStorage.getItem('currentParkId')
    ? parseInt(localStorage.getItem('currentParkId'))
    : null,
})

function login(token, user) {
  state.token = token
  state.user = user
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
  if (user.role !== 'admin') {
    state.currentParkId = user.park_id
    localStorage.setItem('currentParkId', String(user.park_id))
  }
}

function logout() {
  state.token = null
  state.user = null
  state.currentParkId = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('currentParkId')
}

function setCurrentParkId(parkId) {
  state.currentParkId = parkId
  localStorage.setItem('currentParkId', String(parkId))
}

const isAdmin = () => state.user?.role === 'admin'
const isLoggedIn = () => !!state.token
const canEdit = () => state.user?.role === 'admin' || state.user?.can_edit !== false

export function useAuthStore() {
  return { state, login, logout, setCurrentParkId, isAdmin, isLoggedIn, canEdit }
}
