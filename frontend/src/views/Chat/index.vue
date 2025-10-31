<template>
  <el-container class="app-container">
    <!-- 左侧对话列表 -->
    <Sidebar
      :conversations="conversations"
      :current-conversation-id="currentConversationId"
      :is-collapsed="isSidebarCollapsed"
      @switch-conversation="handleSwitchConversation"
      @new-conversation="handleNewConversation"
      @delete-conversation="handleDeleteConversation"
      @toggle-collapse="handleToggleSidebar"
    />

    <!-- 主内容区域 -->
    <el-main class="main-content">
      <MainContent />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useConversationStore } from '@/stores/conversation'
import Sidebar from '@/components/Sidebar/index.vue'
import MainContent from '@/components/MainContent/index.vue'

const route = useRoute()
const router = useRouter()
const conversationStore = useConversationStore()

// 响应式数据
const isSidebarCollapsed = ref(false)

// 计算属性
const conversations = computed(() => conversationStore.conversations)
const currentConversationId = computed(() => conversationStore.currentConversationId)

// 方法
const handleToggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 响应式设计：屏幕宽度小于900px时自动收起侧边栏
const checkScreenSize = () => {
  isSidebarCollapsed.value = window.innerWidth < 900
}

// 监听窗口大小变化
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// 方法
const handleSwitchConversation = (conversationId: string) => {
  conversationStore.switchConversation(conversationId)
  // 更新URL
  if (conversationId) {
    router.push(`/conversation/${conversationId}`)
  } else {
    router.push('/')
  }
}

const handleNewConversation = async () => {
  // 创建新对话，设置默认模型为deepseek
  const newConversation = await conversationStore.createNewConversation({
    model: 'deepseek-chat',
    deepThink: false,
    useSearch: false,
  })
  // 跳转到新对话页面
  router.push(`/conversation/${newConversation.id}`)
}

const handleDeleteConversation = (conversationId: string) => {
  conversationStore.deleteConversation(conversationId)
  // 如果删除的是当前对话，跳转到首页
  if (currentConversationId.value === conversationId) {
    router.push('/')
  }
}

// 监听路由变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId && newId !== currentConversationId.value) {
      conversationStore.switchConversation(newId as string)
    }
  }
)

// 监听当前对话变化，更新URL
watch(currentConversationId, (newId) => {
  if (newId && route.params.id !== newId) {
    router.push(`/conversation/${newId}`)
  }
})

// 组件挂载时处理路由
onMounted(() => {
  const routeId = route.params.id as string
  if (routeId) {
    conversationStore.switchConversation(routeId)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  padding: 0;
  background-color: #ffffff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
}
</style>
