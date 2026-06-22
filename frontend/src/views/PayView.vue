<script setup lang="ts">
import { Close, Promotion, Service } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { getMembershipInfo, upgradePlan, http, getSupportChat, sendSupportMessage } from '../api/http'

const route = useRoute()
const router = useRouter()

const plan = computed(() => String(route.query.plan || 'pro'))
const billing = computed(() => String(route.query.billing || 'monthly'))

const prices: Record<string, Record<string, number>> = {
  pro: { monthly: 29, quarterly: 69, yearly: 279 },
  ultimate: { monthly: 69, quarterly: 169, yearly: 659 },
  style: { monthly: 10, quarterly: 10, yearly: 10 },
  ai: { monthly: 8, quarterly: 8, yearly: 8 },
  template: { monthly: 6, quarterly: 6, yearly: 6 },
}
const labels: Record<string, string> = { pro: '专业版', ultimate: '旗舰版', style: '款式+5', ai: 'AI+10次', template: '模板+2' }
const amount = computed(() => (prices[plan.value] || {})[billing.value] || 29)

// 支付方式
const payMethod = ref<'wechat' | 'alipay' | null>(null)
const showQR = ref(false)
const payMethods = ref<any[]>([])

const filteredMethods = computed(() => {
  if (!payMethod.value) return []
  const kw = payMethod.value === 'wechat' ? '微信' : '支付宝'
  return payMethods.value.filter((m: any) => m.name.includes(kw))
})

async function loadQR() {
  try {
    const res = await http.get('/auth/upgrade/')
    payMethods.value = res.data.methods || []
  } catch { /* */ }
}

function selectPay(m: 'wechat' | 'alipay') { payMethod.value = m; showQR.value = true; loadQR() }
function closeQR() { showQR.value = false }

// 客服聊天
const chatOpen = ref(false)
const chatMessages = ref<{ id: number; content: string; isStaff: boolean; createdAt: string }[]>([])
const chatInput = ref('')
const chatBody = ref<HTMLElement | null>(null)
let chatPollTimer: any = null
let lastChatId = 0

async function loadChat() {
  try {
    const r = await getSupportChat()
    chatMessages.value = r.messages || []
    if (chatMessages.value.length) {
      lastChatId = chatMessages.value[chatMessages.value.length - 1]?.id || 0
    }
    scrollChatBottom()
  } catch { /* */ }
}

async function pollChat() {
  try {
    const r = await getSupportChat()
    const msgs = r.messages || []
    const newMsgs = msgs.filter((m: any) => m.id > lastChatId)
    if (newMsgs.length) {
      chatMessages.value = [...chatMessages.value, ...newMsgs]
      lastChatId = newMsgs[newMsgs.length - 1].id
      scrollChatBottom()
    }
  } catch { /* */ }
}

function scrollChatBottom() {
  setTimeout(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  }, 100)
}

async function sendChat() {
  const t = chatInput.value.trim()
  if (!t) return
  chatInput.value = ''
  await sendSupportMessage(t)
  pollChat()
}

function toggleChat() {
  chatOpen.value = !chatOpen.value
  if (chatOpen.value) loadChat()
}

// 始终轮询，确保不漏消息
onMounted(() => {
  loadChat()
  chatPollTimer = setInterval(pollChat, 1500)
})
onUnmounted(() => clearInterval(chatPollTimer))

// 我已支付
const submitted = ref(false)
const subMsg = ref('')
async function confirmPay() {
  try {
    await upgradePlan({ plan: plan.value, billing: billing.value })
    submitted.value = true
    subMsg.value = '已提交，管理员确认后自动开通'
    chatOpen.value = true
  } catch (e: any) {
    subMsg.value = e?.response?.data?.detail || '提交失败'
  }
}

function goBack() { router.push({ name: 'membership' }) }
function goHome() { router.push({ name: 'home' }) }
</script>

<template>
  <div class="page">
    <header class="nav">
      <div><span class="hello">确认支付</span><h2>{{ labels[plan] || plan }}</h2></div>
      <button class="icon-btn" @click="goBack"><el-icon><Close /></el-icon></button>
    </header>

    <!-- 支付信息 -->
    <div class="pay-card">
      <div class="pay-amount">
        <span>应付金额</span>
        <strong>¥{{ amount }}</strong>
        <small>{{ labels[plan] }} · {{ billing === 'monthly' ? '月付' : billing === 'quarterly' ? '季付' : '年付' }}</small>
      </div>

      <div v-if="!submitted" class="pay-methods">
        <p>选择支付方式</p>
        <div class="method-grid">
          <button class="method wechat" :class="{ active: payMethod === 'wechat' }" @click="selectPay('wechat')">
            <span class="icon">💬</span>
            <b>微信支付</b>
          </button>
          <button class="method alipay" :class="{ active: payMethod === 'alipay' }" @click="selectPay('alipay')">
            <span class="icon">💙</span>
            <b>支付宝</b>
          </button>
        </div>
      </div>

      <div v-if="submitted" class="done-msg">{{ subMsg }}</div>

      <button v-if="!submitted" class="paid-btn" @click="confirmPay">
        我已支付，通知客服
      </button>
      <button v-else class="paid-btn done" @click="goHome">返回首页</button>
    </div>

    <!-- 客服聊天 -->
    <div class="chat-section" :class="{ open: chatOpen }">
      <div class="chat-header" @click="toggleChat">
        <el-icon><Service /></el-icon>
        <span>客服帮助</span>
        <small>{{ chatOpen ? '收起' : '展开' }}</small>
      </div>
      <div v-if="chatOpen" class="chat-box">
        <div ref="chatBody" class="chat-msgs">
          <div v-for="m in chatMessages" :key="m.id" :class="['msg', m.isStaff ? 'assistant' : 'user']">
            <small>{{ m.createdAt }}</small>
            {{ m.content }}
          </div>
        </div>
        <div class="chat-send">
          <input v-model="chatInput" placeholder="输入消息..." @keydown.enter="sendChat" />
          <button @click="sendChat"><el-icon><Promotion /></el-icon></button>
        </div>
      </div>
    </div>

    <!-- 二维码弹窗 -->
    <div v-if="showQR" class="qr-overlay" @click.self="closeQR">
      <div class="qr-modal">
        <h3>{{ payMethod === 'wechat' ? '微信扫码支付' : '支付宝扫码支付' }}</h3>
        <div v-if="filteredMethods.length">
          <div v-for="m in filteredMethods" :key="m.id">
            <img v-if="m.qr_image" :src="m.qr_image" class="qr-img" alt="收款码" />
            <p class="qr-name">{{ m.name }}</p>
          </div>
        </div>
        <div v-else class="qr-placeholder">
          <span>¥{{ amount }}</span>
          <small>请截图此金额，用{{ payMethod === 'wechat' ? '微信' : '支付宝' }}扫码转账</small>
        </div>
        <p class="qr-note">转账请备注手机号，完成后关闭本窗口点击「我已支付」</p>
        <button class="close-qr" @click="closeQR">关闭</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { position: absolute; inset: 0; display: flex; flex-direction: column; overflow: hidden; padding: 12px 14px 0; }
.nav { flex-shrink: 0; display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.hello { color: rgba(255,243,220,0.45); font-size: 11px; }
.nav h2 { color: #fff3dc; font-size: 21px; font-weight: 900; margin: 2px 0 0; }
.icon-btn { width: 34px; height: 34px; display: grid; place-items: center; border: 0; border-radius: 11px; color: #17120a; background: linear-gradient(145deg, #f3d891, #d3a24c); font-size: 14px; }

.pay-card { flex-shrink: 0; padding: 20px; border-radius: 18px; background: linear-gradient(160deg, #fffef9, #f5ecd6); text-align: center; margin-bottom: 10px; }
.pay-amount span { font-size: 12px; color: rgba(23,21,18,0.5); }
.pay-amount strong { display: block; font-size: 44px; font-weight: 950; color: #1a1812; line-height: 1.1; }
.pay-amount small { font-size: 12px; color: rgba(23,21,18,0.4); }

.pay-methods { margin-top: 18px; }
.pay-methods p { font-size: 12px; color: rgba(23,21,18,0.5); margin-bottom: 8px; }
.method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.method {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px; border: 2px solid rgba(189,139,57,0.15); border-radius: 14px;
  background: #fffdf7; cursor: pointer;
}
.method.active { border-color: #bd8b39; background: rgba(189,139,57,0.06); }
.method .icon { font-size: 28px; }
.method b { font-size: 13px; color: #1a1812; }

.paid-btn { width: 100%; height: 44px; margin-top: 16px; border: 0; border-radius: 12px; font-size: 14px; font-weight: 900; cursor: pointer; color: #1a1205; background: linear-gradient(145deg, #f3d891, #d3a24c); }
.paid-btn.done { background: #1a1f18; color: #fff; }
.done-msg { margin-top: 12px; padding: 10px; border-radius: 10px; font-size: 12px; font-weight: 800; color: #2b210f; background: linear-gradient(145deg, #f8daa0, #d2a657); }

/* 聊天 */
.chat-section { flex: 1; display: flex; flex-direction: column; min-height: 0; border-radius: 14px; overflow: hidden; background: rgba(20,25,20,0.85); border: 1px solid rgba(255,255,255,0.08); }
.chat-section.open { flex: 1; }
.chat-header { display: flex; align-items: center; gap: 6px; padding: 10px 12px; cursor: pointer; color: rgba(255,255,255,0.55); font-size: 12px; font-weight: 800; flex-shrink: 0; }
.chat-header small { margin-left: auto; font-size: 10px; color: rgba(255,255,255,0.3); }
.chat-box { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.chat-msgs { flex: 1; overflow-y: auto; padding: 8px 10px; display: grid; gap: 6px; align-content: start; scrollbar-width: none; }
.chat-msgs::-webkit-scrollbar { display: none; }
.msg { max-width: 85%; padding: 8px 12px; border-radius: 14px; font-size: 12px; line-height: 1.5; }
.msg.user { justify-self: end; color: #1a1205; background: linear-gradient(145deg, #f3d891, #d3a24c); }
.msg.assistant { color: #e8ddc8; background: rgba(255,255,255,0.1); }
.chat-send { display: flex; gap: 6px; padding: 8px 10px; border-top: 1px solid rgba(255,255,255,0.08); }
.chat-send input { flex: 1; height: 34px; padding: 0 10px; border: 0; border-radius: 17px; background: rgba(255,255,255,0.12); color: #f0e6ce; font-size: 12px; outline: 0; }
.chat-send button { width: 34px; height: 34px; border: 0; border-radius: 50%; background: linear-gradient(145deg, #f3d891, #d3a24c); color: #1a1205; display: grid; place-items: center; }

/* 二维码弹窗 */
.qr-overlay { position: fixed; inset: 0; z-index: 300; display: flex; align-items: center; justify-content: center; padding: 16px; background: rgba(0,0,0,0.7); }
.qr-modal { width: 100%; max-width: 340px; padding: 24px 20px; border-radius: 24px; background: #1e241e; text-align: center; color: #f0e6ce; }
.qr-modal h3 { margin: 0 0 16px; font-size: 18px; color: #f0d188; }
.qr-img { width: 240px; height: 240px; border-radius: 14px; margin: 0 auto; display: block; background: #fff; }
.qr-placeholder { padding: 30px 0; }
.qr-placeholder span { font-size: 36px; font-weight: 950; color: #f0d188; }
.qr-placeholder small { display: block; margin-top: 8px; font-size: 11px; color: rgba(255,255,255,0.4); }
.qr-note { font-size: 11px; color: rgba(255,255,255,0.4); margin: 10px 0; }
.qr-name { font-size: 11px; color: rgba(255,255,255,0.5); margin: 4px 0 0; }
.close-qr { height: 36px; padding: 0 20px; border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; background: transparent; color: rgba(255,255,255,0.5); font-size: 12px; }
</style>
