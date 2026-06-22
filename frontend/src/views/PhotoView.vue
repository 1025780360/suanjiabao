<script setup lang="ts">
import { Close } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useStore } from '../composables/useStore'
import { getCategoryImage, matchImageByName } from '../assets/style-images'

const router = useRouter()
const {
  imagePreview,
  customCategoryName,
  visibleCategories,
  selectCategory,
  addCustomCategory,
  removeCategory,
} = useStore()

function goHome() { router.push({ name: 'home' }) }

function onSelectCategory(key: string) {
  selectCategory(key)
  router.push({ name: 'cost' })
}

async function onAddCustomCategory() {
  await addCustomCategory()
  router.push({ name: 'cost' })
}

function previewImage(key: string) { imagePreview.value = getCategoryImage(key) }

function thumbFor(item: { key: string; name: string }) {
  const byKey = getCategoryImage(item.key)
  if (byKey !== getCategoryImage('default')) return byKey
  return matchImageByName(item.name)
}

watch(customCategoryName, (val) => {
  if (val.trim()) imagePreview.value = matchImageByName(val)
})

// ── 长按单个品类 → 显示删除按钮 ──
const deletingKey = ref('')
let pressTimer: any = null

function onTouchStart(item: any) {
  previewImage(item.key)
  if (item.ownerId !== 'system') {
    pressTimer = setTimeout(() => { deletingKey.value = item.key }, 600)
  }
}
function onTouchEnd() { clearTimeout(pressTimer) }
function onTouchMove() { clearTimeout(pressTimer) }

async function doDelete(item: any) {
  await removeCategory(item.key)
  deletingKey.value = ''
}
</script>

<template>
  <div class="page">
    <!-- 预览区 -->
    <div class="preview-area">
      <img v-if="imagePreview" :src="imagePreview" alt="" class="preview-img" />
      <div v-else class="preview-empty">选择品类自动出图</div>
      <button class="close-btn" type="button" @click="goHome">
        <el-icon><Close /></el-icon>
      </button>
    </div>

    <!-- 品类区域 -->
    <div class="category-section">
      <div class="section-head">
        <b>选择品类</b>
        <span>系统带出默认成本项</span>
      </div>

      <div class="category-grid">
        <div
          v-for="item in visibleCategories"
          :key="item.key"
          class="cat-wrap"
        >
          <button
            type="button"
            class="cat-btn"
            @click="onSelectCategory(item.key)"
            @touchstart="onTouchStart(item)"
            @touchend="onTouchEnd"
            @touchmove="onTouchMove"
            @contextmenu.prevent
          >
            <span class="cat-icon">
              <img :src="thumbFor(item)" alt="" />
            </span>
            <span class="cat-text">
              <b>{{ item.name }}</b>
              <small>{{ item.desc }}</small>
            </span>
          </button>
          <button
            v-if="deletingKey === item.key"
            class="del-btn"
            type="button"
            @click.stop="doDelete(item)"
          >✕</button>
        </div>
      </div>

      <div class="custom-category">
        <input v-model="customCategoryName" placeholder="没有合适的？自己填一个品类" />
        <button type="button" @click="onAddCustomCategory">创建</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* ── 预览区 ── */
.preview-area {
  position: relative;
  flex: 0 0 auto;
  align-self: center;
  width: min(55%, 180px);
  aspect-ratio: 1;
  margin: 8px 0 6px;
  border-radius: 20px;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 30%, rgba(240,209,136,0.1), transparent 40%),
    linear-gradient(170deg, #1a1f18 0%, #22261e 100%);
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-empty {
  display: grid;
  height: 100%;
  place-items: center;
  color: rgba(255,255,255,0.25);
  font-size: 14px;
  font-weight: 700;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  color: #fff;
  background: rgba(0,0,0,0.35);
  font-size: 15px;
}

/* ── 品类区域 ── */
.category-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0 14px;
}

.section-head {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 0;
}

.section-head b { color: #fff3dc; font-size: 17px; font-weight: 900; }
.section-head span { color: rgba(255,243,220,0.42); font-size: 11px; }

/* ── 品类网格 ── */
.category-grid {
  flex: 1;
  height: 0;
  overflow-y: scroll;
  -webkit-overflow-scrolling: touch;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  align-content: start;
  padding-bottom: 8px;
  scrollbar-width: none;
}
.category-grid::-webkit-scrollbar { display: none; }

.custom-category {
  flex-shrink: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 64px;
  gap: 6px;
  padding: 7px;
  margin-bottom: 8px;
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(255,250,238,0.94), rgba(228,211,180,0.9));
}

.cat-wrap { position: relative; }

.cat-btn {
  width: 100%;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  min-height: 66px;
  padding: 9px 10px;
  border: 0;
  border-radius: 16px;
  text-align: left;
  color: #17130c;
  background: linear-gradient(145deg, rgba(255,250,238,0.96), rgba(228,211,180,0.92));
  box-shadow: 0 8px 22px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.5);
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
}
.cat-btn:active { transform: scale(0.97); }

.cat-icon {
  overflow: hidden;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(0,0,0,0.04);
}
.cat-icon img { width: 100%; height: 100%; object-fit: cover; }

.cat-text b { display: block; color: #050505; font-size: 14px; font-weight: 900; }
.cat-text small { display: block; margin-top: 2px; color: rgba(23,21,18,0.45); font-size: 11px; font-weight: 700; }

/* ── 长按后出现的悬浮删除 X ── */
.del-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border: 2px solid #fff;
  border-radius: 50%;
  padding: 0;
  color: #fff;
  background: #e74c3c;
  font-size: 13px;
  line-height: 1;
  z-index: 5;
  box-shadow: 0 3px 10px rgba(231,76,60,0.45);
}

.custom-category input {
  min-width: 0;
  height: 38px;
  padding: 0 10px;
  border: 2px solid #d2b98f;
  border-radius: 10px;
  outline: 0;
  background: #fffaf2;
  color: #050505;
  font-size: 13px;
  font-weight: 900;
}
.custom-category button {
  border-radius: 10px;
  border: 0;
  font-weight: 900;
  font-size: 12px;
  color: #ffe9b8;
  background: linear-gradient(145deg, #080a07, #1d2118);
}
</style>
