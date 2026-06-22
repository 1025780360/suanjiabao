<script setup lang="ts">
import { Close, CopyDocument, Delete, Promotion, Share } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, reactive, ref, watch } from 'vue'
import { useStore, money } from '../composables/useStore'
import type { AssetKind } from '../composables/useStore'

const route = useRoute()
const router = useRouter()
const { activeAsset, visibleStyles, visibleCategories, averageProfit, copySavedStyle, removeStyle } = useStore()

const kind = computed(() => (route.params.kind as AssetKind) || 'styles')

watch(kind, (val) => {
  activeAsset.value = val
}, { immediate: true })

const assetTitle = computed(() => {
  const titles: Record<AssetKind, string> = {
    styles: '款式档案', quotes: '报价记录', templates: '成本模板', profit: '利润分析',
  }
  return titles[kind.value]
})

function goHome() {
  router.push({ name: 'home' })
}

function openStyle(style: any) {
  copySavedStyle(style)
  router.push({ name: 'cost' })
}

// ── 长按菜单 ──
const menuVisible = ref(false)
const menuStyle = reactive({ top: '0px', left: '0px' })
let menuTarget: any = null
let longPressTimer: any = null

function onTouchStart(e: TouchEvent, style: any) {
  menuTarget = style
  longPressTimer = setTimeout(() => {
    const t = e.touches[0]
    menuStyle.top = (t.clientY - 60) + 'px'
    menuStyle.left = (t.clientX - 80) + 'px'
    menuVisible.value = true
  }, 500)
}

function onTouchMove() {
  clearTimeout(longPressTimer)
}

function onTouchEnd() {
  clearTimeout(longPressTimer)
}

function closeMenu() {
  menuVisible.value = false
  menuTarget = null
}

async function menuDelete() {
  if (menuTarget) await removeStyle(menuTarget.id)
  closeMenu()
}

function menuCopy() {
  if (menuTarget) {
    copySavedStyle(menuTarget)
    router.push({ name: 'cost' })
  }
  closeMenu()
}

async function menuShare() {
  if (!menuTarget) return
  const text = `${menuTarget.name} — 建议报价 ¥${money(menuTarget.price)}，单件利润 ¥${money(menuTarget.profit)}`
  if (navigator.share) {
    await navigator.share({ title: menuTarget.name, text })
  } else {
    await navigator.clipboard.writeText(text)
  }
  closeMenu()
}

function menuImportAi() {
  if (menuTarget) {
    copySavedStyle(menuTarget)
    router.push({ name: 'ai-costing' })
  }
  closeMenu()
}
</script>

<template>
  <div class="page">
    <header class="nav">
      <div>
        <span class="hello">{{ visibleStyles.length }} 款</span>
        <h2>{{ assetTitle }}</h2>
      </div>
      <button class="icon-btn" type="button" @click="goHome">
        <el-icon><Close /></el-icon>
      </button>
    </header>

    <section v-if="kind === 'styles'" class="style-panel">
      <div v-if="visibleStyles.length" class="style-grid">
        <article
            v-for="item in visibleStyles"
            :key="item.id"
            class="style-card"
            @click="openStyle(item)"
            @touchstart.prevent="onTouchStart($event, item)"
            @touchmove="onTouchMove"
            @touchend="onTouchEnd"
            @contextmenu.prevent
          >
          <div class="card-thumb">
            <img v-if="item.image" :src="item.image" alt="款式图片" />
            <div v-else class="no-img">{{ item.name.charAt(0) }}</div>
          </div>
          <div class="card-body">
            <b>{{ item.name }}</b>
            <small>{{ item.category || '未分类' }}</small>
          </div>
          <div class="card-price">
            <strong>¥{{ money(item.price) }}</strong>
            <em>利润 ¥{{ money(item.profit) }}</em>
          </div>
        </article>
      </div>
      <div v-else class="empty-state">
        <b>还没有款式档案</b>
        <span>算完报价保存后，这里会出现全部款式。</span>
      </div>
    </section>

    <section v-else-if="kind === 'quotes'" class="style-panel">
      <article v-for="item in visibleStyles" :key="item.id" class="asset-row">
        <span>
          <b>{{ item.name }}</b>
          <small>最低接单价 ¥{{ item.minPrice }} · 成本 ¥{{ money(item.cost) }}</small>
        </span>
        <strong>¥{{ item.price }}</strong>
      </article>
      <div v-if="!visibleStyles.length" class="empty-state">暂无报价记录。</div>
    </section>

    <section v-else-if="kind === 'templates'" class="style-panel">
      <article v-for="item in visibleCategories" :key="item.key" class="asset-row">
        <span>
          <b>{{ item.name }}</b>
          <small>{{ item.desc }}</small>
        </span>
        <strong>模板</strong>
      </article>
    </section>

    <section v-else class="style-panel">
      <article class="asset-row">
        <span><b>平均单件利润</b><small>来自已保存款式</small></span>
        <strong>¥{{ money(averageProfit) }}</strong>
      </article>
      <article class="asset-row">
        <span><b>最高建议价</b><small>已保存款式中最高报价</small></span>
        <strong>¥{{ money(Math.max(0, ...visibleStyles.map((item) => item.price))) }}</strong>
      </article>
    </section>

    <!-- 长按菜单 -->
    <div v-if="menuVisible" class="menu-overlay" @click="closeMenu">
      <div class="menu-popup" :style="{ top: menuStyle.top, left: menuStyle.left }" @click.stop>
        <button type="button" @click="menuCopy">
          <el-icon><CopyDocument /></el-icon> 复制款式
        </button>
        <button type="button" @click="menuShare">
          <el-icon><Share /></el-icon> 分享报价
        </button>
        <button type="button" @click="menuImportAi">
          <el-icon><Promotion /></el-icon> 导入AI助手
        </button>
        <button type="button" class="danger" @click="menuDelete">
          <el-icon><Delete /></el-icon> 删除
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  padding: 12px 18px 20px;
  scrollbar-width: none;
}

.page::-webkit-scrollbar { display: none; }

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
}

.hello {
  color: rgba(255, 243, 220, 0.58);
  font-size: 13px;
}

.nav h2 {
  margin: 3px 0 0;
  color: #fff3dc;
  font-size: 24px;
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

/* ── 款式网格 ── */
.style-panel {
  display: grid;
  gap: 10px;
}

.style-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.style-card {
  display: grid;
  grid-template-rows: auto 1fr auto;
  overflow: hidden;
  border-radius: 20px;
  color: #17130c;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.58);
  cursor: pointer;
  transition: transform 160ms ease;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
}

.style-card:active { transform: scale(0.97); }

.card-thumb {
  overflow: hidden;
  height: 120px;
  background:
    radial-gradient(circle at 30% 22%, rgba(255, 255, 255, 0.48), transparent 24%),
    linear-gradient(145deg, #eed29a, #5f6b4f);
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-img {
  display: grid;
  height: 100%;
  place-items: center;
  color: #fff;
  font-size: 42px;
  font-weight: 950;
  text-shadow: 0 2px 8px rgba(0,0,0,0.18);
}

.card-body {
  padding: 12px 12px 6px;
}

.card-body b {
  display: block;
  color: #050505;
  font-size: 14px;
  font-weight: 950;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-body small {
  display: block;
  margin-top: 3px;
  color: rgba(23, 21, 18, 0.5);
  font-size: 11px;
  font-weight: 750;
}

.card-price {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 6px 12px 12px;
}

.card-price strong {
  color: #8a6425;
  font-size: 16px;
  font-weight: 950;
}

.card-price em {
  color: rgba(23, 21, 18, 0.42);
  font-size: 11px;
  font-style: normal;
  font-weight: 750;
}

/* ── 列表行 ── */
.asset-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  min-height: 56px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.58);
}

.asset-row b {
  display: block;
  color: #050505;
  font-size: 15px;
}

.asset-row small {
  display: block;
  margin-top: 4px;
  color: rgba(23, 21, 18, 0.48);
  font-size: 12px;
  font-weight: 800;
}

.asset-row strong {
  color: #8a6425;
  font-size: 14px;
  white-space: nowrap;
}

/* ── 空状态 ── */
.empty-state {
  display: grid;
  gap: 6px;
  padding: 24px;
  border-radius: 20px;
  color: #17130c;
  background: rgba(255, 255, 255, 0.58);
  text-align: center;
  justify-items: center;
}

.empty-state b {
  color: #050505;
  font-size: 16px;
}

.empty-state span {
  color: rgba(23, 21, 18, 0.56);
  font-size: 13px;
  line-height: 1.5;
}

/* ── 长按菜单 ── */
.menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0,0,0,0.18);
}

.menu-popup {
  position: fixed;
  z-index: 201;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  display: grid;
  gap: 2px;
  padding: 6px;
  border-radius: 18px;
  background: linear-gradient(145deg, #1a1f18, #252a22);
  box-shadow: 0 16px 48px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08);
  min-width: 150px;
}

.menu-popup button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border: 0;
  border-radius: 13px;
  background: transparent;
  color: #f0ddb0;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  white-space: nowrap;
  transition: background 120ms ease;
}

.menu-popup button:active {
  background: rgba(255,255,255,0.1);
}

.menu-popup button.danger {
  color: #e07060;
}
</style>
