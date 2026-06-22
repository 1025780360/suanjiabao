<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowRightBold, Check, Download, Iphone, Money, PictureFilled, Star, Warning } from '@element-plus/icons-vue'

type DeviceKind = 'ios' | 'huawei' | 'android'

const showIosGuide = ref(false)

const deviceKind = computed<DeviceKind>(() => {
  const ua = window.navigator.userAgent.toLowerCase()
  const platform = window.navigator.platform?.toLowerCase() || ''
  const isIos = /iphone|ipad|ipod/.test(ua) || (platform.includes('mac') && 'ontouchend' in document)
  if (isIos) return 'ios'
  if (/huawei|honor|harmonyos|hmos/.test(ua)) return 'huawei'
  return 'android'
})

const primaryAction = computed(() => {
  if (deviceKind.value === 'ios') {
    return {
      label: '苹果手机安装教程',
      sub: '不用下载 App，添加到主屏幕就能像 App 一样打开',
      icon: Iphone,
    }
  }

  return {
    label: deviceKind.value === 'huawei' ? '华为手机下载' : '安卓手机下载',
    sub: '下载 APK 安装包，安装后直接使用',
    icon: Download,
  }
})

const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const apkUrl = isLocal
  ? 'http://127.0.0.1:8000/api/downloads/android-apk/'
  : `${window.location.origin}/api/downloads/android-apk/`

function handlePrimaryAction() {
  if (deviceKind.value === 'ios') {
    showIosGuide.value = true
    return
  }
  window.location.href = apkUrl
}

function openWebApp() {
  window.location.href = '/login'
}
</script>

<template>
  <main class="official-page">
    <section class="hero">
      <div class="brand-row">
        <span class="brand-mark">衣</span>
        <span>算价宝</span>
      </div>

      <p class="eyebrow">广州档口老板专用</p>
      <h1>拍个款，填几个数，马上知道这件衣服赚不赚</h1>
      <p class="summary">
        不用 Excel，不用复杂 ERP。把面料、加工、辅料、利润快速算清楚，报价前先知道最低接单价。
      </p>

      <button class="download-card" type="button" @click="handlePrimaryAction">
        <span class="download-icon">
          <el-icon><component :is="primaryAction.icon" /></el-icon>
        </span>
        <span>
          <b>{{ primaryAction.label }}</b>
          <small>{{ primaryAction.sub }}</small>
        </span>
        <el-icon class="go"><ArrowRightBold /></el-icon>
      </button>

      <button class="web-link" type="button" @click="openWebApp">已有账号，打开网页版系统</button>
    </section>

    <section class="advantages">
      <article>
        <el-icon><Money /></el-icon>
        <b>1 分钟算清成本</b>
        <span>面料、加工、辅料、包装、利润一次算完，系统直接给出建议报价和最低接单价。</span>
      </article>
      <article>
        <el-icon><PictureFilled /></el-icon>
        <b>拍照就能建款</b>
        <span>款式图、品类、成本记录自动保存，下次类似款可以直接复制改价。</span>
      </article>
      <article>
        <el-icon><Warning /></el-icon>
        <b>低价接单提醒</b>
        <span>报价低于安全价时提醒风险，避免忙了一季最后不赚钱。</span>
      </article>
      <article>
        <el-icon><Star /></el-icon>
        <b>AI 助手会引导</b>
        <span>老板像发微信一样说需求，AI 帮你建款、记成本、算利润。</span>
      </article>
    </section>

    <section class="proof-card">
      <p>适合谁用？</p>
      <h2>档口老板、小型服装厂、临时接单报价</h2>
      <div class="proof-grid">
        <span><el-icon><Check /></el-icon> 不用先建资料库</span>
        <span><el-icon><Check /></el-icon> 手机端优先</span>
        <span><el-icon><Check /></el-icon> 款式和报价留记录</span>
        <span><el-icon><Check /></el-icon> 数据按账号保存</span>
      </div>
    </section>

    <div v-if="showIosGuide" class="guide-mask" @click.self="showIosGuide = false">
      <section class="guide-sheet" role="dialog" aria-modal="true" aria-label="苹果手机安装教程">
        <button class="close-guide" type="button" @click="showIosGuide = false">关闭</button>
        <p class="guide-kicker">苹果手机安装教程</p>
        <h2>添加到主屏幕后，就像 App 一样打开</h2>
        <p class="guide-note">
          请用 Safari 浏览器操作。添加成功后，从手机桌面图标进入系统，就不会再显示这个宣传页。
        </p>

        <div class="guide-steps">
          <article>
            <div class="guide-pic browser-pic">
              <span class="address-bar">算价宝</span>
              <span class="share-dot">□↑</span>
            </div>
            <b>1. 用 Safari 打开网站</b>
            <span>如果是在微信里打开，先点右上角，选择“在 Safari 中打开”。</span>
          </article>

          <article>
            <div class="guide-pic toolbar-pic">
              <span></span>
              <strong>□↑</strong>
              <span></span>
            </div>
            <b>2. 点击底部分享按钮</b>
            <span>在 Safari 底部工具栏中间，找到带向上箭头的分享按钮。</span>
          </article>

          <article>
            <div class="guide-pic menu-pic">
              <i>拷贝</i>
              <i>添加到主屏幕</i>
              <i>收藏</i>
            </div>
            <b>3. 选择“添加到主屏幕”</b>
            <span>如果没看到，向上滑动菜单，找到“添加到主屏幕”。</span>
          </article>

          <article>
            <div class="guide-pic home-pic">
              <em>衣</em>
              <small>算价宝</small>
            </div>
            <b>4. 桌面打开系统</b>
            <span>以后从这个桌面图标进入，直接打开系统，不再弹出宣传页。</span>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.official-page {
  height: 100vh;
  height: 100dvh;
  overflow-y: auto;
  padding: max(env(safe-area-inset-top, 0px), 18px) 18px 34px;
  color: var(--porcelain);
  background:
    radial-gradient(circle at 82% 4%, rgba(239, 208, 131, 0.22), transparent 30%),
    radial-gradient(circle at 12% 24%, rgba(158, 172, 145, 0.24), transparent 34%),
    linear-gradient(120deg, rgba(255, 255, 255, 0.035) 0 1px, transparent 1px 30px),
    linear-gradient(180deg, #102018 0%, #07100d 100%);
  -webkit-overflow-scrolling: touch;
}

.hero {
  min-height: 78vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
}

.brand-row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: rgba(251, 245, 232, 0.78);
  font-weight: 800;
}

.brand-mark,
.download-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  color: #15160f;
  background: var(--gold-gradient);
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 15px;
  font-size: 18px;
}

.eyebrow {
  margin: 26px 0 0;
  color: rgba(251, 245, 232, 0.58);
  font-size: 14px;
  font-weight: 800;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  max-width: 9em;
  color: var(--porcelain);
  font-size: 42px;
  line-height: 1.05;
  letter-spacing: -0.05em;
}

.summary {
  max-width: 330px;
  color: rgba(251, 245, 232, 0.72);
  font-size: 16px;
  line-height: 1.7;
}

.download-card {
  display: grid;
  grid-template-columns: 54px 1fr 20px;
  align-items: center;
  gap: 13px;
  width: 100%;
  margin-top: 12px;
  padding: 14px;
  border: 0;
  border-radius: 24px;
  text-align: left;
  color: var(--text);
  background: var(--panel-gradient);
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.download-icon {
  width: 54px;
  height: 54px;
  border-radius: 19px;
  font-size: 24px;
}

.download-card b,
.download-card small {
  display: block;
}

.download-card b {
  font-size: 19px;
}

.download-card small {
  margin-top: 4px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.35;
}

.go {
  color: rgba(22, 18, 11, 0.62);
}

.web-link {
  width: 100%;
  height: 46px;
  border: 1px solid rgba(239, 208, 131, 0.22);
  border-radius: 18px;
  color: rgba(251, 245, 232, 0.82);
  background: rgba(255, 255, 255, 0.06);
}

.advantages {
  display: grid;
  gap: 12px;
}

.advantages article,
.proof-card {
  border: 1px solid rgba(239, 208, 131, 0.16);
  border-radius: 24px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.08), transparent),
    rgba(11, 18, 15, 0.78);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
}

.advantages article {
  display: grid;
  gap: 7px;
  padding: 18px;
}

.advantages .el-icon {
  color: var(--gold-2);
  font-size: 22px;
}

.advantages b {
  color: var(--porcelain);
  font-size: 18px;
}

.advantages span,
.proof-grid span {
  color: rgba(251, 245, 232, 0.68);
  font-size: 14px;
  line-height: 1.58;
}

.proof-card {
  margin-top: 14px;
  padding: 20px;
}

.proof-card p {
  color: rgba(251, 245, 232, 0.54);
  font-weight: 800;
}

.proof-card h2 {
  margin-top: 8px;
  color: var(--porcelain);
  font-size: 24px;
  line-height: 1.2;
}

.proof-grid {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.proof-grid span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.proof-grid .el-icon {
  color: var(--gold-2);
}

.guide-mask {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: flex-end;
  padding: 16px;
  background: rgba(0, 0, 0, 0.58);
}

.guide-sheet {
  position: relative;
  width: 100%;
  max-height: min(86vh, 720px);
  overflow-y: auto;
  padding: 22px 18px calc(22px + env(safe-area-inset-bottom, 0px));
  border: 1px solid rgba(239, 208, 131, 0.22);
  border-radius: 28px;
  color: #fff4dc;
  background:
    radial-gradient(circle at 86% 0%, rgba(239, 208, 131, 0.28), transparent 30%),
    linear-gradient(180deg, #13201a 0%, #0b120f 100%);
  box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.45);
}

.close-guide {
  position: absolute;
  top: 14px;
  right: 14px;
  height: 34px;
  padding: 0 14px;
  border: 1px solid rgba(239, 208, 131, 0.22);
  border-radius: 999px;
  color: rgba(251, 245, 232, 0.82);
  background: rgba(255, 255, 255, 0.08);
}

.guide-kicker {
  color: rgba(251, 245, 232, 0.58);
  font-size: 13px;
  font-weight: 900;
}

.guide-sheet h2 {
  max-width: 260px;
  margin-top: 8px;
  color: var(--porcelain);
  font-size: 26px;
  line-height: 1.18;
}

.guide-note {
  margin-top: 10px;
  color: rgba(251, 245, 232, 0.7);
  font-size: 14px;
  line-height: 1.65;
}

.guide-steps {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.guide-steps article {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.07);
}

.guide-steps b,
.guide-steps span {
  display: block;
}

.guide-steps b {
  color: #fff8e8;
  font-size: 16px;
}

.guide-steps span {
  margin-top: 5px;
  color: rgba(255, 244, 220, 0.66);
  font-size: 12px;
  line-height: 1.45;
}

.guide-pic {
  display: grid;
  place-items: center;
  width: 96px;
  height: 96px;
  overflow: hidden;
  border-radius: 18px;
  color: #17130c;
  background: linear-gradient(145deg, #fff7e6, #d8ba83);
}

.browser-pic {
  align-content: space-between;
  padding: 12px;
}

.address-bar {
  width: 72px;
  padding: 5px 8px;
  border-radius: 999px;
  color: rgba(23, 19, 12, 0.55);
  background: rgba(23, 19, 12, 0.08);
  font-size: 10px;
}

.share-dot {
  font-size: 24px;
  font-weight: 900;
}

.toolbar-pic {
  grid-template-columns: 1fr 1fr 1fr;
  padding: 14px;
}

.toolbar-pic span {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(23, 19, 12, 0.18);
}

.toolbar-pic strong {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: rgba(23, 19, 12, 0.12);
  font-size: 18px;
}

.menu-pic {
  align-content: center;
  gap: 5px;
  padding: 10px;
}

.menu-pic i {
  width: 78px;
  padding: 5px 7px;
  border-radius: 9px;
  background: rgba(23, 19, 12, 0.1);
  font-size: 10px;
  font-style: normal;
  text-align: center;
}

.menu-pic i:nth-child(2) {
  color: #fff8e8;
  background: #17130c;
}

.home-pic {
  align-content: center;
  gap: 7px;
}

.home-pic em {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 15px;
  color: #17130c;
  background: linear-gradient(145deg, #ffe7ae, #b77b2d);
  font-style: normal;
  font-weight: 900;
}

.home-pic small {
  color: rgba(23, 19, 12, 0.72);
  font-size: 11px;
}

@media (min-width: 700px) {
  .official-page {
    max-width: 430px;
    margin: 0 auto;
    border-inline: 1px solid rgba(232, 199, 130, 0.14);
  }
}
</style>
