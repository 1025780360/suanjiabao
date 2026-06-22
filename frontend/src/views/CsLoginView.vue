<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginAccount } from '../api/http'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await loginAccount({ username: username.value.trim(), password: password.value })
    localStorage.setItem('garment_token', res.token)
    if (res.user?.is_staff) {
      router.replace({ name: 'support' })
    } else {
      error.value = '此账号不是客服账号，无法登录客服后台'
      localStorage.removeItem('garment_token')
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '登录失败'
  }
  loading.value = false
}
</script>

<template>
  <div class="shell">
    <div class="card">
      <h1>客服后台</h1>
      <p>仅限客服账号登录</p>
      <input v-model="username" placeholder="客服账号" autocomplete="username" @keydown.enter="login" />
      <input v-model="password" type="password" placeholder="密码" autocomplete="current-password" @keydown.enter="login" />
      <div v-if="error" class="err">{{ error }}</div>
      <button :disabled="loading" @click="login">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.shell { display: grid; place-items: center; min-height: 100vh; background: #1a1f18; padding: 20px; }
.card { width: 100%; max-width: 320px; display: grid; gap: 10px; padding: 24px; border-radius: 16px; background: #2a3028; box-shadow: 0 12px 32px rgba(0,0,0,0.3); }
h1 { margin: 0; color: #f0d188; font-size: 22px; text-align: center; }
p { margin: 0; color: rgba(255,255,255,0.4); font-size: 12px; text-align: center; }
input { height: 44px; padding: 0 12px; border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; background: rgba(255,255,255,0.06); color: #fff; font-size: 14px; outline: 0; }
input::placeholder { color: rgba(255,255,255,0.25); }
button { height: 44px; border: 0; border-radius: 10px; background: linear-gradient(145deg, #f3d891, #d3a24c); color: #1a1205; font-size: 14px; font-weight: 900; cursor: pointer; }
button:disabled { opacity: 0.5; }
.err { padding: 8px 10px; border-radius: 8px; background: #4a1a1a; color: #e07060; font-size: 12px; }
</style>
