import { computed, reactive, ref } from 'vue'
import {
  createQuickCategory,
  createQuickStyle,
  deleteQuickCategory,
  deleteQuickStyle,
  getMe,
  getQuickCategories,
  getQuickStyles,
  loginAccount,
  registerAccount,
  updateProfile,
} from '../api/http'
import { getCategoryImage, matchImageByName } from '../assets/style-images'

export type StepKey = 'home' | 'photo' | 'cost' | 'result' | 'profile' | 'settings' | 'asset'
export type AssetKind = 'styles' | 'quotes' | 'templates' | 'profit'

export interface FabricItem {
  id: number
  name: string
  price: number
  usage: number
  lossRate?: number
  priceUnit?: string
  usageUnit?: string
}

export interface ProcessItem {
  id: number
  name: string
  fee: number
}

export interface SavedStyle {
  id: number
  ownerId: string
  name: string
  category: string
  image: string
  minPrice: number
  price: number
  cost: number
  profit: number
  fabrics: FabricItem[]
  processes: ProcessItem[]
  accessoryPack: number
  expectedProfit: number
  createdAt: string
  updatedAt: string
}

interface CategoryItem {
  key: string
  ownerId: string
  name: string
  desc: string
}

interface CategoryDefaults {
  name: string
  fabrics: FabricItem[]
  processes: ProcessItem[]
}

// ── Category defaults (system presets) ──
const categoryDefaults: Record<string, CategoryDefaults> = {
  tshirt: {
    name: 'T 恤',
    fabrics: [
      { id: 1, name: '精棉汗布', price: 22, usage: 0.82 },
      { id: 2, name: '罗纹拼料', price: 18, usage: 0.08 },
    ],
    processes: [
      { id: 3, name: '裁剪', fee: 2 },
      { id: 4, name: '车缝', fee: 6.5 },
    ],
  },
  hoodie: {
    name: '卫衣',
    fabrics: [
      { id: 1, name: '卫衣布', price: 32, usage: 1.25 },
      { id: 2, name: '罗纹', price: 24, usage: 0.18 },
      { id: 3, name: '帽绳帽里', price: 12, usage: 0.12 },
    ],
    processes: [
      { id: 4, name: '裁剪', fee: 3 },
      { id: 5, name: '车缝', fee: 14 },
      { id: 6, name: '印花', fee: 5 },
    ],
  },
  pants: {
    name: '裤子',
    fabrics: [
      { id: 1, name: '裤身面料', price: 28, usage: 1.15 },
      { id: 2, name: '袋布', price: 10, usage: 0.2 },
    ],
    processes: [
      { id: 3, name: '裁剪', fee: 3 },
      { id: 4, name: '车缝', fee: 12 },
      { id: 5, name: '洗水', fee: 3 },
    ],
  },
  coat: {
    name: '外套',
    fabrics: [
      { id: 1, name: '外层面料', price: 42, usage: 1.55 },
      { id: 2, name: '里布', price: 12, usage: 1.25 },
      { id: 3, name: '辅料拼布', price: 18, usage: 0.18 },
    ],
    processes: [
      { id: 4, name: '裁剪', fee: 5 },
      { id: 5, name: '车缝', fee: 24 },
      { id: 6, name: '整烫', fee: 3 },
    ],
  },
}

// ── Module-level singleton state ──
const isReady = ref(false)
const isAuthenticated = ref(false)
const authMode = ref<'login' | 'register'>('login')
const authError = ref('')
const saveError = ref('')
const imagePreview = ref('')
const imageFile = ref<File | null>(null)
const customCategoryName = ref('')
const activeAsset = ref<AssetKind>('styles')
const savedStyles = ref<SavedStyle[]>([])
const saveSuccess = ref(false)

let nextId = 20

const authForm = reactive({
  username: '',
  password: '',
  displayName: '',
  shopName: '',
})

const currentUser = reactive({
  id: 'demo-user-001',
  name: '老板',
})

const profile = reactive({
  ownerName: '老板',
  shopName: '锦禾服装报价室',
  location: '广州 · 沙河档口',
  phone: '',
})

const form = reactive({
  styleName: '短袖针织 T',
  category: 'tshirt',
  accessoryPack: 2.2,
  expectedProfit: 7,
  customerPrice: 39,
  fabrics: [
    { id: 1, name: '精棉汗布', price: 22, usage: 0.82 },
    { id: 2, name: '罗纹拼料', price: 18, usage: 0.08 },
  ] as FabricItem[],
  processes: [
    { id: 3, name: '裁剪', fee: 2 },
    { id: 4, name: '车缝', fee: 6.5 },
  ] as ProcessItem[],
})

const categories = ref<CategoryItem[]>([
  { key: 'tshirt', ownerId: 'system', name: 'T 恤', desc: '面料 + 罗纹 + 车缝' },
  { key: 'hoodie', ownerId: 'system', name: '卫衣', desc: '卫衣布 + 罗纹 + 印花' },
  { key: 'pants', ownerId: 'system', name: '裤子', desc: '裤身 + 袋布 + 洗水' },
  { key: 'coat', ownerId: 'system', name: '外套', desc: '外层 + 里布 + 整烫' },
])

// ── Helpers ──
function getListResults(payload: any) {
  return Array.isArray(payload) ? payload : payload?.results || []
}

export function money(value: number) {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: value % 1 === 0 ? 0 : 1,
    maximumFractionDigits: 1,
  })
}

export function roundAmount(value: number) {
  return Math.round(Number(value || 0) * 100) / 100
}

function getImageUrl(item: any): string {
  // New file upload: construct full media URL
  if (item.image) {
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    const base = import.meta.env.VITE_API_BASE_URL || (isLocal ? 'http://127.0.0.1:8000' : window.location.origin)
    return `${base.replace(/\/api\/?$/, '')}${item.image}`
  }
  // Legacy Base64 data
  if (item.image_data) return item.image_data
  return ''
}

function mapApiStyle(item: any): SavedStyle {
  return {
    id: item.id,
    ownerId: String(item.owner_id),
    name: item.name,
    category: item.category,
    image: getImageUrl(item),
    minPrice: Number(item.minimum_price || 0),
    price: Number(item.quote_price || 0),
    cost: Number(item.total_cost || 0),
    profit: Number(item.profit || 0),
    fabrics: item.fabrics || [],
    processes: item.processes || [],
    accessoryPack: Number(item.accessory_pack || 0),
    expectedProfit: Number(item.expected_profit || 0),
    createdAt: item.created_at || '',
    updatedAt: item.updated_at || '',
  }
}

function applyUser(user: any) {
  currentUser.id = String(user.id)
  currentUser.name = user.display_name || user.username || '老板'
  profile.ownerName = user.display_name || user.username || '老板'
  profile.shopName = user.shop_name || '我的服装报价室'
  profile.location = user.shop_location || '广州 · 沙河档口'
  profile.phone = user.phone || ''
}

function cloneItems<T extends { id: number }>(items: T[]) {
  return items.map((item) => ({ ...item, id: nextId++ }))
}

// ── Computed ──
const visibleStyles = computed(() => savedStyles.value.filter((item) => item.ownerId === currentUser.id))
const visibleCategories = computed(() =>
  categories.value.filter((item) => item.ownerId === 'system' || item.ownerId === currentUser.id),
)
const fabricCost = computed(() =>
  form.fabrics.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.usage || 0), 0),
)
const processCost = computed(() => form.processes.reduce((sum, item) => sum + Number(item.fee || 0), 0))
const singleCost = computed(() => fabricCost.value + processCost.value + Number(form.accessoryPack || 0) + 1.6)
const suggestedPrice = computed(() => Math.ceil(singleCost.value + Number(form.expectedProfit || 0)))
const minimumPrice = computed(() => Math.ceil(singleCost.value * 1.18))
const singleProfit = computed(() => suggestedPrice.value - singleCost.value)
const currentCategoryName = computed(
  () => categoryDefaults[form.category]?.name || visibleCategories.value.find((item) => item.key === form.category)?.name || '自定义',
)
const averageProfit = computed(() => {
  if (!visibleStyles.value.length) return 0
  return visibleStyles.value.reduce((sum, item) => sum + item.profit, 0) / visibleStyles.value.length
})

// ── Dashboard metrics（真实数据）──
const now = () => new Date()
const daysAgo = (n: number) => new Date(now().getTime() - n * 86400000)
const thisMonthStart = () => new Date(now().getFullYear(), now().getMonth(), 1)

const recentWeekStyles = computed(() =>
  visibleStyles.value.filter((s) => s.createdAt && new Date(s.createdAt) >= daysAgo(7)),
)
const recentWeekCount = computed(() => recentWeekStyles.value.length)

const quotedCount = computed(() => visibleStyles.value.filter((s) => s.price > 0).length)

const totalFabricCost = computed(() =>
  visibleStyles.value.reduce((sum, s) => {
    const fabricSum = (s.fabrics || []).reduce((fsum, f) => fsum + Number(f.price || 0) * Number(f.usage || 0), 0)
    return sum + fabricSum
  }, 0),
)

const monthlyNewStyles = computed(() =>
  visibleStyles.value.filter((s) => s.createdAt && new Date(s.createdAt) >= thisMonthStart()).length,
)

const assetTitle = computed(() => {
  const titles: Record<AssetKind, string> = {
    styles: '款式档案',
    quotes: '报价记录',
    templates: '成本模板',
    profit: '利润分析',
  }
  return titles[activeAsset.value]
})
const riskText = computed(() => {
  if (Number(form.customerPrice) < minimumPrice.value) {
    return `客户压到 ¥${form.customerPrice}，低于安全价，建议重谈加工费或减少赠品。`
  }
  return `低于 ¥${minimumPrice.value} 接单风险高，容易被返工、辅料和压价吃掉利润。`
})

// ── Auth actions ──
async function loadDatabaseData() {
  const [user, categoryPayload, stylePayload] = await Promise.all([getMe(), getQuickCategories(), getQuickStyles()])
  applyUser(user)
  const systemCategories = categories.value.filter((item) => item.ownerId === 'system')
  const apiCategories = getListResults(categoryPayload).map((item: any) => ({
    key: item.key,
    ownerId: String(item.owner_id),
    name: item.name,
    desc: item.description || '自定义成本模板',
  }))
  categories.value = [...systemCategories, ...apiCategories]
  savedStyles.value = getListResults(stylePayload).map(mapApiStyle)
}

async function submitAuth() {
  authError.value = ''
  try {
    const payload =
      authMode.value === 'register'
        ? await registerAccount({
            username: authForm.username,
            password: authForm.password,
            display_name: authForm.displayName || authForm.username,
            shop_name: authForm.shopName || '我的服装报价室',
            shop_location: '广州 · 沙河档口',
          })
        : await loginAccount({ username: authForm.username, password: authForm.password })
    localStorage.setItem('garment_token', payload.token)
    isAuthenticated.value = true
    applyUser(payload.user)
    await loadDatabaseData()
  } catch (error: any) {
    authError.value = error?.response?.data?.detail || error?.response?.data?.non_field_errors?.[0] || '账号或密码不正确'
  }
}

function logout() {
  localStorage.removeItem('garment_token')
  isAuthenticated.value = false
  savedStyles.value = []
  imagePreview.value = ''
  imageFile.value = null
}

async function saveProfile() {
  const user = await updateProfile({
    display_name: profile.ownerName,
    shop_name: profile.shopName,
    shop_location: profile.location,
    phone: profile.phone,
  })
  applyUser(user)
}

// ── Category / costing actions ──
function selectCategory(key: string, displayName?: string) {
  const defaults = categoryDefaults[key] || {
    name: key,
    fabrics: [{ id: 1, name: '主面料', price: 0, usage: 0 }],
    processes: [{ id: 2, name: '车缝', fee: 0 }],
  }
  form.category = key
  form.fabrics = cloneItems(defaults.fabrics)
  form.processes = cloneItems(defaults.processes)
  // 自动匹配款式图片：先按 key 精确匹配，失败则按名称智能匹配
  const byKey = getCategoryImage(key)
  if (byKey !== getCategoryImage('default')) {
    imagePreview.value = byKey
  } else if (displayName) {
    imagePreview.value = matchImageByName(displayName)
  } else {
    imagePreview.value = getCategoryImage('default')
  }
}

async function addCustomCategory() {
  const name = customCategoryName.value.trim()
  if (!name) return
  const key = `custom-${Date.now()}`
  const created = await createQuickCategory({
    key,
    name,
    description: '自定义成本模板',
    fabrics: [{ name: '主面料', price: 0, usage: 0 }],
    processes: [{ name: '车缝', fee: 0 }],
  })
  categories.value.push({
    key: created.key,
    ownerId: String(created.owner_id),
    name: created.name,
    desc: created.description,
  })
  customCategoryName.value = ''
  selectCategory(created.key, created.name)
}

function addFabric() {
  form.fabrics.push({ id: nextId++, name: '新增面料', price: 0, usage: 0 })
}

function removeFabric(id: number) {
  if (form.fabrics.length <= 1) return
  form.fabrics = form.fabrics.filter((item) => item.id !== id)
}

function addProcess() {
  form.processes.push({ id: nextId++, name: '新增工序', fee: 0 })
}

function removeProcess(id: number) {
  if (form.processes.length <= 1) return
  form.processes = form.processes.filter((item) => item.id !== id)
}

// ── Save / copy ──
async function saveCurrentStyle() {
  saveError.value = ''
  saveSuccess.value = false
  const name = form.styleName.trim() || '未命名款式'

  try {
    // Use FormData if there's a file, otherwise JSON
    let saved: any
    if (imageFile.value) {
      const fd = new FormData()
      fd.append('name', name)
      fd.append('category', currentCategoryName.value)
      fd.append('image', imageFile.value)
      fd.append('fabrics', JSON.stringify(form.fabrics))
      fd.append('processes', JSON.stringify(form.processes))
      fd.append('accessory_pack', String(roundAmount(form.accessoryPack)))
      fd.append('expected_profit', String(roundAmount(form.expectedProfit)))
      fd.append('minimum_price', String(roundAmount(minimumPrice.value)))
      fd.append('quote_price', String(roundAmount(suggestedPrice.value)))
      fd.append('total_cost', String(roundAmount(singleCost.value)))
      fd.append('profit', String(roundAmount(singleProfit.value)))
      saved = await createQuickStyle(fd)
    } else {
      saved = await createQuickStyle({
        name,
        category: currentCategoryName.value,
        image_data: imagePreview.value,
        fabrics: form.fabrics,
        processes: form.processes,
        accessory_pack: roundAmount(form.accessoryPack),
        expected_profit: roundAmount(form.expectedProfit),
        minimum_price: roundAmount(minimumPrice.value),
        quote_price: roundAmount(suggestedPrice.value),
        total_cost: roundAmount(singleCost.value),
        profit: roundAmount(singleProfit.value),
      })
    }

    const item = mapApiStyle(saved)
    savedStyles.value = [
      item,
      ...savedStyles.value.filter((style) => !(style.ownerId === currentUser.id && style.name === name)),
    ]
    saveSuccess.value = true
  } catch (error: any) {
    saveError.value = error?.response?.data ? JSON.stringify(error.response.data) : '保存失败，请检查登录状态后再试'
  }
}

async function saveAiStyle(costDraft: any, calculation: any) {
  saveError.value = ''
  saveSuccess.value = false
  const name = String(costDraft?.styleName || 'AI算价款式').trim()
  try {
    const fabrics = (costDraft?.fabrics || []).map((item: any, index: number) => ({
      id: index + 1,
      name: item.name || '主面料',
      price: roundAmount(item.price),
      usage: roundAmount(item.usage),
      priceUnit: item.priceUnit || 'kg',
      usageUnit: item.usageUnit || 'kg',
      lossRate: Number(item.lossRate ?? 0.05),
    }))
    const processes = (costDraft?.processes || []).map((item: any, index: number) => ({
      id: index + 100,
      name: item.name || '加工',
      fee: roundAmount(item.fee),
    }))
    const saved = await createQuickStyle({
      name,
      category: costDraft?.category || 'AI算价',
      image_data: '',
      fabrics,
      processes,
      accessory_pack: roundAmount(costDraft?.accessoryPack ?? calculation?.accessoryCost ?? 2.2),
      expected_profit: roundAmount(costDraft?.expectedProfit ?? calculation?.singleProfit ?? 0),
      minimum_price: roundAmount(calculation?.minimumPrice ?? 0),
      quote_price: roundAmount(calculation?.suggestedPrice ?? 0),
      total_cost: roundAmount(calculation?.singleCost ?? 0),
      profit: roundAmount(calculation?.singleProfit ?? 0),
    })
    const item = mapApiStyle(saved)
    savedStyles.value = [
      item,
      ...savedStyles.value.filter((style) => !(style.ownerId === currentUser.id && style.name === name)),
    ]
    saveSuccess.value = true
    return item
  } catch (error: any) {
    saveError.value = error?.response?.data ? JSON.stringify(error.response.data) : '保存失败，请检查登录状态后再试'
    return null
  }
}

function copySavedStyle(style: SavedStyle) {
  form.styleName = `${style.name} 复制款`
  form.category = style.category
  form.fabrics = cloneItems(style.fabrics)
  form.processes = cloneItems(style.processes)
  form.accessoryPack = style.accessoryPack
  form.expectedProfit = style.expectedProfit
  form.customerPrice = style.price
  imagePreview.value = style.image
  imageFile.value = null
}

async function removeStyle(styleId: number) {
  await deleteQuickStyle(styleId)
  savedStyles.value = savedStyles.value.filter((s) => s.id !== styleId)
}

async function removeCategory(key: string) {
  await deleteQuickCategory(key)
  categories.value = categories.value.filter((c) => c.key !== key)
}

// ── Image handling ──
function handleImageChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = () => {
    imagePreview.value = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

function triggerFileInput(id: string) {
  document.getElementById(id)?.click()
}

// ── Init ──
async function initAuth() {
  const token = localStorage.getItem('garment_token')
  if (!token) {
    isReady.value = true
    return
  }
  try {
    isAuthenticated.value = true
    await loadDatabaseData()
  } catch {
    localStorage.removeItem('garment_token')
    isAuthenticated.value = false
  } finally {
    isReady.value = true
  }
}

function resetAuthForm() {
  authForm.username = ''
  authForm.password = ''
  authForm.displayName = ''
  authForm.shopName = ''
  authError.value = ''
}

// ── Export ──
export function useStore() {
  return {
    // State
    isReady,
    isAuthenticated,
    authMode,
    authError,
    saveError,
    saveSuccess,
    imagePreview,
    imageFile,
    customCategoryName,
    activeAsset,
    savedStyles,
    authForm,
    currentUser,
    profile,
    form,
    categories,
    // Computed
    visibleStyles,
    visibleCategories,
    fabricCost,
    processCost,
    singleCost,
    suggestedPrice,
    minimumPrice,
    singleProfit,
    currentCategoryName,
    averageProfit,
    recentWeekCount,
    quotedCount,
    totalFabricCost,
    monthlyNewStyles,
    assetTitle,
    riskText,
    categoryDefaults,
    // Methods
    initAuth,
    submitAuth,
    logout,
    saveProfile,
    loadDatabaseData,
    selectCategory,
    addCustomCategory,
    addFabric,
    removeFabric,
    addProcess,
    removeProcess,
    saveCurrentStyle,
    saveAiStyle,
    copySavedStyle,
    removeStyle,
    removeCategory,
    handleImageChange,
    triggerFileInput,
    resetAuthForm,
  }
}
