<script setup lang="ts">
import { Promotion, User } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted, ref } from 'vue'
import {
  getSupportPayments, confirmPayment, getMe, http,
  getSupportRooms, getStaffRoomChat, sendStaffMessage,
} from '../api/http'

const router = useRouter()
const tab = ref<'payments' | 'chats' | 'members'>('payments')
const payments = ref<any[]>([])
const rooms = ref<any[]>([])
const members = ref<any[]>([])
const activeRoom = ref<any>(null)
const chatMessages = ref<any[]>([])
const chatInput = ref('')
const chatBody = ref<HTMLElement | null>(null)
const lastMsgId = ref(0)
let pollTimer: any = null

// 付款
async function loadPayments() { try { const r = await getSupportPayments(); payments.value = r.payments || [] } catch { /* */ } }
async function doConfirm(id: number) { await confirmPayment(id); loadPayments() }

// 聊天
async function loadRooms() { try { const r = await getSupportRooms(); rooms.value = r.rooms || [] } catch { /* */ } }
async function openRoom(room: any) {
  activeRoom.value = room; lastMsgId.value = 0
  try { const r = await getStaffRoomChat(room.id); chatMessages.value = r.messages || []
    if (chatMessages.value.length) lastMsgId.value = chatMessages.value[chatMessages.value.length - 1]?.id || 0
  } catch { /* */ }
  setTimeout(() => { if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight }, 100)
}
async function pollRoom() {
  if (!activeRoom.value) return
  try {
    const r = await getStaffRoomChat(activeRoom.value.id); const msgs = r.messages || []
    const news = msgs.filter((m: any) => m.id > lastMsgId.value)
    if (news.length) { chatMessages.value = [...chatMessages.value, ...news]; lastMsgId.value = news[news.length - 1].id
      setTimeout(() => { if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight }, 100) }
  } catch { /* */ }
}
async function sendMsg() {
  const t = chatInput.value.trim(); if (!t || !activeRoom.value) return
  chatInput.value = ''; await sendStaffMessage(activeRoom.value.id, t); pollRoom()
}

// 会员管理
async function loadMembers() { try { const r = await http.get('/auth/support/members/'); members.value = r.data.members || [] } catch { /* */ } }
async function setPlan(id: number, plan: string) { await http.post('/auth/support/members/', { id, plan }); loadMembers() }

function goLogout() { localStorage.removeItem('garment_token'); router.replace({ name: 'cs-login' }) }

onMounted(async () => {
  try { const me = await getMe(); if (!me.is_staff) { localStorage.removeItem('garment_token'); router.replace({ name: 'cs-login' }); return } } catch { router.replace({ name: 'cs-login' }); return }
  loadPayments(); loadRooms(); loadMembers()
  pollTimer = setInterval(() => { loadPayments(); loadRooms(); pollRoom() }, 1500)
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<template>
  <div class="dashboard">
    <header class="topbar"><h2>客服后台</h2><button @click="goLogout">退出</button></header>
    <div class="tabs">
      <button :class="{ active: tab === 'payments' }" @click="tab = 'payments'">待确认 ({{ payments.length }})</button>
      <button :class="{ active: tab === 'chats' }" @click="tab = 'chats'">聊天 ({{ rooms.length }})</button>
      <button :class="{ active: tab === 'members' }" @click="tab = 'members'">会员 ({{ members.length }})</button>
    </div>

    <div v-if="tab === 'payments'" class="panel">
      <div v-if="!payments.length" class="empty">暂无</div>
      <div v-for="p in payments" :key="p.id" class="pay-row">
        <div class="pay-info">
          <b>{{ p.tenant }}</b><span>{{ p.plan }}{{ p.extension ? ' · '+p.extension : '' }}</span>
          <strong>{{ p.amount }}</strong><small>{{ p.createdAt }}</small>
        </div>
        <button class="confirm" @click="doConfirm(p.id)">确认到账</button>
      </div>
    </div>

    <div v-if="tab === 'chats'" class="chat-layout">
      <div class="room-list">
        <div v-if="!rooms.length" class="empty">暂无</div>
        <button v-for="r in rooms" :key="r.id" class="room-item" :class="{ active: activeRoom?.id === r.id }" @click="openRoom(r)">
          <el-icon><User /></el-icon><div><b>{{ r.tenant }}</b><small>{{ r.user }} · {{ r.updatedAt }}</small></div>
        </button>
      </div>
      <div class="chat-main">
        <div v-if="!activeRoom" class="empty">选择聊天室</div>
        <template v-else>
          <div class="chat-title">{{ activeRoom.tenant }}</div>
          <div ref="chatBody" class="chat-body">
            <div v-for="m in chatMessages" :key="m.id" :class="['bubble', m.isStaff ? 'staff' : 'user']">
              <small>{{ m.createdAt }}</small><p>{{ m.content }}</p>
            </div>
          </div>
          <div class="chat-send"><input v-model="chatInput" placeholder="回复..." @keydown.enter="sendMsg" /><button @click="sendMsg"><el-icon><Promotion /></el-icon></button></div>
        </template>
      </div>
    </div>

    <div v-if="tab === 'members'" class="panel">
      <div v-for="m in members" :key="m.id" class="member-row">
        <div class="mem-info">
          <b>{{ m.name }}</b><small>{{ m.owner }} · 注册 {{ m.createdAt }}</small>
          <span class="plan-tag" :class="m.planKey">{{ m.plan }}</span>
          <em v-if="m.trialInfo" class="trial-tag">{{ m.trialInfo }}</em>
        </div>
        <select :value="m.planKey" @change="setPlan(m.id, ($event.target as HTMLSelectElement).value)">
          <option value="free">免费版</option>
          <option value="pro">专业版</option>
          <option value="ultimate">旗舰版</option>
        </select>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard { position: fixed; inset: 0; display: flex; flex-direction: column; background: #f5f0e5; color: #1a1812; font-size: 13px; }
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #1a1f18; color: #f0d188; }
.topbar h2 { margin: 0; font-size: 17px; }
.topbar button { height: 32px; padding: 0 14px; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; background: transparent; color: #fff; font-size: 12px; }
.tabs { display: flex; }
.tabs button { flex: 1; height: 38px; border: 0; background: #e8e0d0; color: #5a4a30; font-size: 12px; font-weight: 800; }
.tabs button.active { background: #fff; color: #1a1812; border-bottom: 2px solid #bd8b39; }
.panel { flex: 1; overflow-y: auto; padding: 10px; }
.pay-row, .member-row { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 6px; border-radius: 12px; background: #fff; }
.pay-info, .mem-info { flex: 1; }
.pay-info b, .mem-info b { font-size: 13px; display: block; }
.pay-info span, .mem-info small { font-size: 11px; color: #8a6425; display: block; }
.pay-info strong { font-size: 16px; color: #c0392b; }
.pay-info small { color: #999; font-size: 10px; }
.confirm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #27ae60; color: #fff; font-size: 11px; font-weight: 800; }
.plan-tag { display: inline-block; font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #e8e0d0; color: #5a4a30; font-weight: 800; margin-top: 2px; }
.plan-tag.ultimate { background: #f0d188; color: #3d2a0a; }
.plan-tag.pro { background: #d4c8a0; color: #3d2a0a; }
.trial-tag { font-size: 10px; color: #c0392b; font-weight: 800; font-style: normal; }
select { height: 32px; padding: 0 8px; border: 1px solid #ddd; border-radius: 8px; font-size: 12px; }
.chat-layout { flex: 1; display: grid; grid-template-columns: 160px 1fr; min-height: 0; }
.room-list { overflow-y: auto; border-right: 1px solid #e0d8c8; background: #faf5ec; }
.room-item { display: flex; align-items: center; gap: 8px; width: 100%; padding: 10px 8px; border: 0; border-bottom: 1px solid #e8e0d0; background: transparent; text-align: left; cursor: pointer; }
.room-item.active { background: #fff; }
.room-item b { font-size: 11px; display: block; }
.room-item small { font-size: 10px; color: #999; }
.chat-main { display: flex; flex-direction: column; min-height: 0; }
.chat-title { padding: 8px 12px; font-weight: 900; border-bottom: 1px solid #e8e0d0; background: #fff; }
.chat-body { flex: 1; overflow-y: auto; padding: 10px; display: grid; gap: 8px; align-content: start; }
.bubble { max-width: 80%; padding: 8px 12px; border-radius: 12px; font-size: 12px; line-height: 1.5; }
.bubble small { font-size: 9px; color: #999; display: block; margin-bottom: 2px; }
.bubble p { margin: 0; }
.bubble.user { justify-self: end; background: #e8e0d0; }
.bubble.staff { justify-self: start; background: #d4e8d0; }
.chat-send { display: flex; gap: 6px; padding: 8px 10px; border-top: 1px solid #e8e0d0; background: #fff; }
.chat-send input { flex: 1; height: 34px; padding: 0 10px; border: 1px solid #ddd; border-radius: 17px; outline: 0; }
.chat-send button { width: 34px; height: 34px; border: 0; border-radius: 50%; background: #1a1f18; color: #f0d188; display: grid; place-items: center; }
.empty { text-align: center; padding: 40px; color: #999; }
</style>
