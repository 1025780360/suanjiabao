<script setup lang="ts">
import { Document, Files, FolderOpened, Setting, TrendCharts } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { useStore, money } from '../composables/useStore'
import { getAiChatHistory, getMembershipInfo } from '../api/http'
import type { AssetKind } from '../composables/useStore'

const router = useRouter()
const { profile, visibleStyles, visibleCategories, averageProfit, monthlyNewStyles, activeAsset, copySavedStyle } = useStore()

const quotedCount = computed(() => visibleStyles.value.filter(s => s.price > 0).length)
const templateCount = computed(() => visibleCategories.value.length)
const bestPrice = computed(() => Math.max(0, ...visibleStyles.value.map(s => s.price || 0)))

// ── 会员状态 ──
const memberInfo = ref<any>(null)
const planLabel: Record<string, string> = { free: '免费版', pro: '专业版', ultimate: '旗舰版' }

onMounted(async () => {
  try { memberInfo.value = await getMembershipInfo() } catch { /* */ }
})

// ── AI 最近对话 ──
const lastUserMsg = ref('')
const lastAiReply = ref('')
const lastDraft = ref<any>(null)

onMounted(async () => {
  try {
    const history = await getAiChatHistory()
    if (Array.isArray(history) && history.length) {
      const msgs = [...history].reverse()
      const user = msgs.find((m: any) => m.role === 'user')
      const ai = msgs.find((m: any) => m.role === 'assistant')
      if (user) lastUserMsg.value = user.text || ''
      if (ai) {
        lastAiReply.value = ai.text || ''
        if (ai.costDraft && Object.keys(ai.costDraft).length) lastDraft.value = ai
      }
    }
  } catch { /* 静默 */ }
})

function goSettings() { router.push({ name: 'settings' }) }
function goMembership() { router.push({ name: 'membership' }) }
function openAsset(kind: AssetKind) { activeAsset.value = kind; router.push({ name: 'asset', params: { kind } }) }
function goAiChat() { router.push({ name: 'ai-costing' }) }
function openAiDraft() {
  if (lastDraft.value?.costDraft) {
    copySavedStyle(lastDraft.value.costDraft)
    router.push({ name: 'cost' })
  }
}
</script>

<template>
  <div class="page profile-page">
    <header class="profile-head">
      <div class="shop-mark">L</div>
      <div>
        <h2>{{ profile.shopName || '拉斐尔定制工坊' }}</h2>
        <span>{{ profile.location || '广州 · 海珠区' }}</span>
      </div>
      <button type="button" @click="goSettings">
        <el-icon><Setting /></el-icon>
      </button>
    </header>

    <!-- 会员状态 -->
    <div v-if="memberInfo" class="member-strip" @click="goMembership">
      <div class="member-left">
        <span>
          {{ planLabel[memberInfo.plan] || '免费版' }}
          <em v-if="memberInfo.isTrial" class="trial-badge">试用 {{ memberInfo.trialDaysLeft }} 天</em>
        </span>
        <small>款式 {{ memberInfo.styleUsed }}/{{ memberInfo.styleQuota || '∞' }} · AI {{ memberInfo.aiUsedToday }}/{{ memberInfo.aiDailyQuota || '∞' }} 次</small>
        <small v-if="memberInfo.expireDate && memberInfo.plan !== 'free'" class="expire">到期：{{ memberInfo.expireDate }}</small>
      </div>
      <em v-if="!memberInfo.isTrial" class="arrow">升级 ›</em>
      <em v-else class="arrow trial">续费 ›</em>
    </div>

    <section class="archive-hero">
      <span>STYLE ARCHIVE OS</span>
      <h3>让每一次报价成为可复用的资产</h3>
      <p>档案沉淀越多，报价越精准，利润更可控。</p>
      <div class="archive-stats">
        <article>
          <small>本月新增</small>
          <b>{{ monthlyNewStyles }}</b>
          <em>款</em>
        </article>
        <article>
          <small>平均利润</small>
          <b>¥{{ money(averageProfit) }}</b>
          <em>/单</em>
        </article>
      </div>
    </section>

    <div class="profile-stats">
      <article>
        <span>已保存款式档案</span>
        <b>{{ visibleStyles.length }}</b>
        <small>个</small>
      </article>
      <article>
        <span>平均单件利润</span>
        <b>¥{{ money(averageProfit) }}</b>
        <small>全部款式</small>
      </article>
    </div>

    <section class="search-strip">
      <span>搜索档案、面料、客户或工艺</span>
      <button type="button">
        <el-icon><TrendCharts /></el-icon>
      </button>
    </section>

    <section class="asset-panel">
      <div class="section-title">
        <b>资产管理</b>
        <button type="button" @click="openAsset('styles')">全部</button>
      </div>

      <button class="asset-row" type="button" @click="openAsset('styles')">
        <i><el-icon><FolderOpened /></el-icon></i>
        <span>
          <b>款式档案</b>
          <small>管理已归档的款式资料与工艺配置</small>
        </span>
        <strong>{{ visibleStyles.length }} 个</strong>
      </button>
      <button class="asset-row" type="button" @click="openAsset('quotes')">
        <i><el-icon><Document /></el-icon></i>
        <span>
          <b>报价记录</b>
          <small>查看历史报价与客户沟通记录</small>
        </span>
        <strong>{{ quotedCount }} 条</strong>
      </button>
      <button class="asset-row" type="button" @click="openAsset('templates')">
        <i><el-icon><Files /></el-icon></i>
        <span>
          <b>成本模板</b>
          <small>整理常用成本结构与材料组合</small>
        </span>
        <strong>{{ templateCount }} 个</strong>
      </button>
      <button class="asset-row" type="button" @click="openAsset('profit')">
        <i><el-icon><TrendCharts /></el-icon></i>
        <span>
          <b>利润分析</b>
          <small>分析利润结构，优化定价策略</small>
        </span>
        <strong>¥{{ money(bestPrice) }}</strong>
      </button>
    </section>

    <section class="ai-preview" @click="goAiChat">
      <div class="section-title">
        <b>AI 助手</b>
        <button type="button" @click.stop="goAiChat">查看对话</button>
      </div>
      <div v-if="lastUserMsg || lastAiReply" class="ai-content">
        <div class="chat-lines">
          <p v-if="lastUserMsg">{{ lastUserMsg }}</p>
          <p v-if="lastAiReply" class="reply">{{ lastAiReply }}</p>
        </div>
        <article v-if="lastDraft?.costDraft" class="draft-mini" @click.stop="openAiDraft">
          <span>草稿</span>
          <b>{{ lastDraft.costDraft.styleName || '未命名' }}</b>
          <small>{{ lastDraft.costDraft.category || '' }}</small>
          <strong v-if="lastDraft.calculation?.suggestedPrice">¥{{ money(lastDraft.calculation.suggestedPrice) }}</strong>
          <button type="button" @click.stop="openAiDraft">编辑</button>
        </article>
      </div>
      <div v-else class="ai-empty">
        <span>还没有对话记录</span>
        <small>去 AI 助手聊聊吧</small>
      </div>
    </section>
  </div>
</template>

<style scoped>
.profile-page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 16px 18px;
  scrollbar-width: none;
  overscroll-behavior: contain;
}

.profile-page::-webkit-scrollbar {
  display: none;
}

.profile-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.shop-mark {
  display: grid;
  width: 58px;
  height: 58px;
  place-items: center;
  border-radius: 50%;
  color: #f0d188;
  background:
    radial-gradient(circle at 50% 20%, rgba(240, 209, 136, 0.16), transparent 34%),
    linear-gradient(145deg, #07110d, #0f3a2c);
  font-size: 19px;
  font-weight: 950;
}

.profile-head h2 {
  overflow: hidden;
  margin: 0;
  color: #101410;
  font-size: 24px;
  font-weight: 950;
  letter-spacing: -0.05em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-head span {
  display: block;
  margin-top: 6px;
  color: rgba(23, 32, 24, 0.58);
  font-size: 13px;
  font-weight: 750;
}

.member-strip {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; margin-bottom: 10px;
  border-radius: 14px; cursor: pointer;
  background: linear-gradient(145deg, #0d3326, #0a261c);
  border: 1px solid rgba(240,209,136,0.18);
}
.member-left { flex: 1; }
.member-strip span { color: #f0d188; font-size: 13px; font-weight: 900; }
.member-strip small { display: block; margin-top: 2px; color: rgba(255,243,220,0.55); font-size: 11px; font-weight: 700; }
.trial-badge { font-style: normal; font-size: 10px; color: #fff; background: #c0392b; padding: 2px 6px; border-radius: 4px; margin-left: 6px; }
.expire { color: rgba(255,243,220,0.4) !important; font-size: 10px !important; }
.arrow { color: rgba(255,243,220,0.35); font-size: 14px; font-style: normal; flex-shrink: 0; }
.arrow.trial { color: #f0d188; }

.profile-head button {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border: 1px solid rgba(45, 61, 49, 0.1);
  border-radius: 17px;
  color: #172018;
  background: rgba(255, 250, 241, 0.72);
  font-size: 20px;
}

.profile-page .archive-hero {
  display: block;
  flex: 0 0 auto;
  overflow: hidden;
  min-height: 0;
  padding: 16px 18px 12px;
  border: 1px solid rgba(240, 209, 136, 0.22);
  border-radius: 18px;
  color: #f8e6bd;
  background:
    radial-gradient(circle at 82% 22%, rgba(240, 209, 136, 0.18), transparent 28%),
    linear-gradient(145deg, #07110d, #0d3327 70%);
  box-shadow: 0 14px 28px rgba(14, 45, 34, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.profile-page .archive-hero > span {
  display: block;
  color: #bd8b39;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.profile-page .archive-hero h3 {
  display: block;
  max-width: 280px;
  margin: 10px 0 6px;
  color: #f9e8c3;
  font-size: 24px;
  font-weight: 750;
  line-height: 1.22;
  letter-spacing: -0.05em;
}

.profile-page .archive-hero p {
  display: block;
  max-width: 275px;
  margin: 0;
  color: rgba(251, 242, 223, 0.72);
  font-size: 12px;
  line-height: 1.45;
}

.archive-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 14px;
  overflow: hidden;
  border: 1px solid rgba(251, 242, 223, 0.18);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
}

.archive-stats article {
  display: flex;
  align-items: baseline;
  gap: 5px;
  padding: 9px 10px;
}

.archive-stats article + article {
  border-left: 1px solid rgba(251, 242, 223, 0.16);
}

.archive-stats small {
  color: rgba(251, 242, 223, 0.76);
  font-size: 11px;
  font-weight: 800;
}

.archive-stats b {
  color: #f0d188;
  font-size: 22px;
  font-weight: 650;
}

.archive-stats em {
  color: rgba(251, 242, 223, 0.72);
  font-size: 11px;
  font-style: normal;
}

.profile-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 10px 0;
}

.profile-stats article,
.search-strip,
.asset-panel,
.ai-preview {
  border: 1px solid rgba(45, 61, 49, 0.1);
  background: rgba(255, 250, 241, 0.76);
  box-shadow: 0 6px 18px rgba(31, 42, 30, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.68);
}

.profile-stats article {
  min-height: 90px;
  padding: 12px 14px;
  border-radius: 18px;
}

.profile-stats span,
.profile-stats small {
  color: rgba(23, 32, 24, 0.58);
  font-size: 12px;
  font-weight: 850;
}

.profile-stats b {
  display: block;
  margin-top: 8px;
  color: #101410;
  font-size: 30px;
  font-weight: 500;
  letter-spacing: -0.06em;
}

.profile-stats small {
  display: block;
  margin-top: 3px;
}

.search-strip {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  min-height: 46px;
  margin-bottom: 10px;
  padding: 0 10px 0 14px;
  border-radius: 16px;
  color: rgba(23, 32, 24, 0.42);
  font-size: 13px;
  font-weight: 800;
}

.search-strip button {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 0;
  border-radius: 10px;
  color: #71501f;
  background: rgba(189, 139, 57, 0.1);
}

.asset-panel,
.ai-preview {
  padding: 12px 14px;
  border-radius: 18px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-title b {
  color: #101410;
  font-size: 17px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.section-title button {
  min-height: 30px;
  border: 0;
  color: rgba(23, 32, 24, 0.52);
  background: transparent;
  font-size: 12px;
  font-weight: 850;
}

.asset-row {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  width: 100%;
  min-height: 64px;
  padding: 8px 0;
  border: 0;
  border-top: 1px solid rgba(45, 61, 49, 0.08);
  background: transparent;
  text-align: left;
}

.asset-row i {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 12px;
  color: #bd8b39;
  background:
    radial-gradient(circle at 30% 24%, rgba(255, 255, 255, 0.55), transparent 24%),
    linear-gradient(145deg, #dfd3b8, #596650);
  font-style: normal;
  font-size: 19px;
}

.asset-row span,
.asset-row b,
.asset-row small {
  display: block;
  min-width: 0;
}

.asset-row b {
  color: #101410;
  font-size: 15px;
  font-weight: 950;
}

.asset-row small {
  margin-top: 4px;
  color: rgba(23, 32, 24, 0.56);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.3;
}

.asset-row strong {
  color: #3b2b15;
  font-size: 14px;
  font-weight: 800;
  white-space: nowrap;
}

.ai-preview {
  margin-top: 10px;
  padding-bottom: 10px;
}

.ai-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 110px;
  gap: 8px;
  align-items: stretch;
}

.chat-lines {
  display: grid;
  align-content: center;
  gap: 6px;
}

.chat-lines p {
  margin: 0;
  padding: 8px 10px;
  border-radius: 12px;
  color: rgba(23, 32, 24, 0.76);
  background: rgba(238, 225, 199, 0.72);
  font-size: 11px;
  line-height: 1.4;
}

.chat-lines .reply {
  color: #fbf2df;
  background: linear-gradient(145deg, #0a3427, #07110d);
}

.draft-mini {
  display: grid;
  align-content: start;
  padding: 8px 10px;
  border: 1px solid rgba(189, 139, 57, 0.2);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.55);
}

.draft-mini span {
  width: fit-content;
  padding: 3px 8px;
  border-radius: 999px;
  color: #6f5528;
  background: rgba(189, 139, 57, 0.12);
  font-size: 10px;
  font-weight: 850;
}

.draft-mini b {
  margin-top: 8px;
  color: #101410;
  font-size: 12px;
}

.draft-mini small {
  margin-top: 6px;
  color: rgba(23, 32, 24, 0.56);
  font-size: 10px;
}

.draft-mini strong {
  margin-top: 2px;
  color: #101410;
  font-size: 20px;
  font-weight: 650;
}

.draft-mini button {
  min-height: 34px;
  margin-top: 8px;
  border: 0;
  border-radius: 10px;
  color: #07110d;
  background: var(--gold-gradient);
  font-size: 11px;
  font-weight: 950;
}

.ai-empty {
  padding: 16px 0;
  text-align: center;
  color: rgba(23,32,24,0.35);
}
.ai-empty span { display: block; font-size: 13px; font-weight: 700; }
.ai-empty small { display: block; margin-top: 4px; font-size: 11px; }

@media (max-width: 390px) {
  .profile-page {
    padding-inline: 14px;
  }

  .archive-hero h3 {
    font-size: 27px;
  }

  .ai-content {
    grid-template-columns: 1fr;
  }
}
</style>
