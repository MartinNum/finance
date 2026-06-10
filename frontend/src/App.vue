<template>
  <div v-if="!authStore.isLoggedIn()" style="height: 100vh">
    <router-view />
  </div>
  <el-container v-else style="height: 100vh">
    <el-aside width="200px" style="background-color: #304156">
      <div style="padding: 20px; color: #fff; font-size: 18px; font-weight: bold; text-align: center">
        记账系统
      </div>

      <!-- Park selector for admin -->
      <div v-if="authStore.isAdmin()" style="padding: 0 10px 10px">
        <el-select
          v-model="selectedParkId"
          size="small"
          style="width: 100%"
          placeholder="选择园区"
          @change="onParkChange"
        >
          <el-option
            v-for="p in parks"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
      </div>
      <div v-else style="padding: 0 10px 10px; color: #bfcbd9; font-size: 12px; text-align: center">
        {{ authStore.state.user?.park_name }}
      </div>

      <!-- Cycle selector -->
      <div style="padding: 0 10px 15px">
        <el-select
          v-model="cycleStore.state.currentCycleId"
          size="small"
          style="width: 100%"
          placeholder="选择周期"
          @change="onCycleChange"
        >
          <el-option
            v-for="c in cycleStore.state.cycles"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-sub-menu index="costs">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>成本管理</span>
          </template>
          <el-menu-item index="/wage">工资录入</el-menu-item>
          <el-menu-item index="/expense">支出录入</el-menu-item>
          <el-menu-item index="/grape-cost">葡萄成本</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="finance">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>财务</span>
          </template>
          <el-menu-item index="/income">收入录入</el-menu-item>
          <el-menu-item index="/investment">投资管理</el-menu-item>
          <el-menu-item index="/dividend">分账管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/report">
          <el-icon><TrendCharts /></el-icon>
          <span>报表面板</span>
        </el-menu-item>
        <el-sub-menu index="settings">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/cycle">周期管理</el-menu-item>
          <el-menu-item index="/job-type">工种管理</el-menu-item>
          <el-menu-item index="/expense-category">支出分类管理</el-menu-item>
          <el-menu-item index="/grape-grade">葡萄等级</el-menu-item>
          <el-menu-item v-if="authStore.isAdmin()" index="/admin/parks">园区管理</el-menu-item>
          <el-menu-item v-if="authStore.isAdmin()" index="/admin/users">用户管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; display: flex; align-items: center; justify-content: flex-end; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 0 20px; height: 50px">
        <span style="margin-right: 15px; color: #606266; font-size: 14px">
          {{ authStore.state.user?.display_name }}
        </span>
        <el-button size="small" @click="handleLogout">退出</el-button>
      </el-header>
      <el-main style="padding: 20px; background-color: #f0f2f5">
        <router-view :key="cycleStore.state.currentCycleId" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCycleStore } from './store/cycle.js'
import { useAuthStore } from './store/auth.js'
import { adminApi } from './api'

const router = useRouter()
const cycleStore = useCycleStore()
const authStore = useAuthStore()

const parks = ref([])
const selectedParkId = ref(authStore.state.currentParkId)

const loadParks = async () => {
  try {
    const res = await adminApi.listParks()
    parks.value = res.data.filter(p => p.is_active)
    if (!selectedParkId.value && parks.value.length > 0) {
      selectedParkId.value = parks.value[0].id
      authStore.setCurrentParkId(selectedParkId.value)
    }
  } catch (e) {
    // not admin or not logged in
  }
}

const onParkChange = (parkId) => {
  authStore.setCurrentParkId(parkId)
  cycleStore.state.currentCycleId = null
  cycleStore.loadCycles()
}

const onCycleChange = () => {
  // router-view key change triggers re-render
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (authStore.isLoggedIn()) {
    if (authStore.isAdmin()) {
      await loadParks()
    }
    cycleStore.loadCycles()
  }
})

watch(() => authStore.state.token, async (newVal) => {
  if (newVal) {
    if (authStore.isAdmin()) {
      await loadParks()
    }
    cycleStore.loadCycles()
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.el-menu {
  border-right: none;
}
</style>
