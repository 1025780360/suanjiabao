<script setup lang="ts">
import { ChatDotRound, CopyDocument, Delete, Plus, Scissor } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useStore, money } from '../composables/useStore'

const router = useRouter()
const { profile, visibleStyles, recentWeekCount, totalFabricCost, averageProfit, activeAsset, copySavedStyle, removeStyle } = useStore()
const swipedId = ref<number | null>(null)
let touchStartX = 0

function shortMoney(val: number) {
  if (val >= 10000) return '¥' + (val / 10000).toFixed(1) + 'w'
  return '¥' + money(val)
}

function goPhoto() { router.push({ name: 'photo' }) }
function goAi() { router.push({ name: 'ai-costing' }) }

function goCopyOrPhoto() {
  if (visibleStyles.value.length) {
    copySavedStyle(visibleStyles.value[0])
    router.push({ name: 'cost' })
  } else {
    router.push({ name: 'photo' })
  }
}

function openStyle(style: any) {
  if (swipedId.value) { swipedId.value = null; return }
  copySavedStyle(style)
  router.push({ name: 'cost' })
}

function goAllStyles() {
  activeAsset.value = 'styles'
  router.push({ name: 'asset', params: { kind: 'styles' } })
}

// ── 左滑删除 ──
function onTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX
}

function onTouchEnd(e: TouchEvent, id: number) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (dx < -60) {
    swipedId.value = id
  } else if (dx > 30 || swipedId.value === id) {
    swipedId.value = null
  }
}

function closeSwipe() {
  swipedId.value = null
}

async function onDelete(style: any) {
  await removeStyle(style.id)
  swipedId.value = null
}
</script>

<template>
  <div class="page home-page">
    <header class="home-head">
      <div>
        <span>你好，{{ profile.ownerName || '老板' }}</span>
        <h2>今天先算哪款？</h2>
      </div>
      <button class="round-add" type="button" @click="goPhoto">
        <el-icon><Plus /></el-icon>
      </button>
    </header>

    <section class="metric-band">
      <article>
        <b>{{ recentWeekCount }}</b>
        <span>最近款式</span>
        <small>近 7 天新增</small>
      </article>
      <article>
        <b>{{ visibleStyles.length }}</b>
        <span>款式总数</span>
        <small>累计保存</small>
      </article>
      <article>
        <b>{{ shortMoney(totalFabricCost) }}</b>
        <span>面料成本</span>
        <small>全部款式合计</small>
      </article>
      <article>
        <b>¥{{ money(averageProfit) }}</b>
        <span>平均利润</span>
        <small>单件</small>
      </article>
    </section>

    <div class="quick-actions">
      <button class="action-card primary" type="button" @click="goPhoto">
        <el-icon><Scissor /></el-icon>
        <b>快速算价</b>
        <span>新建款式并计算</span>
      </button>
      <button class="action-card dark" type="button" @click="goCopyOrPhoto">
        <el-icon><CopyDocument /></el-icon>
        <b>复制旧款</b>
        <span>基于旧款快速建款</span>
      </button>
      <button class="action-card light" type="button" @click="goAi">
        <strong>AI</strong>
        <b>AI 助手</b>
        <span>智能分析与建议</span>
      </button>
    </div>

    <section class="recent-panel">
      <div class="section-head">
        <b>最近款式</b>
        <button type="button" @click="goAllStyles">全部</button>
      </div>

      <div v-if="visibleStyles.length" class="style-list" @click="closeSwipe">
        <div
          v-for="item in visibleStyles"
          :key="item.id"
          class="swipe-row"
          :class="{ swiped: swipedId === item.id }"
          @touchstart.passive="onTouchStart($event)"
          @touchend.passive="onTouchEnd($event, item.id)"
        >
          <button class="swipe-del" type="button" @click.stop="onDelete(item)">
            <el-icon><Delete /></el-icon>
            <span>删除</span>
          </button>
          <article class="style-item" @click="openStyle(item)">
            <div class="thumb">
              <img v-if="item.image" :src="item.image" alt="款式图片" />
            </div>
            <div class="style-copy">
              <b>{{ item.name }}</b>
              <span>{{ item.category || '未分类' }}</span>
            </div>
            <aside>
              <strong>¥{{ money(item.price) }}</strong>
              <em>报价</em>
            </aside>
          </article>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><ChatDotRound /></el-icon>
        <b>还没有款式档案</b>
        <span>先拍一张衣服照片，算完报价后这里会自动沉淀记录。</span>
        <button type="button" @click="goPhoto">开始建款</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  padding: 14px 16px 12px;
}

.home-head {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.home-head span {
  color: rgba(23, 32, 24, 0.62);
  font-size: 13px;
  font-weight: 650;
}

.home-head h2 {
  margin: 4px 0 0;
  color: #073426;
  font-size: 27px;
  line-height: 1.05;
  font-weight: 950;
  letter-spacing: -0.06em;
}

.round-add {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  color: #07110d;
  background: var(--gold-gradient);
  box-shadow: 0 12px 22px rgba(169, 112, 43, 0.24);
  font-size: 22px;
}

.metric-band {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  overflow: hidden;
  min-height: 96px;
  border: 1px solid rgba(240, 209, 136, 0.22);
  border-radius: 18px;
  color: #f7e7bf;
  background:
    radial-gradient(circle at 20% 0%, rgba(255, 236, 176, 0.18), transparent 36%),
    linear-gradient(145deg, #063323, #062417 74%);
  box-shadow: 0 18px 36px rgba(18, 53, 39, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.11);
}

.metric-band article {
  display: grid;
  align-content: center;
  justify-items: center;
  min-width: 0;
  padding: 10px 2px;
  text-align: center;
}

.metric-band b {
  overflow: hidden;
  width: 100%;
  color: #f0d188;
  font-size: 22px;
  line-height: 1;
  font-weight: 950;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-band span {
  margin-top: 7px;
  color: #fff4d4;
  font-size: 12px;
  font-weight: 900;
}

.metric-band small {
  margin-top: 5px;
  color: rgba(251, 242, 223, 0.74);
  font-size: 10px;
  font-weight: 750;
}

.quick-actions {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 18px 0 18px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 6px;
  padding: 12px 6px 14px;
  border: 1px solid rgba(188, 139, 57, 0.25);
  border-radius: 20px;
  text-align: center;
  cursor: pointer;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.action-card > :first-child {
  margin-top: 0 !important;
}

.action-card:active {
  transform: scale(0.96);
}

.action-card :deep(i) {
  display: flex !important;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  font-size: 18px;
  margin: 0 !important;
}

.action-card strong {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  font-size: 22px;
  font-weight: 950;
  line-height: 1;
  margin: 0 !important;
}

.action-card b {
  color: inherit;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: -0.01em;
  line-height: 1;
  margin: 0;
}

.action-card span {
  color: currentColor;
  opacity: 0.6;
  font-size: 10px;
  font-weight: 650;
  line-height: 1.1;
  margin: 0;
}

/* 快速算价 — 金色 */
.action-card.primary {
  color: #1a1205;
  background: linear-gradient(160deg, #f8dc9a 0%, #daa54a 45%, #b87a28 100%);
  border-color: rgba(200, 145, 45, 0.4);
  box-shadow:
    0 4px 16px rgba(180, 120, 40, 0.22),
    0 1px 0 rgba(255, 255, 255, 0.25) inset;
}
.action-card.primary .el-icon {
  background: rgba(0,0,0,0.1);
  color: #fff8e1;
}

/* 复制旧款 — 深色 */
.action-card.dark {
  color: #f0ddb0;
  background: linear-gradient(160deg, #0a2e22 0%, #0d3f2f 50%, #072016 100%);
  border-color: rgba(140, 180, 140, 0.3);
  box-shadow:
    0 4px 18px rgba(8, 40, 30, 0.28),
    0 1px 0 rgba(255,255,255,0.08) inset;
}
.action-card.dark .el-icon {
  background: rgba(255,255,255,0.08);
  color: #f0d188;
}

/* AI 助手 — 浅色 */
.action-card.light {
  color: #0d3325;
  background: linear-gradient(160deg, #fffdf7 0%, #faf3e0 40%, #efe1c4 100%);
  border-color: rgba(190, 160, 110, 0.35);
  box-shadow:
    0 4px 16px rgba(80, 60, 30, 0.1),
    0 1px 0 rgba(255,255,255,0.7) inset;
}
.action-card.light strong {
  background: linear-gradient(145deg, #f3d891, #d3a24c);
  color: #1a1205;
}

.recent-panel {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
}

.section-head {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-head b {
  color: #101a14;
  font-size: 21px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.section-head button {
  min-height: 32px;
  border: 0;
  color: rgba(23, 32, 24, 0.58);
  background: transparent;
  font-size: 13px;
  font-weight: 800;
}

.style-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  border: 1px solid rgba(188, 139, 57, 0.22);
  border-radius: 16px;
  background: rgba(255, 250, 241, 0.7);
  scrollbar-width: none;
  overscroll-behavior: contain;
}

.style-list::-webkit-scrollbar { display: none; }

/* ── 左滑删除容器 ── */
.swipe-row {
  position: relative;
  overflow: hidden;
}

.swipe-row + .swipe-row {
  border-top: 1px solid rgba(188, 139, 57, 0.18);
}

.swipe-del {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  width: 68px;
  border: 0;
  border-radius: 0 12px 12px 0;
  color: #fff;
  background: #c0392b;
  font-size: 16px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 150ms ease;
  z-index: 0;
}

.swipe-row.swiped .swipe-del {
  opacity: 1;
}

.swipe-del span {
  font-size: 11px;
  font-weight: 800;
}

.swipe-row .style-item {
  position: relative;
  z-index: 2;
  background: linear-gradient(145deg, #fffef9, #f5ecd6);
  will-change: transform;
  transition: transform 220ms cubic-bezier(0.25, 0.8, 0.25, 1.2);
  transform: translateX(0);
}

.swipe-row.swiped .style-item {
  transform: translateX(-68px);
}

.style-item {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto 14px;
  gap: 10px;
  align-items: center;
  min-height: 68px;
  padding: 8px 10px;
  cursor: pointer;
}


.thumb {
  overflow: hidden;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background:
    radial-gradient(circle at 26% 18%, rgba(255, 255, 255, 0.5), transparent 25%),
    linear-gradient(145deg, #d6cda8, #65705c);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.style-copy {
  min-width: 0;
}

.style-copy b,
.style-copy span,
.style-copy small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.style-copy b {
  color: #101410;
  font-size: 14px;
  font-weight: 950;
}

.style-copy span,
.style-copy small {
  margin-top: 3px;
  color: rgba(23, 32, 24, 0.54);
  font-size: 11px;
  font-weight: 720;
}

.style-item aside {
  display: grid;
  justify-items: end;
  gap: 5px;
}

.style-item aside strong {
  color: #101410;
  font-size: 15px;
  font-weight: 950;
}

.style-item aside em {
  padding: 3px 8px;
  border: 1px solid rgba(189, 139, 57, 0.38);
  border-radius: 999px;
  color: #a9702b;
  font-size: 10px;
  font-style: normal;
  font-weight: 900;
}

.empty-state {
  display: grid;
  flex: 1;
  align-content: center;
  justify-items: start;
  gap: 9px;
  padding: 22px;
  border: 1px solid rgba(188, 139, 57, 0.2);
  border-radius: 22px;
  color: #172018;
  background: rgba(255, 250, 241, 0.72);
}

.empty-state .el-icon {
  color: #bd8b39;
  font-size: 28px;
}

.empty-state b {
  font-size: 18px;
  font-weight: 950;
}

.empty-state span {
  color: rgba(23, 32, 24, 0.62);
  font-size: 14px;
  line-height: 1.55;
}

.empty-state button {
  min-height: 44px;
  padding: 0 18px;
  border: 0;
  border-radius: 15px;
  color: #07110d;
  background: var(--gold-gradient);
  font-weight: 950;
}

@media (max-width: 390px) {
  .home-page {
    padding-inline: 14px;
  }

  .home-head h2 {
    font-size: 29px;
  }

  .quick-actions {
    gap: 9px;
  }

  .action-card {
    min-height: 122px;
  }
}
</style>
