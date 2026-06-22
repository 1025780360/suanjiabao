<script setup lang="ts">
import { Close } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { getMembershipInfo } from '../api/http'

const router = useRouter()
const loading = ref(true)
const info = ref<any>({})
const billing = ref<'monthly' | 'quarterly' | 'yearly'>('yearly')

const plans = [
  {
    key: 'free', name: '免费版',
    monthly: 0, quarterly: 0, yearly: 0,
    features: ['5 个款式', '5 次AI/天', '系统模板', '基础利润分析', '最近10条报价'],
  },
  {
    key: 'pro', name: '专业版',
    monthly: 29, quarterly: 69, yearly: 279,
    discount: { quarterly: '省¥18', yearly: '省¥69' },
    features: ['100 个款式', '100 次AI/天', '3 自定义模板', '批量报价', '全部历史报价', '月度利润趋势'],
  },
  {
    key: 'ultimate', name: '旗舰版',
    monthly: 69, quarterly: 169, yearly: 659,
    discount: { quarterly: '省¥38', yearly: '省¥169' },
    features: ['200 个款式', 'AI 无限次', '无限模板', '批量报价+对比', 'AI 智能定价', '导出 Excel', '3 人团队协作'],
  },
]

function price(p: typeof plans[0]) {
  return p[billing.value]
}

function goPay(plan: string) {
  router.push({ name: 'pay', query: { plan, billing: billing.value } })
}

function goHome() { router.push({ name: 'profile' }) }

onMounted(async () => {
  try { info.value = await getMembershipInfo() } catch { /* */ }
  loading.value = false
})
</script>

<template>
  <div class="page">
    <header class="nav">
      <div><span class="hello">会员中心</span><h2>选择套餐</h2></div>
      <button class="icon-btn" @click="goHome"><el-icon><Close /></el-icon></button>
    </header>

    <!-- 计费周期切换 -->
    <div class="billing-tabs">
      <button :class="{ active: billing === 'monthly' }" @click="billing = 'monthly'">月付</button>
      <button :class="{ active: billing === 'quarterly' }" @click="billing = 'quarterly'">季付</button>
      <button :class="{ active: billing === 'yearly' }" @click="billing = 'yearly'">
        年付 <small>最省</small>
      </button>
    </div>

    <!-- 套餐卡片 -->
    <div class="plan-cards">
      <div v-for="p in plans" :key="p.key"
        class="plan-card"
        :class="{ current: info.plan === p.key, highlight: p.key === 'pro' }">
        <div class="card-top">
          <b>{{ p.name }}</b>
          <div class="price-row">
            <strong v-if="price(p) === 0">免费</strong>
            <strong v-else>¥{{ price(p) }}</strong>
            <small v-if="billing !== 'monthly' && price(p) > 0">/{{ billing === 'quarterly' ? '季' : '年' }}</small>
          </div>
          <em v-if="p.discount && billing !== 'monthly'">{{ (p.discount as any)[billing] }}</em>
        </div>
        <ul>
          <li v-for="f in p.features" :key="f">{{ f }}</li>
        </ul>
        <button v-if="info.plan === p.key" class="btn current" disabled>当前套餐</button>
        <button v-else-if="p.key === 'free'" class="btn outline" disabled>默认</button>
        <button v-else class="btn primary" @click="goPay(p.key)">
          {{ p.key === 'pro' ? '升级专业版' : '升级旗舰版' }}
        </button>
      </div>
    </div>

    <!-- 扩容包 -->
    <h3 class="ext-title">扩容包</h3>
    <div class="ext-list">
      <div class="ext-item">
        <span>款式存档 +5 个</span>
        <strong>¥10</strong>
        <button class="ext-btn" @click="goPay('style')">购买</button>
      </div>
      <div class="ext-item">
        <span>AI 次数 +10 次/天</span>
        <strong>¥8/月</strong>
        <button class="ext-btn" @click="goPay('ai')">购买</button>
      </div>
      <div class="ext-item">
        <span>成本模板 +2 个</span>
        <strong>¥6</strong>
        <button class="ext-btn" @click="goPay('template')">购买</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { position: absolute; inset: 0; overflow-y: auto; padding: 12px 14px 20px; scrollbar-width: none; }
.page::-webkit-scrollbar { display: none; }
.nav { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.hello { color: rgba(23,32,24,0.5); font-size: 11px; }
.nav h2 { color: #1a1812; font-size: 21px; font-weight: 900; margin: 2px 0 0; }
.icon-btn { width: 34px; height: 34px; display: grid; place-items: center; border: 0; border-radius: 11px; color: #17120a; background: linear-gradient(145deg, #f3d891, #d3a24c); font-size: 14px; }

/* 计费切换 */
.billing-tabs { display: flex; gap: 6px; margin-bottom: 14px; }
.billing-tabs button { flex: 1; height: 40px; border: 1.5px solid rgba(189,139,57,0.25); border-radius: 10px; background: rgba(255,255,255,0.6); color: #3d3020; font-size: 13px; font-weight: 800; cursor: pointer; }
.billing-tabs button.active { border-color: #bd8b39; background: rgba(240,209,136,0.35); color: #1a1205; font-weight: 900; }
.billing-tabs small { font-size: 10px; color: #8a6425; }

/* 套餐卡 */
.plan-cards { display: grid; gap: 10px; margin-bottom: 18px; }
.plan-card { padding: 16px; border-radius: 16px; background: linear-gradient(160deg, #fffef9, #f5ecd6); border: 1px solid rgba(189,139,57,0.15); }
.plan-card.highlight { border-color: #bd8b39; box-shadow: 0 4px 16px rgba(189,139,57,0.12); }
.plan-card.current { opacity: 0.7; }
.card-top { text-align: center; margin-bottom: 12px; }
.card-top b { font-size: 17px; font-weight: 950; color: #1a1812; }
.price-row { margin: 4px 0; }
.price-row strong { font-size: 32px; font-weight: 950; color: #1a1812; }
.price-row small { font-size: 12px; color: rgba(23,21,18,0.4); }
.card-top em { font-size: 11px; color: #c0392b; font-weight: 900; font-style: normal; background: #ffe8e4; padding: 2px 8px; border-radius: 4px; }

.plan-card ul { margin: 0 0 12px; padding: 0; }
.plan-card li { font-size: 12px; color: #3d3020; padding: 4px 0; list-style: none; font-weight: 650; }
.plan-card li::before { content: '✓ '; color: #bd8b39; font-weight: 900; }

.btn { width: 100%; height: 42px; border: 0; border-radius: 12px; font-size: 14px; font-weight: 900; cursor: pointer; }
.btn.primary { color: #fff; background: linear-gradient(145deg, #1a1f18, #2a3020); }
.btn.outline { color: rgba(23,21,18,0.3); background: rgba(0,0,0,0.03); cursor: default; }
.btn.current { color: #8a6425; background: rgba(189,139,57,0.1); cursor: default; }

/* 扩容 */
.ext-title { font-size: 16px; font-weight: 950; color: #1a1812; margin: 0 0 10px; }
.ext-list { display: grid; gap: 8px; }
.ext-item { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-radius: 12px; background: rgba(255,255,255,0.7); border: 1.5px solid rgba(189,139,57,0.2); }
.ext-item span { flex: 1; font-size: 14px; color: #1a1812; font-weight: 750; }
.ext-item strong { color: #8a6425; font-size: 15px; font-weight: 950; }
.ext-btn { height: 30px; padding: 0 14px; border: 0; border-radius: 8px; font-size: 11px; font-weight: 900; color: #fff; background: linear-gradient(145deg, #1a1f18, #2a3020); cursor: pointer; }
</style>
