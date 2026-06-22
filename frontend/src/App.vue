<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Document, House, Money, User } from '@element-plus/icons-vue'
import { useStore } from './composables/useStore'

const { isReady, isAuthenticated, initAuth } = useStore()
const route = useRoute()
const isOfficialSite = computed(() => route.meta.publicSite === true)
const isSupportPage = computed(() => String(route.path).startsWith('/support'))

onMounted(() => {
  initAuth()
})
</script>

<template>
  <router-view v-if="isOfficialSite || isSupportPage" />
  <main v-else class="mobile-showcase">
    <section v-if="!isReady" class="auth-panel">
      <div class="loading-mark">L</div>
      <h1>正在打开服装供应系统</h1>
      <p>正在检查登录状态，请稍等。</p>
    </section>

    <section v-else-if="!isAuthenticated" class="auth-panel">
      <router-view />
    </section>

    <template v-else>
      <section class="phone" aria-label="手机端成本报价系统预览">
        <div class="screen">
          <div class="notch"></div>
          <div
            class="app-view"
            :class="{ 'app-view-locked': $route.name === 'ai-costing' || $route.name === 'home' || $route.name === 'cost' }"
          >
            <router-view v-slot="{ Component }">
              <Transition name="page-fade" mode="out-in">
                <component :is="Component" />
              </Transition>
            </router-view>
          </div>
          <nav class="bottom-bar" aria-label="主导航">
            <button :class="{ active: $route.name === 'home' }" type="button" @click="$router.push({ name: 'home' })">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </button>
            <button :class="{ active: $route.name === 'photo' }" type="button" @click="$router.push({ name: 'photo' })">
              <el-icon><Document /></el-icon>
              <span>建款</span>
            </button>
            <button
              :class="{ active: $route.name === 'cost' || $route.name === 'result' }"
              type="button"
              @click="$router.push({ name: 'cost' })"
            >
              <el-icon><Money /></el-icon>
              <span>报价</span>
            </button>
            <button
              :class="{ active: $route.name === 'profile' || $route.name === 'settings' || $route.name === 'asset' }"
              type="button"
              @click="$router.push({ name: 'profile' })"
            >
              <el-icon><User /></el-icon>
              <span>我的</span>
            </button>
          </nav>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
/* ====== 基础布局：全屏 flex 链 ====== */
.mobile-showcase {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100dvh;
  height: -webkit-fill-available;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--porcelain);
}

.auth-panel {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  align-content: center;
  width: 100%;
  overflow-y: auto;
  scrollbar-width: none;
  color: var(--porcelain);
  background: var(--ink);
  padding: 22px;
  padding-top: calc(22px + env(safe-area-inset-top, 0px));
  padding-bottom: calc(22px + env(safe-area-inset-bottom, 0px));
}

.auth-panel::-webkit-scrollbar {
  display: none;
}

.phone {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.screen {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: max(28px, env(safe-area-inset-top, 0px));
  background:
    radial-gradient(circle at 78% 0%, rgba(240, 209, 136, 0.22), transparent 27%),
    linear-gradient(180deg, #fbf2df 0%, #f7ecd4 54%, #eddec0 100%);
}

.app-view {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: hidden;
}

.app-view::-webkit-scrollbar {
  display: none;
}

.app-view.app-view-locked {
  overflow: hidden;
  overscroll-behavior: contain;
  touch-action: none;
}

.app-view.app-view-locked > :deep(*) {
  min-height: 0;
  touch-action: auto;
}

.bottom-bar {
  flex-shrink: 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3px;
  align-items: center;
  height: 48px;
  margin: 0 14px 4px;
  padding: 4px;
  border: 1px solid rgba(152, 123, 69, 0.18);
  border-radius: 22px;
  background: rgba(255, 250, 241, 0.86);
  box-shadow: 0 -12px 32px rgba(51, 42, 26, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(16px);
}

.bottom-bar button {
  display: grid;
  gap: 1px;
  min-width: 0;
  min-height: 38px;
  place-items: center;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: rgba(23, 32, 24, 0.62);
  font-size: 10px;
  font-weight: 850;
  line-height: 1;
}

.bottom-bar .el-icon {
  font-size: 17px;
}

.bottom-bar button.active {
  color: #f3d891;
  background: linear-gradient(145deg, #083426, #0e4b37);
  transform: translateY(-6px);
  box-shadow: 0 12px 22px rgba(12, 54, 40, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.11);
}

/* ====== 通用 ====== */
.mobile-showcase::before,
.desktop-copy,
.loading-mark { display: none; }

button {
  cursor: pointer;
  transition: transform 180ms ease, filter 180ms ease, box-shadow 180ms ease, opacity 180ms ease;
}

button:hover { filter: brightness(1.04); }
button:active { transform: translateY(1px) scale(0.99); }

input:focus,
button:focus-visible {
  outline: 2px solid rgba(189, 139, 57, 0.5);
  outline-offset: 1px;
}

/* ── 页面过渡动画 ── */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ====== 手机端 ====== */
@media (max-width: 900px) {
  .notch { display: none; }

  .screen {
    padding-top: env(safe-area-inset-top, 0px);
    padding-bottom: 0;
  }

  .bottom-bar {
    height: 46px;
    margin: 0 8px 4px;
    padding: 3px;
    border-radius: 20px;
  }

  .bottom-bar button { min-height: 36px; font-size: 10px; }
  .bottom-bar .el-icon { font-size: 16px; }
}
</style>
