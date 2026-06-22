<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ArrowDown, Check, CopyDocument, Promotion, RefreshRight } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { costingChat, getAiChatHistory } from '../api/http'
import { money, useStore } from '../composables/useStore'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  text: string
  intent?: string
  costDraft?: any
  calculation?: any | null
  needMoreInfo?: boolean
  readyToSave?: boolean
}

const router = useRouter()
const { visibleStyles, saveAiStyle, saveSuccess, saveError } = useStore()

const inputText = ref('')
const isSending = ref(false)
const chatBody = ref<HTMLElement | null>(null)
const lastCostDraft = ref<any>({})
const copied = ref(false)
const savedTip = ref('')
const isStylePickerOpen = ref(false)
const selectedStyles = ref<number[]>([])
let messageId = 1

const messages = ref<ChatMessage[]>([
  {
    id: messageId++,
    role: 'assistant',
    text: '老板好！👋\n\n不选款式时，我是「建款助手」——直接说你想做什么衣服，我帮你从零建款。\n\n勾选款式后，我是「报价助手」——帮你算成本、改工艺、出报价。',
  },
])

const examples = ['帮我建一款牛仔外套', '这款开始算成本', '客户要 300 件', '加工费改成 7 块']

// 已选中的款式数据
const selectedStylesData = computed(() =>
  visibleStyles.value.filter(s => selectedStyles.value.includes(s.id))
)

function toggleStyle(id: number) {
  const idx = selectedStyles.value.indexOf(id)
  if (idx >= 0) selectedStyles.value.splice(idx, 1)
  else selectedStyles.value.push(id)
}

function isStyleSelected(id: number) {
  return selectedStyles.value.includes(id)
}

const importableStyles = computed(() => {
  const seen = new Set<string>()
  return visibleStyles.value
    .filter((style) => {
      const key = style.name.trim()
      if (!key || seen.has(key)) return false
      seen.add(key)
      return true
    })
})

const latestDraftMessage = computed(() =>
  [...messages.value].reverse().find((item) => item.role === 'assistant' && item.costDraft && !item.needMoreInfo),
)

function canShowDraftCard(message: ChatMessage) {
  return Boolean(
    message.role === 'assistant' &&
      message.costDraft &&
      !message.needMoreInfo &&
      (message.readyToSave || message.costDraft?._readyToSave),
  )
}

function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  })
}

function hasActiveDraftContext() {
  const d = lastCostDraft.value
  if (!d || Object.keys(d).length === 0) return false
  return Boolean(
    d._createRequested ||
    d._lastMissingField ||
    d.styleName ||
    (Array.isArray(d.fabrics) && d.fabrics.length > 0) ||
    (Array.isArray(d.processes) && d.processes.length > 0),
  )
}

function isTooVague(content: string) {
  if (hasActiveDraftContext()) return false
  return /^[\d\s.]+$/.test(content) || content.length < 2
}

async function loadChatHistory() {
  try {
    const history = await getAiChatHistory()
    if (!Array.isArray(history) || !history.length) return
    messages.value = history.map((item: any) => ({
      id: Number(item.id),
      role: item.role,
      text: item.text,
      intent: item.intent,
      costDraft: item.costDraft,
      calculation: item.calculation && Object.keys(item.calculation).length ? item.calculation : null,
      needMoreInfo: item.needMoreInfo,
      readyToSave: item.readyToSave ?? item.costDraft?._readyToSave,
    }))
    messageId = Math.max(...messages.value.map((item) => item.id)) + 1
    const latestDraft = [...messages.value].reverse().find((item) => item.costDraft && Object.keys(item.costDraft).length)
    lastCostDraft.value = latestDraft?.costDraft || {}
    scrollToBottom()
  } catch {
    // 历史记录加载失败不影响当前对话。
  }
}

async function sendMessage(text?: string) {
  const content = (text || inputText.value).trim()
  if (!content || isSending.value) return

  messages.value.push({ id: messageId++, role: 'user', text: content })
  inputText.value = ''
  copied.value = false
  savedTip.value = ''
  const hasStyles = selectedStyles.value.length > 0
  const hasDraft = hasActiveDraftContext()

  // 用户要切换模式/取消建款
  const cancelKeywords = /算了|不建了|不要了|取消|换个|重新|别建了|别管了|停下|不用了|切换|换一个|算报价|算成本|先不算|先别|等等/
  if (hasDraft && !hasStyles && cancelKeywords.test(content)) {
    lastCostDraft.value = {}
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: '好的老板，刚才的建款先放一边。你想做什么？勾选款式算报价，还是重新建个新款？',
    })
    scrollToBottom()
    return
  }

  // 用户有草稿但想切换到算报价模式（且勾选了款式）
  const quoteKeywords = /算报价|算成本|报个价|多少钱|什么价/
  if (hasDraft && hasStyles && quoteKeywords.test(content)) {
    // 放弃当前草稿，用勾选的款式来算
    lastCostDraft.value = {}
    // 不 return，继续往下走到 API
  }

  // 没有勾选款式也没有草稿 → 要算成本就先提示
  const costKeywords = /算成本|算报价|报价|成本|多少钱|什么价|算一下|算算|计算/
  if (costKeywords.test(content) && !hasStyles && !hasDraft) {
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: '老板，你还没选款式也没在建款中。要不先在上面勾选要算的款式，或者直接告诉我「帮我建一款xxx」我从零帮你建。',
      needMoreInfo: true,
    })
    scrollToBottom()
    return
  }

  if (isTooVague(content)) {
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: '老板，只发数字我判断不了是款式、数量还是价格。你可以说：帮我建一款牛仔外套，或者这款面料 26 一公斤。',
      needMoreInfo: true,
    })
    scrollToBottom()
    return
  }
  isSending.value = true
  scrollToBottom()

  try {
    const payload = await costingChat({
      message: content,
      context: {
        lastCostDraft: lastCostDraft.value,
        hasSelectedStyles: selectedStyles.value.length > 0,
        selectedStyles: selectedStylesData.value.map((style) => ({
          name: style.name,
          category: style.category,
          fabrics: style.fabrics,
          processes: style.processes,
          accessoryPack: style.accessoryPack,
          expectedProfit: style.expectedProfit,
          quantity: 100,
        })),
        recentMessages: messages.value.slice(-12).map((item) => ({
          role: item.role,
          text: item.text,
          intent: item.intent,
          needMoreInfo: item.needMoreInfo,
        })),
        existingStyles: selectedStylesData.value.map((style) => ({
          name: style.name,
          category: style.category,
          fabrics: style.fabrics,
          processes: style.processes,
          accessoryPack: style.accessoryPack,
          expectedProfit: style.expectedProfit,
          quantity: 100,
        })),
      },
    })
    // 如果后端返回了计算结果（而非继续建款），清掉草稿
    if (payload.calculation && Object.keys(payload.calculation).length) {
      lastCostDraft.value = {}
    } else {
      lastCostDraft.value = payload.costDraft || {}
    }
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: payload.reply,
      intent: payload.intent,
      costDraft: payload.costDraft,
      calculation: payload.calculation,
      needMoreInfo: payload.needMoreInfo,
      readyToSave: payload.readyToSave ?? payload.costDraft?._readyToSave,
    })
  } catch (error: any) {
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: error?.response?.data?.detail || '老板，刚才没处理成功。你再发一次，或者检查一下网络和登录状态。',
    })
  } finally {
    isSending.value = false
    scrollToBottom()
  }
}

function styleToDraft(style: any) {
  return {
    styleName: style.name,
    category: style.category,
    fabrics: style.fabrics || [],
    processes: style.processes || [],
    accessoryPack: style.accessoryPack || 2.2,
    expectedProfit: style.expectedProfit || null,
    quantity: 100,
  }
}

async function saveAsStyle(message: ChatMessage) {
  if (!message.costDraft) return
  const saved = await saveAiStyle(message.costDraft, message.calculation || {})
  if (saved && saveSuccess.value) {
    savedTip.value = '已保存到首页款式档案'
    router.push({ name: 'home' })
  }
}

function continueEdit(message?: ChatMessage) {
  if (message?.calculation) {
    inputText.value = '加工费改成 '
    return
  }
  inputText.value = '这款开始算成本，面料 '
}

async function copyDraft(message: ChatMessage) {
  if (!message.costDraft) return
  const draft = message.costDraft
  const calc = message.calculation
  const text = calc
    ? `${draft.styleName || '这款'}：单件成本约 ${calc.singleCost} 元，建议报价 ${calc.suggestedPrice} 元，最低接单价 ${calc.minimumPrice} 元。`
    : `${draft.styleName || '这款'}：品类 ${draft.category || '未确定'}，已建立款式草稿，后面可继续补成本。`
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
  } catch {
    copied.value = false
  }
}

function lossText(draft: any) {
  const rate = draft?.fabrics?.[0]?.lossRate ?? 0.05
  return `${money(Number(rate) * 100)}%`
}

onMounted(() => {
  loadChatHistory()
})
</script>

<template>
  <div class="ai-page">
    <header class="ai-header">
      <div>
        <span>会建款、会记账、会算价</span>
        <h2>AI 智能助手</h2>
        <p>像发微信一样说，帮你把款式和成本记清楚</p>
      </div>
      <strong>AI</strong>
    </header>

    <section v-if="importableStyles.length" class="import-strip">
      <button class="import-toggle" type="button" @click="isStylePickerOpen = !isStylePickerOpen">
        <span>{{ selectedStyles.length ? '已选 ' + selectedStyles.length + ' 款' : '选择已有款式' }}</span>
        <b>{{ importableStyles.length }} 款</b>
        <el-icon :class="{ open: isStylePickerOpen }"><ArrowDown /></el-icon>
      </button>
      <div v-if="isStylePickerOpen" class="style-picker">
        <button
          v-for="style in importableStyles"
          :key="style.id"
          class="style-option"
          :class="{ checked: isStyleSelected(style.id) }"
          type="button"
          @click.stop="toggleStyle(style.id)"
        >
          <span class="check-mark">{{ isStyleSelected(style.id) ? '✓' : '' }}</span>
          {{ style.name }}
        </button>
      </div>
    </section>

    <section ref="chatBody" class="chat-body">
      <article v-for="message in messages" :key="message.id" :class="['message', message.role]">
        <div class="bubble">
          <p>{{ message.text }}</p>
        </div>

        <div v-if="canShowDraftCard(message)" class="draft-card">
          <div class="card-head">
            <div>
              <span>{{ message.calculation ? '确认保存' : '款式资料' }}</span>
              <b>{{ message.costDraft?.styleName || '未命名款式' }}</b>
            </div>
            <strong>{{ message.costDraft?.category || '未确定' }}</strong>
          </div>

          <div v-if="!message.calculation" class="draft-info">
            <div>
              <span>最后一步</span>
              <b>资料已经整理好，确认后保存</b>
            </div>
            <p>保存后会进入首页款式档案，后面可以继续补成本和报价。</p>
          </div>

          <template v-else>
            <div class="cost-grid">
              <div>
                <span>面料成本</span>
                <b>¥{{ money(message.calculation.fabricCost) }}</b>
              </div>
              <div>
                <span>加工成本</span>
                <b>¥{{ money(message.calculation.processCost) }}</b>
              </div>
              <div>
                <span>辅料包装</span>
                <b>¥{{ money(message.calculation.accessoryCost) }}</b>
              </div>
              <div>
                <span>损耗</span>
                <b>{{ lossText(message.costDraft) }}</b>
              </div>
              <div>
                <span>单件成本</span>
                <b>¥{{ money(message.calculation.singleCost) }}</b>
              </div>
              <div>
                <span>建议报价</span>
                <b>¥{{ money(message.calculation.suggestedPrice) }}</b>
              </div>
              <div>
                <span>最低接单价</span>
                <b>¥{{ money(message.calculation.minimumPrice) }}</b>
              </div>
              <div>
                <span>单件利润</span>
                <b>¥{{ money(message.calculation.singleProfit) }}</b>
              </div>
            </div>

            <div class="profit-row">
              <div>
                <span>100 件预计利润</span>
                <b>¥{{ money(message.calculation.profitFor100) }}</b>
              </div>
              <div>
                <span>500 件预计利润</span>
                <b>¥{{ money(message.calculation.profitFor500) }}</b>
              </div>
            </div>
          </template>

          <div class="card-actions">
            <button :disabled="message.needMoreInfo" type="button" @click="saveAsStyle(message)">
              <el-icon><Check /></el-icon>
              保存为款式
            </button>
            <button type="button" @click="continueEdit(message)">
              <el-icon><RefreshRight /></el-icon>
              {{ message.calculation ? '继续修改' : '继续补充' }}
            </button>
            <button type="button" @click="copyDraft(message)">
              <el-icon><CopyDocument /></el-icon>
              {{ message.calculation ? '复制报价' : '复制款式' }}
            </button>
          </div>
        </div>
      </article>

      <div v-if="isSending" class="typing">AI 正在帮你整理...</div>
      <div v-if="saveError" class="save-error">{{ saveError }}</div>
      <div v-if="savedTip" class="save-ok">{{ savedTip }}</div>
      <div v-if="copied" class="save-ok">已复制</div>
    </section>

    <footer class="chat-input">
      <div class="quick-examples">
        <button v-for="item in examples" :key="item" type="button" @click="sendMessage(item)">{{ item }}</button>
      </div>
      <div class="input-box">
        <textarea
          v-model="inputText"
          rows="1"
          placeholder="说点什么..."
          @keydown.enter.prevent="sendMessage()"
        />
        <button :disabled="isSending || !inputText.trim()" type="button" @click="sendMessage()">
          <el-icon><Promotion /></el-icon>
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.ai-page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── 头部 ── */
.ai-header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 14px 6px;
}

.ai-header span { color: rgba(255,243,220,0.5); font-size: 11px; font-weight: 800; }
.ai-header h2 { margin: 2px 0 0; color: #fff3dc; font-size: 21px; line-height: 1.1; font-weight: 900; }
.ai-header p { margin: 0; color: rgba(255,243,220,0.68); font-size: 12px; font-weight: 700; }

.ai-header strong {
  display: grid;
  width: 40px; height: 40px;
  place-items: center;
  border-radius: 14px;
  color: #17120a;
  background: linear-gradient(145deg, #ffe4a8, #b88335);
  box-shadow: 0 8px 20px rgba(188,132,50,0.25);
  font-size: 16px;
}

/* ── 导入条 ── */
.import-strip { flex: 0 0 auto; margin: 0 16px 8px; position: relative; z-index: 20; }
.import-toggle {
  display: flex; align-items: center; gap: 6px;
  width: 100%; min-height: 38px; padding: 0 12px;
  border: 1px solid rgba(231,202,139,0.3); border-radius: 14px;
  color: #f6d796; background: rgba(20, 25, 18, 0.85);
  font-size: 12px; font-weight: 800;
}
.import-toggle b { color: #f6d796; font-size: 11px; margin-left: auto; }
.import-toggle .el-icon { transition: transform 180ms ease; }
.import-toggle .el-icon.open { transform: rotate(180deg); }

.style-picker {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
  position: absolute; top: 42px; left: 0; right: 0; z-index: 30;
  max-height: 180px; overflow-y: auto; padding: 6px;
  border-radius: 14px; border: 1px solid rgba(231,202,139,0.18);
  background: linear-gradient(145deg, #1a1f18, #242a20);
  box-shadow: 0 14px 36px rgba(0,0,0,0.4);
  scrollbar-width: none;
}
.style-picker::-webkit-scrollbar { display: none; }
.style-option {
  display: flex; align-items: center; gap: 6px;
  min-height: 34px; padding: 0 10px; border: 1px solid rgba(231,202,139,0.2); border-radius: 10px;
  color: #e8d5a8; background: rgba(255,255,255,0.06);
  font-size: 11px; font-weight: 800; text-overflow: ellipsis; white-space: nowrap;
  transition: background 120ms ease;
}
.style-option.checked {
  color: #17120a;
  background: linear-gradient(145deg, #ffe4a8, #b88335);
  border-color: transparent;
}
.check-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; border-radius: 5px;
  border: 1.5px solid rgba(231,202,139,0.4);
  font-size: 11px; flex-shrink: 0;
  background: transparent; color: transparent;
}
.style-option.checked .check-mark {
  background: rgba(0,0,0,0.2);
  border-color: transparent;
  color: #fff;
}

/* ── 聊天区 ── */
.chat-body {
  flex: 1; min-height: 0; overflow-y: auto;
  padding: 4px 12px 4px;
  scrollbar-width: none;
}
.chat-body::-webkit-scrollbar { display: none; }

.message { display: grid; gap: 4px; margin-bottom: 12px; }
.message.user { justify-items: end; }

.bubble {
  max-width: 84%; padding: 10px 14px; border-radius: 18px;
  font-size: 13px; line-height: 1.55; white-space: pre-line;
}
.bubble p { margin: 0; }

.assistant .bubble {
  color: #1a1812;
  background: linear-gradient(145deg, #fefdf7, #f3ead5);
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.user .bubble {
  color: #17120a;
  background: linear-gradient(145deg, #f5d388, #c89235);
  border-bottom-right-radius: 6px;
  font-weight: 850;
  box-shadow: 0 2px 8px rgba(180,120,40,0.2);
}

/* ── 款式卡片 ── */
.draft-card {
  width: min(280px, 86%);
  padding: 10px; border-radius: 16px;
  color: #17130c;
  background: linear-gradient(145deg, #fffef8, #f0e6ce);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.6);
}
.assistant .draft-card { justify-self: start; }

.card-head { display: grid; grid-template-columns: minmax(0,1fr) auto; align-items: start; gap: 4px; margin-bottom: 6px; }
.card-head span, .cost-grid span, .profit-row span, .draft-info span { color: rgba(23,19,12,0.45); font-size: 10px; font-weight: 800; }
.card-head b { font-size: 14px; font-weight: 950; }
.card-head strong { padding: 4px 8px; border-radius: 999px; color: #ffe9b8; background: #1a1c16; font-size: 10px; }

.draft-info { padding: 8px; border-radius: 12px; background: rgba(255,255,255,0.6); margin-bottom: 4px; }
.draft-info b { font-size: 13px; }
.draft-info p { margin: 4px 0 0; color: rgba(23,19,12,0.55); font-size: 11px; line-height: 1.4; }

.cost-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 4px; }
.cost-grid div, .profit-row div { padding: 6px; border: 1px solid rgba(0,0,0,0.06); border-radius: 10px; background: rgba(255,255,255,0.6); }
.cost-grid b { color: #050505; font-size: 13px; font-weight: 900; margin-top: 2px; }
.profit-row { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.profit-row b { color: #050505; font-size: 13px; margin-top: 2px; }

.card-actions { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
.card-actions button {
  display: inline-flex; align-items: center; justify-content: center; gap: 3px;
  min-height: 34px; border: 0; border-radius: 10px;
  color: #ffe9b8;
  background: linear-gradient(145deg, #1a1f18, #242a20);
  font-size: 10px; font-weight: 800;
}
.card-actions button:first-child {
  color: #17120a;
  background: linear-gradient(145deg, #f3d891, #d3a24c);
}

/* ── 状态提示 ── */
.typing, .save-error, .save-ok {
  width: fit-content; max-width: 90%; margin: 6px auto; padding: 7px 12px;
  border-radius: 999px; font-size: 11px; font-weight: 800;
}
.typing, .save-ok { color: #2b210f; background: linear-gradient(145deg, #f8daa0, #d2a657); }
.save-error { color: #6f1d1b; background: #ffe0d8; }

/* ── 输入区 ── */
.chat-input {
  flex: 0 0 auto; z-index: 25;
  margin: 4px 10px 6px;
  padding: 8px 10px 8px;
  border-radius: 20px;
  background: rgba(20,26,20,0.85);
  border: 0.5px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(8px);
}

.quick-examples {
  display: flex; gap: 5px; overflow-x: auto;
  margin-bottom: 6px;
  scrollbar-width: none;
}
.quick-examples button {
  flex-shrink: 0; height: 22px; padding: 0 9px;
  font-size: 10px; font-weight: 700;
  color: rgba(212,184,108,0.7);
  background: rgba(255,255,255,0.04);
  border: 0.5px solid rgba(255,255,255,0.08);
  border-radius: 11px;
  white-space: nowrap;
}

.input-box {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 5px 5px 14px;
  background: rgba(255,255,255,0.06);
  border: 0.5px solid rgba(255,255,255,0.1);
  border-radius: 22px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.input-box textarea {
  flex: 1; min-height: 20px; max-height: 44px;
  padding: 0; margin: 0;
  border: 0; outline: 0; resize: none; overflow: hidden;
  background: transparent; color: #ede3cc;
  font-size: 13px; font-weight: 700; line-height: 20px;
  caret-color: #d3a24c;
  -webkit-appearance: none; box-shadow: none;
}
.input-box textarea::placeholder { color: rgba(255,243,220,0.18); }

.input-box button {
  width: 32px; height: 32px; flex-shrink: 0; border: 0;
  display: grid; place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0d080, #c8963a);
  box-shadow: 0 2px 8px rgba(180,120,40,0.3);
  color: #1a1205; font-size: 14px;
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.input-box button:not(:disabled):active {
  transform: scale(0.92);
  box-shadow: 0 1px 4px rgba(180,120,40,0.2);
}
.input-box button:disabled { opacity: 0.3; box-shadow: none; }
</style>
