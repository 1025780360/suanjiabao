import { createRouter, createWebHistory } from 'vue-router'

function isStandaloneApp() {
  const nav = window.navigator as Navigator & { standalone?: boolean }
  const isCapacitorHost = window.location.protocol === 'capacitor:' || window.location.origin === 'https://localhost'
  return isCapacitorHost || window.matchMedia('(display-mode: standalone)').matches || nav.standalone === true
}

function getAppEntryPath() {
  const token = localStorage.getItem('garment_token')
  return token ? '/home' : '/login'
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: () => {
        return isStandaloneApp() ? getAppEntryPath() : '/official'
      },
    },
    {
      path: '/official',
      name: 'official',
      component: () => import('../views/OfficialSiteView.vue'),
      meta: { publicSite: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/photo',
      name: 'photo',
      component: () => import('../views/PhotoView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/cost',
      name: 'cost',
      component: () => import('../views/CostView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/ai-costing',
      name: 'ai-costing',
      component: () => import('../views/AiCostingView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('../views/ResultView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/asset/:kind',
      name: 'asset',
      component: () => import('../views/AssetView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/membership',
      name: 'membership',
      component: () => import('../views/MembershipView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/pay',
      name: 'pay',
      component: () => import('../views/PayView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/support/login',
      name: 'cs-login',
      component: () => import('../views/CsLoginView.vue'),
    },
    {
      path: '/support',
      name: 'support',
      component: () => import('../views/SupportDashboard.vue'),
      meta: { requiresStaff: true },
    },
  ],
})

router.beforeEach((to, _from) => {
  if (to.meta.publicSite && isStandaloneApp()) {
    return getAppEntryPath()
  }

  // 客服后台：需要 staff 权限
  if (to.meta.requiresStaff) {
    const token = localStorage.getItem('garment_token')
    if (!token) {
      return { name: 'cs-login' }
    }
    // 简单判断：有 token 先放行，页面内会二次校验
    return
  }

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('garment_token')
    if (!token) {
      return { name: 'login' }
    }
  }
  // Don't let authenticated users see login
  if (to.name === 'login') {
    const token = localStorage.getItem('garment_token')
    if (token) {
      return { name: 'home' }
    }
  }
})

export default router
