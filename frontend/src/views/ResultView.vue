<script setup lang="ts">
import { CopyDocument, Share, WarningFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useStore, money } from '../composables/useStore'

const router = useRouter()
const {
  suggestedPrice,
  minimumPrice,
  fabricCost,
  processCost,
  singleCost,
  singleProfit,
  riskText,
  saveError,
  saveSuccess,
  saveCurrentStyle,
} = useStore()

function goCost() {
  router.push({ name: 'cost' })
}

async function onSave() {
  await saveCurrentStyle()
  if (saveSuccess.value) {
    router.push({ name: 'home' })
  }
}
</script>

<template>
  <div class="page">
    <header class="nav">
      <div>
        <span class="hello">步骤 3/3 · 报价结果</span>
        <h2>这单能不能接？</h2>
      </div>
      <button class="icon-btn" type="button" @click="onSave">
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
      <button type="button" @click="goCost">
        <el-icon><CopyDocument /></el-icon>
        复制改价
      </button>
      <button type="button" @click="onSave">
        <el-icon><Share /></el-icon>
        保存款式
      </button>
    </div>
  </div>
</template>

<style scoped>
.page {
  position: absolute; inset: 0;
  overflow-y: auto; padding: 12px 16px 16px;
  scrollbar-width: none;
}
.page::-webkit-scrollbar { display: none; }

.nav {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 16px;
}
.hello { color: rgba(255,243,220,0.5); font-size: 12px; }
.nav h2 { margin: 2px 0 0; color: #fff3dc; font-size: 22px; font-weight: 900; }

.icon-btn {
  display: grid; width: 38px; height: 38px; place-items: center;
  border: 0; border-radius: 13px;
  color: #17120a; background: linear-gradient(145deg, #f3d891, #d3a24c);
  box-shadow: 0 6px 16px rgba(180,120,40,0.25); font-size: 16px;
}

/* 主价格卡 */
.result-hero {
  position: relative; overflow: hidden;
  padding: 20px; border-radius: 22px; text-align: center;
  border: 1px solid rgba(239,204,132,0.2);
  background:
    radial-gradient(circle at 50% 0%, rgba(240,180,80,0.2), transparent 40%),
    linear-gradient(160deg, #0d221c 0%, #16281e 50%, #1f2818 100%);
  box-shadow: 0 12px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.06);
}
.result-hero span { color: rgba(255,240,204,0.55); font-size: 12px; font-weight: 800; }
.result-hero strong {
  display: block; margin: 6px 0 4px;
  font-size: 52px; font-weight: 950; line-height: 1; color: #f0d188;
}
.result-hero p {
  max-width: 220px; margin: 0 auto;
  color: rgba(255,249,238,0.6); font-size: 12px; line-height: 1.5;
}

/* 指标网格 */
.metric-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0;
}
.metric-grid article {
  padding: 12px 14px; border-radius: 16px;
  background: linear-gradient(145deg, #fffef9, #f3e8d2);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.metric-grid span { color: rgba(23,21,18,0.45); font-size: 11px; font-weight: 800; }
.metric-grid b { display: block; margin-top: 4px; color: #1a1812; font-size: 19px; font-weight: 900; }

/* 批量利润 */
.profit-strip {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;
}
.profit-strip div {
  padding: 12px 14px; border-radius: 16px; text-align: center;
  background: linear-gradient(145deg, #0d3326, #0a261c);
  border: 1px solid rgba(240,209,136,0.15);
}
.profit-strip span { color: rgba(255,243,220,0.55); font-size: 11px; font-weight: 800; }
.profit-strip b { display: block; margin-top: 4px; color: #f0d188; font-size: 18px; font-weight: 950; }

/* 风险提醒 */
.risk {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; border-radius: 16px;
  color: #3d2a0a; background: linear-gradient(135deg, #f2d896, #dbb85c);
  font-size: 12px; line-height: 1.5; font-weight: 750;
}
.risk .el-icon { flex-shrink: 0; margin-top: 1px; }
.risk b { font-weight: 950; }

.auth-error {
  margin-top: 8px; padding: 8px 12px; border-radius: 12px;
  color: #8b2118; background: #ffe8e4; font-size: 12px; font-weight: 800;
}

/* 操作按钮 */
.result-actions {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px;
}
.result-actions button {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  min-height: 44px; border-radius: 14px; font-size: 13px; font-weight: 900;
  border: 0;
  color: #ffe9b8; background: linear-gradient(145deg, #1a1f18, #242922);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.result-actions button:first-child {
  color: #1a1812;
  background: linear-gradient(145deg, #fffef9, #efe2c8);
}
</style>
}
