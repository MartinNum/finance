import { reactive } from 'vue'
import { cycleApi } from '../api'

const state = reactive({
  cycles: [],
  currentCycleId: null
})

const loadCycles = async () => {
  const res = await cycleApi.list()
  state.cycles = res.data
  const current = res.data.find(c => c.is_current)
  if (current && !state.currentCycleId) {
    state.currentCycleId = current.id
  }
}

const setCurrentCycle = (id) => {
  state.currentCycleId = id
}

export function useCycleStore() {
  return {
    state,
    loadCycles,
    setCurrentCycle
  }
}
