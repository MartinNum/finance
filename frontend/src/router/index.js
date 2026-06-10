import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import Dashboard from '../views/Dashboard.vue'
import Wage from '../views/Wage.vue'
import Expense from '../views/Expense.vue'
import JobType from '../views/JobType.vue'
import ExpenseCategory from '../views/ExpenseCategory.vue'
import Investment from '../views/Investment.vue'
import Cycle from '../views/Cycle.vue'
import Report from '../views/Report.vue'
import GrapeCost from '../views/GrapeCost.vue'
import GrapeGrade from '../views/GrapeGrade.vue'
import Income from '../views/Income.vue'
import Dividend from '../views/Dividend.vue'
import Login from '../views/Login.vue'
import ParkManage from '../views/admin/ParkManage.vue'
import UserManage from '../views/admin/UserManage.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/wage', name: 'Wage', component: Wage },
  { path: '/expense', name: 'Expense', component: Expense },
  { path: '/income', name: 'Income', component: Income },
  { path: '/investment', name: 'Investment', component: Investment },
  { path: '/dividend', name: 'Dividend', component: Dividend },
  { path: '/cycle', name: 'Cycle', component: Cycle },
  { path: '/job-type', name: 'JobType', component: JobType },
  { path: '/expense-category', name: 'ExpenseCategory', component: ExpenseCategory },
  { path: '/grape-grade', name: 'GrapeGrade', component: GrapeGrade },
  { path: '/report', name: 'Report', component: Report },
  { path: '/grape-cost', name: 'GrapeCost', component: GrapeCost },
  { path: '/admin/parks', name: 'ParkManage', component: ParkManage, meta: { admin: true } },
  { path: '/admin/users', name: 'UserManage', component: UserManage, meta: { admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const { isLoggedIn, isAdmin } = useAuthStore()
  if (to.meta.public) {
    next()
  } else if (!isLoggedIn()) {
    next('/login')
  } else if (to.meta.admin && !isAdmin()) {
    next('/')
  } else {
    next()
  }
})

export default router
