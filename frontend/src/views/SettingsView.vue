<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useStore } from '../composables/useStore'

const router = useRouter()
const { profile, saveProfile, logout } = useStore()

async function onSave() {
  await saveProfile()
  router.push({ name: 'profile' })
}

function onLogout() {
  logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="page">
    <header class="nav profile-nav">
      <div>
        <span class="hello">个人资料</span>
        <h2>设置</h2>
      </div>
      <button class="icon-btn" type="button" @click="onSave">
        <el-icon><Check /></el-icon>
      </button>
    </header>

    <section class="profile-panel">
      <div class="panel-title">
        <b>档口资料</b>
        <span>这些信息会显示在我的页面和报价资料里</span>
      </div>
      <label class="profile-field">
        <span>你的称呼</span>
        <input v-model="profile.ownerName" placeholder="例如：张老板" />
      </label>
      <label class="profile-field">
        <span>店铺名称</span>
        <input v-model="profile.shopName" placeholder="例如：锦禾服装报价室" />
      </label>
      <label class="profile-field">
        <span>所在位置</span>
        <input v-model="profile.location" placeholder="例如：广州 · 沙河档口" />
      </label>
      <label class="profile-field">
        <span>联系电话</span>
        <input v-model="profile.phone" inputmode="tel" placeholder="可不填" />
      </label>
      <button class="logout-btn" type="button" @click="onLogout">退出当前账号</button>
    </section>
  </div>
</template>

<style scoped>
.page {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  padding: 12px 22px 20px;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 20px;
}

.hello {
  color: rgba(255, 243, 220, 0.58);
  font-size: 13px;
}

.nav h2 {
  margin: 3px 0 0;
  color: #fff3dc;
  font-size: 25px;
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

.profile-panel {
  margin-top: 12px;
  padding: 16px;
  border-radius: 26px;
  color: #17130c;
  background: linear-gradient(145deg, rgba(255, 250, 238, 0.96), rgba(228, 211, 180, 0.92));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.58);
}

.panel-title {
  margin-bottom: 12px;
}

.panel-title b,
.panel-title span {
  display: block;
}

.panel-title b {
  color: #17130c;
  font-size: 17px;
}

.panel-title span {
  margin-top: 4px;
  color: rgba(23, 21, 18, 0.5);
  font-size: 12px;
  font-weight: 800;
}

.profile-field {
  display: grid;
  gap: 7px;
  margin-top: 12px;
}

.profile-field span {
  color: rgba(23, 21, 18, 0.58);
  font-size: 13px;
  font-weight: 900;
}

.profile-field input {
  height: 46px;
  border: 2px solid #d2b98f;
  border-radius: 16px;
  outline: 0;
  padding: 0 12px;
  color: #050505;
  background: #fffaf2;
  font-size: 15px;
  font-weight: 900;
}

.profile-field input:focus {
  border-color: #1f241f;
  box-shadow: 0 0 0 3px rgba(194, 145, 62, 0.22);
}

.logout-btn {
  min-height: 48px;
  width: 100%;
  margin-top: 18px;
  border: 0;
  border-radius: 18px;
  color: #fffaf1;
  background: #1e241e;
  font-weight: 900;
}
</style>
