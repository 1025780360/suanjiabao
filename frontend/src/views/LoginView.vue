<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../composables/useStore'

const router = useRouter()
const { authMode, authError, authForm, submitAuth, resetAuthForm } = useStore()
const submitting = ref(false)
const isRegister = ref(authMode.value === 'register')

// 验证码
const captchaCode = ref('')
const captchaInput = ref('')
const captchaError = ref('')
function generateCaptcha() {
  captchaCode.value = String(Math.floor(1000 + Math.random() * 9000))
  captchaInput.value = ''
  captchaError.value = ''
}
generateCaptcha()

function validate(): boolean {
  captchaError.value = ''

  // 手机号（登录和注册都需要）
  const phone = authForm.username.trim()
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    captchaError.value = '请输入正确的11位中国手机号'
    return false
  }

  // 密码
  const pwd = authForm.password
  if (pwd.length < 6 || pwd.length > 20) {
    captchaError.value = '密码需要6-20位'
    return false
  }
  if (!/[a-zA-Z]/.test(pwd)) {
    captchaError.value = '密码必须包含字母'
    return false
  }
  if (!/[0-9]/.test(pwd)) {
    captchaError.value = '密码必须包含数字'
    return false
  }
  if (/[^a-zA-Z0-9]/.test(pwd)) {
    captchaError.value = '密码不允许使用特殊符号'
    return false
  }

  // 验证码
  if (captchaInput.value !== captchaCode.value) {
    captchaError.value = '验证码错误，请重新输入'
    generateCaptcha()
    return false
  }
  return true
}

function toggleMode() {
  resetAuthForm()
  captchaError.value = ''
  generateCaptcha()
  isRegister.value = !isRegister.value
  authMode.value = isRegister.value ? 'register' : 'login'
}

async function handleSubmit() {
  if (submitting.value) return
  if (!validate()) return
  submitting.value = true
  await submitAuth()
  submitting.value = false
  if (localStorage.getItem('garment_token')) {
    router.replace({ name: 'home' })
  }
}
</script>

<template>
  <div class="login-shell">
    <div class="brand">
      <div class="logo">衣</div>
      <h1>算价宝</h1>
      <p>广州档口老板的服装成本报价工具</p>
    </div>

    <form class="form-card" @submit.prevent="handleSubmit">
      <!-- 手机号 -->
      <div class="form-group">
        <input v-model.trim="authForm.username"
          type="tel" inputmode="numeric" maxlength="11"
          placeholder="手机号" autocomplete="tel" />
      </div>

      <!-- 密码 -->
      <div class="form-group">
        <input v-model="authForm.password"
          :autocomplete="isRegister ? 'new-password' : 'current-password'"
          type="password" placeholder="密码（字母+数字，6-20位）" />
      </div>

      <!-- 注册额外字段 -->
      <template v-if="isRegister">
        <div class="form-group">
          <input v-model.trim="authForm.displayName" placeholder="你的称呼，如：张老板" />
        </div>
        <div class="form-group">
          <input v-model.trim="authForm.shopName" placeholder="店铺名称，如：锦禾服装报价室" />
        </div>
      </template>

      <!-- 验证码 -->
      <div class="captcha-row">
        <input v-model="captchaInput" type="text" inputmode="numeric" maxlength="4"
          placeholder="验证码" autocomplete="off" />
        <button type="button" class="captcha-box" @click="generateCaptcha">
          {{ captchaCode }}
        </button>
      </div>

      <div v-if="captchaError" class="error-msg">{{ captchaError }}</div>
      <div v-if="authError && !captchaError" class="error-msg">{{ authError }}</div>

      <button class="submit-btn" type="submit" :disabled="submitting">
        {{ submitting ? '处理中...' : isRegister ? '注册并进入' : '登录' }}
      </button>
    </form>

    <button class="switch-btn" type="button" @click="toggleMode">
      {{ isRegister ? '已有账号，去登录' : '没有账号？注册一个' }}
    </button>
  </div>
</template>

<style scoped>
.login-shell {
  display: flex; flex-direction: column; align-items: center;
  min-height: 100%; padding: 20px 20px 30px;
  gap: 16px;
  overflow-y: auto;
}
.brand { text-align: center; flex-shrink: 0; }
.logo {
  display: inline-grid; width: 50px; height: 50px; place-items: center; border-radius: 16px;
  color: #161006; background: linear-gradient(145deg, #f3d891, #d3a24c);
  box-shadow: 0 8px 22px rgba(180,120,40,0.25); font-size: 22px; font-weight: 950;
  margin-bottom: 10px;
}
.brand h1 { margin: 0; color: #fff6e0; font-size: 26px; font-weight: 950; }
.brand p { margin: 2px 0 0; color: rgba(255,246,224,0.45); font-size: 12px; font-weight: 700; }

.form-card {
  width: 100%; max-width: 320px; display: grid; gap: 8px; padding: 16px;
  border-radius: 18px; background: linear-gradient(160deg, #fffef9, #f5ecd6);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  flex-shrink: 0;
}
.form-group input {
  width: 100%; height: 42px; padding: 0 12px;
  border: 1.5px solid rgba(189,139,57,0.3); border-radius: 10px; outline: 0;
  background: #fffdf7; color: #1a1812; font-size: 14px; font-weight: 850;
}
.form-group input::placeholder { color: rgba(23,19,12,0.3); }
.form-group input:focus { border-color: #bd8b39; box-shadow: 0 0 0 3px rgba(189,139,57,0.1); }

.captcha-row { display: grid; grid-template-columns: 1fr 80px; gap: 8px; }
.captcha-row input {
  height: 42px; padding: 0 8px; text-align: center; letter-spacing: 6px;
  border: 1.5px solid rgba(189,139,57,0.3); border-radius: 10px; outline: 0;
  background: #fffdf7; font-size: 15px; font-weight: 850;
}
.captcha-row input:focus { border-color: #bd8b39; }
.captcha-box {
  height: 42px; border: 0; border-radius: 10px;
  background: linear-gradient(135deg, #e8d5a0, #d4ba80);
  color: #3d2a0a; font-size: 20px; font-weight: 950;
  letter-spacing: 3px; font-family: monospace; cursor: pointer;
}

.error-msg {
  padding: 8px 10px; border-radius: 10px;
  color: #8b2118; background: #ffe8e4;
  font-size: 11px; font-weight: 800; line-height: 1.3;
}

.submit-btn {
  height: 44px; margin-top: 2px; border: 0; border-radius: 12px;
  color: #fff; background: linear-gradient(145deg, #1a1f18, #2a3020);
  font-size: 14px; font-weight: 900; cursor: pointer;
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}
.submit-btn:disabled { opacity: 0.5; }

.switch-btn {
  border: 0; background: transparent;
  color: rgba(255,246,224,0.5); font-size: 12px; font-weight: 800;
  flex-shrink: 0;
}
</style>
