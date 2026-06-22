<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  CameraFilled,
  Check,
  Close,
  CopyDocument,
  Delete,
  Setting,
  House,
  Money,
  PictureFilled,
  Plus,
  Share,
  User,
  WarningFilled,
} from '@element-plus/icons-vue'
import {
  createQuickCategory,
  createQuickStyle,
  getMe,
  getQuickCategories,
  getQuickStyles,
  loginAccount,
  registerAccount,
  updateProfile,
} from '../api/http'

type StepKey = 'home' | 'photo' | 'cost' | 'result' | 'profile' | 'settings' | 'asset'
type AssetKind = 'styles' | 'quotes' | 'templates' | 'profit'

interface FabricItem {
  id: number
  name: string
  price: number
  usage: number
}

interface ProcessItem {
  id: number
  name: string
  fee: number
}

interface SavedStyle {
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
}

const activeStep = ref<StepKey>('home')
const activeAsset = ref<AssetKind>('styles')
const imagePreview = ref('')
const customCategoryName = ref('')
const savedStyles = ref<SavedStyle[]>([])
const isReady = ref(false)
const isAuthenticated = ref(false)
const authMode = ref<'login' | 'register'>('login')
const authError = ref('')
const saveError = ref('')
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
let nextId = 20

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

const categoryDefaults: Record<string, { name: string; fabrics: FabricItem[]; processes: ProcessItem[] }> = {
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

const categories = ref([
  { key: 'tshirt', ownerId: 'system', name: 'T 恤', desc: '面料 + 罗纹 + 车缝' },
  { key: 'hoodie', ownerId: 'system', name: '卫衣', desc: '卫衣布 + 罗纹 + 印花' },
  { key: 'pants', ownerId: 'system', name: '裤子', desc: '裤身 + 袋布 + 洗水' },
  { key: 'coat', ownerId: 'system', name: '外套', desc: '外层 + 里布 + 整烫' },
])

function getListResults(payload: any) {
  return Array.isArray(payload) ? payload : payload?.results || []
}

function mapApiStyle(item: any): SavedStyle {
  return {
    id: item.id,
    ownerId: String(item.owner_id),
    name: item.name,
    category: item.category,
    image: item.image_data || '',
    minPrice: Number(item.minimum_price || 0),
    price: Number(item.quote_price || 0),
    cost: Number(item.total_cost || 0),
    profit: Number(item.profit || 0),
    fabrics: item.fabrics || [],
    processes: item.processes || [],
    accessoryPack: Number(item.accessory_pack || 0),
    expectedProfit: Number(item.expected_profit || 0),
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
  activeStep.value = 'home'
}

async function saveProfile() {
  const user = await updateProfile({
    display_name: profile.ownerName,
    shop_name: profile.shopName,
    shop_location: profile.location,
    phone: profile.phone,
  })
  applyUser(user)
  activeStep.value = 'profile'
}

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

function money(value: number) {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: value % 1 === 0 ? 0 : 1,
    maximumFractionDigits: 1,
  })
}

function roundAmount(value: number) {
  return Math.round(Number(value || 0) * 100) / 100
}

function cloneItems<T extends { id: number }>(items: T[]) {
  return items.map((item) => ({ ...item, id: nextId++ }))
}

function setStep(step: StepKey) {
  activeStep.value = step
}

function openAsset(kind: AssetKind) {
  activeAsset.value = kind
  activeStep.value = 'asset'
}

function selectCategory(key: string) {
  const defaults = categoryDefaults[key] || {
    name: key,
    fabrics: [{ id: 1, name: '主面料', price: 0, usage: 0 }],
    processes: [{ id: 2, name: '车缝', fee: 0 }],
  }
  form.category = key
  form.fabrics = cloneItems(defaults.fabrics)
  form.processes = cloneItems(defaults.processes)
  activeStep.value = 'cost'
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
  categories.value.push({ key: created.key, ownerId: String(created.owner_id), name: created.name, desc: created.description })
  customCategoryName.value = ''
  selectCategory(created.key)
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

async function saveCurrentStyle() {
  saveError.value = ''
  const name = form.styleName.trim() || '未命名款式'
  try {
    const saved = await createQuickStyle({
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
    const item = mapApiStyle(saved)
    savedStyles.value = [
      item,
      ...savedStyles.value.filter((style) => !(style.ownerId === currentUser.id && style.name === name)),
    ]
    activeStep.value = 'home'
  } catch (error: any) {
    saveError.value = error?.response?.data ? JSON.stringify(error.response.data) : '保存失败，请检查登录状态后再试'
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
  activeStep.value = 'cost'
}

function handleImageChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    imagePreview.value = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

function triggerFileInput(id: string) {
  document.getElementById(id)?.click()
}

onMounted(async () => {
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
})
</script>

<template>
  <main class="mobile-showcase">
    <section v-if="!isReady" class="auth-panel">
      <h1>正在打开档口系统</h1>
      <p>请稍等，正在检查登录状态。</p>
    </section>

    <section v-else-if="!isAuthenticated" class="auth-panel">
      <div class="eyebrow">
        <span></span>
        ACCOUNT LOGIN
      </div>
      <h1>{{ authMode === 'login' ? '登录账号' : '注册账号' }}</h1>
      <p>账号、款式、报价和个人资料都会保存到数据库，换版本也不会丢。</p>

      <div class="auth-card">
        <label>
          账号
          <input v-model="authForm.username" autocomplete="username" placeholder="请输入账号" />
        </label>
        <label>
          密码
          <input v-model="authForm.password" autocomplete="current-password" type="password" placeholder="至少 6 位" />
        </label>
        <template v-if="authMode === 'register'">
          <label>
            你的称呼
            <input v-model="authForm.displayName" placeholder="例如：张老板" />
          </label>
          <label>
            店铺名称
            <input v-model="authForm.shopName" placeholder="例如：锦禾服装报价室" />
          </label>
        </template>
        <div v-if="authError" class="auth-error">{{ authError }}</div>
        <button type="button" @click="submitAuth">{{ authMode === 'login' ? '登录' : '注册并进入' }}</button>
        <button class="ghost-btn" type="button" @click="authMode = authMode === 'login' ? 'register' : 'login'">
          {{ authMode === 'login' ? '没有账号？去注册' : '已有账号？去登录' }}
        </button>
      </div>
    </section>

    <section v-else class="desktop-copy">
      <div class="eyebrow">
        <span></span>
        GUANGZHOU FASHION COSTING APP
      </div>
      <h1>把档口老板的手算经验，做成高级报价系统</h1>
      <p>
        拍个款、填几个数，系统自动算出成本、最低安全价和利润空间。前台像计算器一样简单，后台自动沉淀款式和报价记录。
      </p>
      <div class="promise">
        <b>核心体验</b>
        <span>不用 Excel，不用先建复杂资料库。每一次算价，都会自然变成款式档案、成本档案和报价记录。</span>
      </div>
    </section>

    <section v-if="isAuthenticated" class="phone" aria-label="手机端成本报价系统预览">
      <div class="screen">
        <div class="notch"></div>

        <div class="app-view">
          <section v-if="activeStep === 'home'" class="page">
            <header class="nav">
              <div>
                <span class="hello">你好，{{ profile.ownerName || '老板' }}</span>
                <h2>今天先算哪款？</h2>
              </div>
              <button class="icon-btn" type="button" @click="setStep('photo')">
                <el-icon><Plus /></el-icon>
              </button>
            </header>

            <article class="hero-card">
              <span>已保存款式</span>
              <strong>{{ visibleStyles.length }} 款</strong>
              <p>点开历史款式，可以复制旧款直接改价。</p>
            </article>

            <div class="quick-actions">
              <button class="action-card primary" type="button" @click="setStep('photo')">
                <b>快速算价</b>
                <span>拍款式图，输入关键成本</span>
              </button>
              <button class="action-card" type="button" @click="visibleStyles[0] ? copySavedStyle(visibleStyles[0]) : setStep('photo')">
                <b>复制旧款</b>
                <span>{{ visibleStyles.length ? '相似款直接改几个数' : '先保存一个款式' }}</span>
              </button>
            </div>

            <div class="section-head">
              <b>最近款式</b>
              <span>{{ visibleStyles.length }} 款</span>
            </div>

            <div v-if="visibleStyles.length" class="style-list">
              <article v-for="item in visibleStyles" :key="item.id" class="style-item" @click="copySavedStyle(item)">
                <div class="thumb">
                  <img v-if="item.image" :src="item.image" alt="款式图片" />
                </div>
                <div>
                  <b>{{ item.name }}</b>
                  <span>{{ item.category }} · 最低接单价 ¥{{ item.minPrice }}</span>
                </div>
                <strong>赚 ¥{{ money(item.profit) }}</strong>
              </article>
            </div>
            <div v-else class="empty-state">
              <b>暂无款式</b>
              <span>算完报价后点“保存款式”，这里就会出现记录。</span>
            </div>
          </section>

          <section v-else-if="activeStep === 'photo'" class="page">
            <header class="nav">
              <div>
                <span class="hello">步骤 1/3</span>
                <h2>拍照建款</h2>
              </div>
              <button class="icon-btn" type="button" @click="setStep('home')">
                <el-icon><Close /></el-icon>
              </button>
            </header>

            <div class="camera-area">
              <input id="camera-input" type="file" accept="image/*" capture="environment" @change="handleImageChange" />
              <input id="album-input" type="file" accept="image/*" @change="handleImageChange" />
              <img v-if="imagePreview" :src="imagePreview" alt="款式图片" />
              <template v-else>
                <div class="scan-frame"></div>
                <div class="mock-shirt"></div>
              </template>
              <div class="scan-copy">
                <div>
                  <b>对准衣服拍一张</b>
                  <span>款式图会自动保存到报价记录</span>
                </div>
                <button class="shutter" type="button" @click="triggerFileInput('camera-input')">
                  <el-icon><CameraFilled /></el-icon>
                </button>
              </div>
            </div>

            <div class="photo-actions">
              <button type="button" @click="triggerFileInput('camera-input')">
                <el-icon><CameraFilled /></el-icon>
                现在拍照
              </button>
              <button type="button" @click="triggerFileInput('album-input')">
                <el-icon><PictureFilled /></el-icon>
                从相册选
              </button>
            </div>

            <div class="section-head">
              <b>选择品类</b>
              <span>系统带出默认成本项</span>
            </div>

            <div class="category-grid">
              <button v-for="item in visibleCategories" :key="item.key" type="button" @click="selectCategory(item.key)">
                <b>{{ item.name }}</b>
                <span>{{ item.desc }}</span>
              </button>
            </div>

            <div class="custom-category">
              <input v-model="customCategoryName" placeholder="没有合适品类，自己填一个" />
              <button type="button" @click="addCustomCategory">创建</button>
            </div>
          </section>

          <section v-else-if="activeStep === 'cost'" class="page">
            <header class="nav">
              <div>
                <span class="hello">步骤 2/3 · {{ currentCategoryName }}</span>
                <h2>只填关键数字</h2>
              </div>
              <button class="icon-btn" type="button" @click="setStep('result')">
                <el-icon><Check /></el-icon>
              </button>
            </header>

            <label class="style-name-field">
              <span>款式名称</span>
              <input v-model="form.styleName" placeholder="例如：短袖针织 T" />
            </label>

            <div class="input-help">不会填的先用默认值。系统会帮你把面料、加工、辅料、利润合起来算。</div>

            <div class="cost-sheet">
              <div class="sheet-title">
                <div>
                  <b>面料</b>
                  <span>支持多种面料一起计算</span>
                </div>
                <button type="button" @click="addFabric">
                  <el-icon><Plus /></el-icon>
                  加面料
                </button>
              </div>

              <article v-for="item in form.fabrics" :key="item.id" class="line-card">
                <input v-model="item.name" class="name-input" aria-label="面料名称" placeholder="面料名称" />
                <div class="line-grid">
                  <label>
                    <small>单价</small>
                    <em>¥<input v-model.number="item.price" type="number" inputmode="decimal" placeholder="0" /></em>
                  </label>
                  <label>
                    <small>用量</small>
                    <em><input v-model.number="item.usage" type="number" inputmode="decimal" placeholder="0" />m</em>
                  </label>
                  <button type="button" class="delete-btn" @click="removeFabric(item.id)">
                    <el-icon><Delete /></el-icon>
                  </button>
                </div>
              </article>
            </div>

            <div class="cost-sheet">
              <div class="sheet-title">
                <div>
                  <b>加工工序</b>
                  <span>裁剪、车缝、印花都能加</span>
                </div>
                <button type="button" @click="addProcess">
                  <el-icon><Plus /></el-icon>
                  加工序
                </button>
              </div>

              <article v-for="item in form.processes" :key="item.id" class="line-card compact">
                <input v-model="item.name" class="name-input" aria-label="工序名称" placeholder="工序名称" />
                <div class="line-grid process-grid">
                  <label>
                    <small>费用</small>
                    <em>¥<input v-model.number="item.fee" type="number" inputmode="decimal" placeholder="0" /></em>
                  </label>
                  <button type="button" class="delete-btn" @click="removeProcess(item.id)">
                    <el-icon><Delete /></el-icon>
                  </button>
                </div>
              </article>

              <label class="input-row">
                <span>
                  <small>辅料包装</small>
                  <b>吊牌 / 胶袋 / 主唛</b>
                </span>
                <em>¥<input v-model.number="form.accessoryPack" type="number" inputmode="decimal" placeholder="0" /></em>
              </label>
              <label class="input-row">
                <span>
                  <small>想赚利润</small>
                  <b>按单件利润</b>
                </span>
                <em>¥<input v-model.number="form.expectedProfit" type="number" inputmode="decimal" placeholder="0" /></em>
              </label>

              <button class="calc-button" type="button" @click="setStep('result')">马上算报价</button>
            </div>
          </section>

          <section v-else class="page">
            <template v-if="activeStep === 'result'">
            <header class="nav">
              <div>
                <span class="hello">步骤 3/3 · 报价结果</span>
                <h2>这单能不能接？</h2>
              </div>
              <button class="icon-btn" type="button" @click="setStep('home')">
                <el-icon><Share /></el-icon>
              </button>
            </header>

            <article class="result-hero">
              <span>建议批发价</span>
              <strong>¥{{ suggestedPrice }}</strong>
              <p>低于 ¥{{ minimumPrice }} 接单风险高，容易被返工、辅料和压价吃掉利润。</p>
            </article>

            <div class="metric-grid">
              <article>
                <span>面料合计</span>
                <b>¥{{ money(fabricCost) }}</b>
              </article>
              <article>
                <span>加工合计</span>
                <b>¥{{ money(processCost) }}</b>
              </article>
              <article>
                <span>单件成本</span>
                <b>¥{{ money(singleCost) }}</b>
              </article>
              <article>
                <span>单件利润</span>
                <b>¥{{ money(singleProfit) }}</b>
              </article>
            </div>

            <div class="profit-strip">
              <div>
                <span>100 件赚</span>
                <b>¥{{ money(singleProfit * 100) }}</b>
              </div>
              <div>
                <span>500 件赚</span>
                <b>¥{{ money(singleProfit * 500) }}</b>
              </div>
            </div>

            <div class="risk">
              <el-icon><WarningFilled /></el-icon>
              <span><b>安全价提醒：</b>{{ riskText }}</span>
            </div>

            <div v-if="saveError" class="auth-error">{{ saveError }}</div>

            <div class="result-actions">
              <button type="button" @click="setStep('cost')">
                <el-icon><CopyDocument /></el-icon>
                复制改价
              </button>
              <button type="button" @click="saveCurrentStyle">
                <el-icon><Share /></el-icon>
                保存款式
              </button>
            </div>
            </template>

            <template v-else-if="activeStep === 'profile'">
              <header class="nav profile-nav">
                <div>
                  <span class="hello">店铺中心</span>
                  <h2>我的档口</h2>
                </div>
                <button class="icon-btn" type="button" @click="setStep('settings')">
                  <el-icon><Setting /></el-icon>
                </button>
              </header>

              <article class="profile-card">
                <div class="avatar-mark">{{ profile.shopName.slice(0, 1) || '档' }}</div>
                <div>
                  <span>{{ profile.location }}</span>
                  <strong>{{ profile.shopName }}</strong>
                  <p>当前已保存 {{ visibleStyles.length }} 个款式，建议先把爆款都沉淀成模板。</p>
                </div>
              </article>

              <div class="profile-stats">
                <article>
                  <span>已保存</span>
                  <b>{{ visibleStyles.length }}</b>
                  <small>款式</small>
                </article>
                <article>
                  <span>平均利润</span>
                  <b>¥{{ money(averageProfit) }}</b>
                  <small>单件</small>
                </article>
              </div>

              <section class="profile-panel">
                <div class="panel-title">
                  <b>资产管理</b>
                  <span>每一次报价都会变成你的经验库</span>
                </div>
                <div class="asset-grid">
                  <button type="button" @click="openAsset('styles')">款式档案</button>
                  <button type="button" @click="openAsset('quotes')">报价记录</button>
                  <button type="button" @click="openAsset('templates')">成本模板</button>
                  <button type="button" @click="openAsset('profit')">利润分析</button>
                </div>
              </section>
            </template>

            <template v-else-if="activeStep === 'settings'">
              <header class="nav profile-nav">
                <div>
                  <span class="hello">个人资料</span>
                  <h2>设置</h2>
                </div>
                <button class="icon-btn" type="button" @click="saveProfile">
                  <el-icon><Check /></el-icon>
                </button>
              </header>

              <section class="profile-panel">
                <div class="panel-title">
                  <b>档口资料</b>
                  <span>这些信息会显示在我的页面和报价资料里</span>
                </div>
                <label class="profile-field">
                  <span>你的称呼</span>
                  <input v-model="profile.ownerName" placeholder="例如：张老板" />
                </label>
                <label class="profile-field">
                  <span>店铺名称</span>
                  <input v-model="profile.shopName" placeholder="例如：锦禾服装报价室" />
                </label>
                <label class="profile-field">
                  <span>所在位置</span>
                  <input v-model="profile.location" placeholder="例如：广州 · 沙河档口" />
                </label>
                <label class="profile-field">
                  <span>联系电话</span>
                  <input v-model="profile.phone" inputmode="tel" placeholder="可不填" />
                </label>
                <button class="logout-btn" type="button" @click="logout">退出当前账号</button>
              </section>
            </template>

            <template v-else>
              <header class="nav profile-nav">
                <div>
                  <span class="hello">资产管理</span>
                  <h2>{{ assetTitle }}</h2>
                </div>
                <button class="icon-btn" type="button" @click="setStep('profile')">
                  <el-icon><Close /></el-icon>
                </button>
              </header>

              <section class="profile-panel asset-page">
                <template v-if="activeAsset === 'styles'">
                  <article v-for="item in visibleStyles" :key="item.id" class="asset-row">
                    <div class="thumb"><img v-if="item.image" :src="item.image" alt="款式图片" /></div>
                    <span>
                      <b>{{ item.name }}</b>
                      <small>{{ item.category }} · 成本 ¥{{ money(item.cost) }}</small>
                    </span>
                    <strong>¥{{ item.price }}</strong>
                  </article>
                  <div v-if="!visibleStyles.length" class="empty-state">暂无款式，先去建款保存。</div>
                </template>

                <template v-else-if="activeAsset === 'quotes'">
                  <article v-for="item in visibleStyles" :key="item.id" class="asset-row">
                    <span>
                      <b>{{ item.name }}</b>
                      <small>最低接单价 ¥{{ item.minPrice }}</small>
                    </span>
                    <strong>报价 ¥{{ item.price }}</strong>
                  </article>
                  <div v-if="!visibleStyles.length" class="empty-state">暂无报价记录。</div>
                </template>

                <template v-else-if="activeAsset === 'templates'">
                  <article v-for="item in visibleCategories" :key="item.key" class="asset-row">
                    <span>
                      <b>{{ item.name }}</b>
                      <small>{{ item.desc }}</small>
                    </span>
                    <strong>模板</strong>
                  </article>
                </template>

                <template v-else>
                  <article class="asset-row">
                    <span>
                      <b>平均单件利润</b>
                      <small>来自已保存款式</small>
                    </span>
                    <strong>¥{{ money(averageProfit) }}</strong>
                  </article>
                  <article class="asset-row">
                    <span>
                      <b>最高建议价</b>
                      <small>已保存款式中最高报价</small>
                    </span>
                    <strong>¥{{ money(Math.max(0, ...visibleStyles.map((item) => item.price))) }}</strong>
                  </article>
                </template>
              </section>
            </template>
          </section>
        </div>

        <nav class="bottom-bar">
          <button :class="{ active: activeStep === 'home' }" type="button" @click="setStep('home')">
            <el-icon><House /></el-icon>
            首页
          </button>
          <button :class="{ active: activeStep === 'photo' }" type="button" @click="setStep('photo')">
            <el-icon><PictureFilled /></el-icon>
            建款
          </button>
          <button :class="{ active: activeStep === 'cost' || activeStep === 'result' }" type="button" @click="setStep('cost')">
            <el-icon><Money /></el-icon>
            报价
          </button>
          <button :class="{ active: activeStep === 'profile' }" type="button" @click="setStep('profile')">
            <el-icon><User /></el-icon>
            我的
          </button>
        </nav>
      </div>
    </section>
  </main>
</template>

<style scoped>
.mobile-showcase {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 64px;
  min-height: 100dvh;
  padding: 56px 72px;
  overflow: hidden;
  color: #fff4dc;
  background:
    radial-gradient(circle at 16% 10%, rgba(215, 171, 88, 0.22), transparent 30%),
    radial-gradient(circle at 78% 24%, rgba(101, 116, 83, 0.24), transparent 26%),
    radial-gradient(circle at 48% 108%, rgba(223, 192, 124, 0.16), transparent 32%),
    linear-gradient(135deg, #070806 0%, #151711 42%, #2a261b 100%);
}

.mobile-showcase::before {
  content: "";
  position: fixed;
  inset: 0;
  background:
    linear-gradient(rgba(235, 206, 145, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(235, 206, 145, 0.045) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
}

.mobile-showcase::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image: radial-gradient(rgba(255, 232, 176, 0.18) 0.6px, transparent 0.6px);
  background-size: 5px 5px;
  opacity: 0.18;
  pointer-events: none;
}

.desktop-copy,
.phone {
  position: relative;
  z-index: 1;
}

.desktop-copy {
  display: grid;
  align-content: center;
  max-width: 760px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  height: 34px;
  padding: 0 14px;
  border: 1px solid rgba(229, 195, 124, 0.36);
  border-radius: 999px;
  color: rgba(247, 237, 215, 0.8);
  background: rgba(255, 244, 220, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  font-size: 14px;
  letter-spacing: 0.08em;
}

.eyebrow span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #e5bd73;
  box-shadow: 0 0 0 5px rgba(229, 189, 115, 0.14), 0 0 24px rgba(229, 189, 115, 0.5);
}

.desktop-copy h1 {
  max-width: 760px;
  margin: 18px 0 18px;
  color: #fff5df;
  font-size: clamp(48px, 7vw, 82px);
  line-height: 0.98;
  letter-spacing: -0.05em;
  text-wrap: balance;
  text-shadow: 0 22px 46px rgba(0, 0, 0, 0.35);
}

.desktop-copy p {
  max-width: 620px;
  margin: 0;
  color: rgba(247, 237, 215, 0.68);
  font-size: 20px;
  line-height: 1.7;
}

.promise {
  width: 360px;
  margin-top: 42px;
  padding: 24px 26px;
  border: 1px solid rgba(229, 195, 124, 0.22);
  border-radius: 26px;
  color: #f8eed8;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.08), transparent 38%),
    linear-gradient(145deg, #10130e, #252719);
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.promise b {
  display: block;
  margin-bottom: 12px;
  color: #fff7e8;
  font-size: 18px;
}

.promise span {
  color: rgba(248, 238, 216, 0.72);
  font-size: 14px;
  line-height: 1.7;
}

.auth-panel {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: center;
  width: min(420px, 100%);
  min-height: calc(100dvh - 112px);
  margin: 0 auto;
}

.auth-panel h1 {
  margin: 18px 0 12px;
  color: #fff5df;
  font-size: 42px;
  line-height: 1;
}

.auth-panel p {
  margin: 0 0 18px;
  color: rgba(247, 237, 215, 0.72);
  line-height: 1.6;
}

.auth-card {
  display: grid;
  gap: 12px;
  padding: 18px;
  border: 1px solid rgba(239, 204, 132, 0.18);
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.32);
}

.auth-card label {
  display: grid;
  gap: 7px;
  color: rgba(23, 21, 18, 0.62);
  font-size: 13px;
  font-weight: 900;
}

.auth-card input {
  height: 48px;
  border: 2px solid #d2b98f;
  border-radius: 16px;
  outline: 0;
  padding: 0 12px;
  background: #fffaf2;
  color: #050505;
  font-size: 15px;
  font-weight: 900;
}

.auth-card button,
.logout-btn {
  min-height: 48px;
  border: 0;
  border-radius: 18px;
  color: #fffaf1;
  background: #1e241e;
  font-weight: 900;
}

.auth-card .ghost-btn {
  color: #171512;
  background: rgba(255, 255, 255, 0.58);
}

.auth-error {
  padding: 10px 12px;
  border-radius: 14px;
  color: #6f1d1b;
  background: #ffe0d8;
  font-size: 13px;
  font-weight: 900;
}

.phone {
  width: 360px;
  height: 732px;
  align-self: center;
  padding: 14px;
  border-radius: 52px;
  background:
    linear-gradient(145deg, #070707 0%, #242116 48%, #6f5527 49%, #11110e 56%, #000 100%);
  box-shadow:
    0 42px 100px rgba(0, 0, 0, 0.48),
    0 0 0 1px rgba(230, 195, 119, 0.18),
    inset 0 0 0 1px rgba(255, 248, 223, 0.16);
}

.screen {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 40px;
  color: #fff3dc;
  background:
    radial-gradient(circle at 80% 0%, rgba(218, 177, 96, 0.18), transparent 30%),
    linear-gradient(180deg, #151811 0%, #0e110d 100%);
  box-shadow: inset 0 0 0 1px rgba(231, 202, 139, 0.16);
}

.notch {
  position: absolute;
  top: 13px;
  left: 50%;
  z-index: 5;
  width: 104px;
  height: 28px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: #080808;
}

.app-view {
  height: calc(100% - 80px);
  overflow: auto;
  padding-top: 48px;
  scrollbar-width: none;
}

.app-view::-webkit-scrollbar {
  display: none;
}

.page {
  padding: 12px 22px 20px;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 20px;
}

.hello {
  color: rgba(255, 243, 220, 0.58);
  font-size: 13px;
}

.nav h2 {
  margin: 3px 0 0;
  color: #fff3dc;
  font-size: 25px;
  line-height: 1.18;
  font-weight: 900;
  letter-spacing: -0.04em;
}

.icon-btn {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 0;
  border-radius: 15px;
  color: #17120a;
  background: linear-gradient(145deg, #ffe4a8, #b88335);
  box-shadow: 0 10px 26px rgba(188, 132, 50, 0.3);
  font-size: 18px;
}

.hero-card,
.result-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(239, 204, 132, 0.18);
  border-radius: 28px;
  color: #fff9ee;
  background:
    radial-gradient(circle at 86% 18%, rgba(231, 185, 88, 0.52), transparent 28%),
    linear-gradient(145deg, #080907 0%, #1b2115 52%, #4b3d1d 100%);
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.hero-card {
  min-height: 172px;
  padding: 22px;
}

.hero-card::after {
  content: "";
  position: absolute;
  right: -12px;
  bottom: -30px;
  width: 132px;
  height: 172px;
  border-radius: 66px 66px 24px 24px;
  background:
    linear-gradient(90deg, transparent 42%, rgba(255, 252, 229, 0.24) 43%, transparent 45%),
    linear-gradient(145deg, #f1d49b, #8a6127);
  opacity: 0.82;
  transform: rotate(-12deg);
}

.hero-card span,
.result-hero span {
  position: relative;
  z-index: 1;
  color: rgba(255, 240, 204, 0.62);
  font-size: 13px;
}

.hero-card strong {
  position: relative;
  z-index: 1;
  display: block;
  margin: 12px 0 6px;
  font-size: 44px;
  line-height: 1;
  font-weight: 900;
}

.hero-card p,
.result-hero p {
  position: relative;
  z-index: 1;
  max-width: 190px;
  margin: 0;
  color: rgba(255, 249, 238, 0.76);
  font-size: 13px;
  line-height: 1.45;
}

.quick-actions,
.metric-grid,
.profit-strip,
.result-actions,
.category-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-actions {
  margin: 16px 0 22px;
}

.action-card,
.style-item,
.category-grid button,
.custom-category,
.empty-state,
.cost-sheet,
.metric-grid article,
.profit-strip div {
  color: #17130c;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.58);
}

.action-card {
  min-height: 88px;
  padding: 14px;
  border: 0;
  border-radius: 22px;
  text-align: left;
}

.action-card.primary {
  color: #17110a;
  background: linear-gradient(145deg, #f6d796, #ba7d2c);
}

.action-card b,
.action-card span,
.section-head b,
.section-head span {
  display: block;
}

.action-card b {
  margin-bottom: 8px;
  font-size: 16px;
}

.action-card span {
  opacity: 0.74;
  font-size: 12px;
  line-height: 1.35;
}

.section-head,
.sheet-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 8px 0 12px;
}

.section-head b,
.sheet-title b {
  color: #fff3dc;
  font-size: 17px;
}

.section-head span,
.sheet-title span {
  display: block;
  margin-top: 3px;
  color: rgba(255, 243, 220, 0.48);
  font-size: 12px;
  font-weight: 700;
}

.style-list {
  display: grid;
  gap: 10px;
}

.style-item {
  display: grid;
  grid-template-columns: 52px 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 10px;
  border-radius: 18px;
  cursor: pointer;
}

.thumb {
  overflow: hidden;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background:
    radial-gradient(circle at 30% 22%, rgba(255, 255, 255, 0.48), transparent 24%),
    linear-gradient(145deg, #eed29a, #5f6b4f);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.style-item b,
.style-item span {
  display: block;
}

.style-item b {
  margin-bottom: 4px;
  color: #171512;
  font-size: 14px;
}

.style-item span {
  color: rgba(23, 21, 18, 0.5);
  font-size: 12px;
}

.style-item strong {
  color: #8a6425;
  font-size: 14px;
}

.empty-state {
  display: grid;
  gap: 6px;
  padding: 18px;
  border-radius: 20px;
}

.empty-state span {
  color: rgba(23, 21, 18, 0.58);
  font-size: 13px;
  line-height: 1.45;
}

.camera-area {
  position: relative;
  display: block;
  height: 230px;
  margin: 8px 0 18px;
  overflow: hidden;
  border: 1px solid rgba(239, 204, 132, 0.16);
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(8, 9, 7, 0.08), rgba(8, 9, 7, 0.58)),
    radial-gradient(circle at 76% 18%, rgba(248, 221, 161, 0.28), transparent 30%),
    linear-gradient(135deg, #b9a886, #3f4938);
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.28);
}

.camera-area input {
  display: none;
}

.camera-area img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: -6px 0 18px;
}

.photo-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 48px;
  border: 1px solid rgba(231, 202, 139, 0.28);
  border-radius: 18px;
  color: #fff4dc;
  background: rgba(255, 244, 220, 0.1);
  font-weight: 900;
}

.photo-actions button:first-child {
  color: #171512;
  background: linear-gradient(145deg, #f4d994, #d59a3d);
}

.scan-frame {
  position: absolute;
  inset: 22px;
  z-index: 1;
  border: 2px solid rgba(255, 235, 185, 0.88);
  border-radius: 24px;
}

.mock-shirt {
  position: absolute;
  left: 50%;
  top: 38px;
  width: 135px;
  height: 182px;
  border-radius: 58px 58px 26px 26px;
  background:
    linear-gradient(90deg, transparent 47%, rgba(255, 255, 255, 0.22) 48%, transparent 50%),
    linear-gradient(150deg, #f2d79c, #80602b 68%);
  box-shadow: 0 24px 40px rgba(35, 24, 10, 0.2);
  transform: translateX(-50%);
}

.scan-copy {
  position: absolute;
  left: 22px;
  right: 22px;
  bottom: 20px;
  z-index: 2;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  color: #fff;
}

.scan-copy b,
.scan-copy span {
  display: block;
}

.scan-copy b {
  font-size: 20px;
}

.scan-copy span {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.76);
  font-size: 12px;
}

.shutter {
  display: grid !important;
  flex: 0 0 auto;
  width: 54px;
  height: 54px;
  place-items: center;
  border: 3px solid rgba(255, 255, 255, 0.78);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  color: #fff !important;
  font-size: 22px !important;
}

.category-grid {
  gap: 10px;
}

.category-grid button {
  min-height: 84px;
  padding: 14px;
  border: 0;
  border-radius: 20px;
  text-align: left;
}

.category-grid b,
.category-grid span {
  display: block;
}

.category-grid b {
  color: #050505;
  font-size: 15px;
}

.category-grid span {
  margin-top: 5px;
  color: rgba(23, 21, 18, 0.5);
  font-size: 12px;
  font-weight: 700;
}

.custom-category {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 74px;
  gap: 8px;
  margin-top: 12px;
  padding: 10px;
  border-radius: 20px;
}

.custom-category input,
.style-name-field input,
.name-input {
  min-width: 0;
  border: 2px solid #d2b98f;
  border-radius: 14px;
  outline: 0;
  background: #fffaf2;
  color: #050505;
  font-weight: 900;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.8);
}

.custom-category input {
  height: 42px;
  padding: 0 12px;
  font-size: 14px;
}

.custom-category button,
.sheet-title button,
.calc-button,
.result-actions button,
.bottom-bar {
  border: 1px solid rgba(231, 202, 139, 0.16);
  color: #ffe9b8;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.08), transparent),
    linear-gradient(145deg, #080a07, #1d2118);
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.36);
}

.custom-category button {
  border-radius: 14px;
  font-weight: 900;
}

.style-name-field {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.style-name-field span {
  color: rgba(255, 243, 220, 0.58);
  font-size: 12px;
  font-weight: 800;
}

.style-name-field input,
.name-input {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  font-size: 16px;
}

.input-help {
  margin: 0 0 12px;
  padding: 10px 12px;
  border-radius: 16px;
  color: #2b210f;
  background: linear-gradient(145deg, #f8daa0, #d2a657);
  font-size: 13px;
  font-weight: 900;
  line-height: 1.45;
}

.cost-sheet {
  margin-top: 10px;
  padding: 16px;
  border-radius: 28px;
}

.sheet-title b {
  color: #17130c;
}

.sheet-title span {
  color: rgba(23, 19, 12, 0.48);
}

.sheet-title button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 34px;
  border-radius: 13px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
}

.line-card {
  display: grid;
  gap: 10px;
  margin-bottom: 10px;
  padding: 13px;
  border: 1px solid rgba(23, 21, 18, 0.08);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
}

.line-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 34px;
  gap: 8px;
  align-items: end;
}

.process-grid {
  grid-template-columns: 1fr 34px;
}

.line-grid label {
  display: grid;
  gap: 5px;
}

.line-grid small {
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 800;
}

.line-grid em,
.input-row em {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-height: 38px;
  border: 2px solid #d2b98f;
  border-radius: 14px;
  background: #fffaf2;
  color: #050505;
  font-style: normal;
  font-size: 15px;
  font-weight: 900;
  text-align: right;
}

.line-grid em input,
.input-row em input {
  width: 58px;
  border: 0;
  outline: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: right;
}

.delete-btn {
  display: grid;
  width: 34px;
  height: 38px;
  place-items: center;
  border: 0;
  border-radius: 13px;
  color: #8a5a32;
  background: rgba(194, 145, 62, 0.16);
}

.input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  min-height: 58px;
  margin-top: 10px;
  padding: 10px;
  border: 1px solid rgba(23, 21, 18, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
}

.input-row small,
.input-row b {
  display: block;
}

.input-row small {
  margin-bottom: 5px;
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 800;
}

.input-row b {
  color: #050505;
  font-size: 16px;
}

.input-row em {
  min-width: 86px;
  padding: 10px 12px;
}

.calc-button {
  display: grid;
  width: 100%;
  height: 54px;
  margin-top: 18px;
  place-items: center;
  border-radius: 20px;
  font-weight: 900;
}

.result-hero {
  padding: 22px;
  border-radius: 30px;
}

.result-hero strong {
  display: block;
  margin: 10px 0 8px;
  font-size: 56px;
  line-height: 1;
  letter-spacing: -0.05em;
}

.metric-grid,
.profit-strip {
  gap: 10px;
  margin: 12px 0;
}

.metric-grid article,
.profit-strip div {
  padding: 13px;
  border-radius: 20px;
}

.metric-grid span,
.metric-grid b,
.profit-strip span,
.profit-strip b {
  display: block;
}

.metric-grid span,
.profit-strip span {
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 800;
}

.metric-grid b,
.profit-strip b {
  margin-top: 6px;
  color: #050505;
  font-size: 21px;
}

.risk {
  display: flex;
  gap: 8px;
  padding: 14px;
  border-radius: 22px;
  color: #2b210f;
  background: linear-gradient(145deg, #f8daa0, #d2a657);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.14);
  font-size: 13px;
  line-height: 1.45;
}

.result-actions {
  gap: 10px;
  margin-top: 12px;
}

.result-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  height: 46px;
  border-radius: 18px;
  font-weight: 900;
}

.result-actions button:first-child {
  color: #171512;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
}

.profile-card {
  display: grid;
  grid-template-columns: 62px 1fr;
  gap: 14px;
  align-items: center;
  padding: 18px;
  border: 1px solid rgba(239, 204, 132, 0.18);
  border-radius: 28px;
  background:
    radial-gradient(circle at 88% 18%, rgba(231, 185, 88, 0.42), transparent 30%),
    linear-gradient(145deg, #080907 0%, #1b2115 56%, #433719 100%);
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.avatar-mark {
  display: grid;
  width: 62px;
  height: 62px;
  place-items: center;
  border-radius: 22px;
  color: #17120a;
  background: linear-gradient(145deg, #ffe4a8, #b88335);
  box-shadow: 0 14px 30px rgba(188, 132, 50, 0.28);
  font-size: 28px;
  font-weight: 900;
}

.profile-card span,
.profile-card strong,
.profile-card p {
  display: block;
}

.profile-card span {
  color: rgba(255, 240, 204, 0.62);
  font-size: 12px;
  font-weight: 800;
}

.profile-card strong {
  margin-top: 4px;
  color: #fff6df;
  font-size: 20px;
  letter-spacing: -0.03em;
}

.profile-card p {
  margin: 7px 0 0;
  color: rgba(255, 249, 238, 0.72);
  font-size: 12px;
  line-height: 1.45;
}

.profile-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 14px 0;
}

.profile-stats article {
  padding: 16px;
  border-radius: 22px;
  color: #17130c;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.58);
}

.profile-stats span,
.profile-stats b,
.profile-stats small {
  display: block;
}

.profile-stats span {
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 800;
}

.profile-stats b {
  margin-top: 8px;
  color: #050505;
  font-size: 32px;
  line-height: 1;
  letter-spacing: -0.05em;
}

.profile-stats small {
  margin-top: 5px;
  color: #8a6425;
  font-size: 12px;
  font-weight: 900;
}

.profile-panel {
  margin-top: 12px;
  padding: 16px;
  border-radius: 26px;
  color: #17130c;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.58);
}

.panel-title {
  margin-bottom: 12px;
}

.panel-title b,
.panel-title span {
  display: block;
}

.panel-title b {
  color: #17130c;
  font-size: 17px;
}

.panel-title span {
  margin-top: 4px;
  color: rgba(23, 21, 18, 0.5);
  font-size: 12px;
  font-weight: 800;
}

.setting-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  width: 100%;
  min-height: 62px;
  padding: 10px 0;
  border: 0;
  border-top: 1px solid rgba(23, 21, 18, 0.08);
  background: transparent;
  text-align: left;
}

.setting-row span,
.setting-row b,
.setting-row small {
  display: block;
}

.setting-row b {
  color: #050505;
  font-size: 15px;
}

.setting-row small {
  margin-top: 4px;
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
}

.setting-row strong {
  min-width: 58px;
  padding: 9px 10px;
  border-radius: 14px;
  color: #17120a;
  background: linear-gradient(145deg, #f6d796, #ba7d2c);
  font-size: 13px;
  text-align: center;
}

.profile-field {
  display: grid;
  gap: 7px;
  margin-top: 12px;
}

.profile-field span {
  color: rgba(23, 21, 18, 0.58);
  font-size: 13px;
  font-weight: 900;
}

.profile-field input {
  height: 46px;
  border: 2px solid #d2b98f;
  border-radius: 16px;
  outline: 0;
  padding: 0 12px;
  color: #050505;
  background: #fffaf2;
  font-size: 15px;
  font-weight: 900;
}

.profile-field input:focus {
  border-color: #1f241f;
  box-shadow: 0 0 0 3px rgba(194, 145, 62, 0.22);
}

.asset-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.asset-grid button {
  min-height: 48px;
  border: 1px solid rgba(138, 100, 37, 0.2);
  border-radius: 16px;
  color: #17120a;
  background: rgba(255, 255, 255, 0.42);
  font-size: 13px;
  font-weight: 900;
}

.asset-page {
  display: grid;
  gap: 10px;
}

.asset-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  min-height: 62px;
  padding: 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.58);
}

.asset-row > span,
.asset-row b,
.asset-row small {
  display: block;
}

.asset-row b {
  color: #050505;
  font-size: 15px;
}

.asset-row small {
  margin-top: 4px;
  color: rgba(23, 21, 18, 0.5);
  font-size: 12px;
  font-weight: 800;
}

.asset-row strong {
  color: #8a6425;
  font-size: 14px;
  white-space: nowrap;
}

.asset-page .empty-state {
  color: #17130c;
  background: rgba(255, 255, 255, 0.58);
}

.bottom-bar {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 16px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  align-items: center;
  height: 54px;
  border-radius: 22px;
}

.bottom-bar button {
  display: grid;
  gap: 2px;
  place-items: center;
  border: 0;
  background: transparent;
  color: rgba(255, 250, 240, 0.7);
  font-size: 11px;
}

.bottom-bar button.active {
  color: #f6d796;
  font-weight: 900;
}

button {
  cursor: pointer;
  transition:
    transform 180ms ease,
    filter 180ms ease,
    opacity 180ms ease;
}

button:hover {
  filter: brightness(1.05);
}

button:active {
  transform: translateY(1px) scale(0.99);
}

input:focus,
button:focus-visible {
  outline: 3px solid rgba(246, 215, 150, 0.45);
  outline-offset: 2px;
}

@media (max-width: 900px) {
  .mobile-showcase {
    display: block;
    min-height: 100dvh;
    padding: 0;
    overflow: hidden;
    background: #0e110d;
  }

  .mobile-showcase::before,
  .mobile-showcase::after,
  .desktop-copy {
    display: none;
  }

  .phone {
    width: 100vw;
    height: 100dvh;
    padding: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
  }

  .screen {
    border-radius: 0;
  }

  .notch {
    display: none;
  }

  .app-view {
    height: calc(100dvh - 74px);
    padding-top: 0;
  }

  .page {
    padding: 18px 20px;
  }
}

@media (max-width: 360px) {
  .quick-actions,
  .category-grid,
  .metric-grid,
  .profit-strip,
  .result-actions {
    grid-template-columns: 1fr;
  }
}
</style>

