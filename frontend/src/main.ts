import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import router from './router'

function setRealVH() {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

function keepPagePinned() {
  window.scrollTo(0, 0)
  document.documentElement.scrollTop = 0
  document.body.scrollTop = 0
}

function updateKeyboardInset() {
  const viewport = window.visualViewport
  const inset = viewport ? Math.max(0, window.innerHeight - viewport.height - viewport.offsetTop) : 0
  document.documentElement.style.setProperty('--keyboard-inset', `${Math.round(inset)}px`)
}

setRealVH()
updateKeyboardInset()

window.addEventListener('orientationchange', () => {
  window.setTimeout(() => {
    setRealVH()
    updateKeyboardInset()
    keepPagePinned()
  }, 260)
})

window.addEventListener('resize', () => {
  setRealVH()
  const tag = document.activeElement?.tagName
  const isTyping = tag === 'INPUT' || tag === 'TEXTAREA'
  if (!isTyping) {
    keepPagePinned()
  }
  updateKeyboardInset()
})

document.addEventListener('focusout', () => {
  window.setTimeout(() => {
    updateKeyboardInset()
    keepPagePinned()
  }, 80)
})

window.visualViewport?.addEventListener('resize', () => {
  updateKeyboardInset()
})
window.visualViewport?.addEventListener('scroll', () => {
  updateKeyboardInset()
})

createApp(App).use(router).use(ElementPlus).mount('#app')
