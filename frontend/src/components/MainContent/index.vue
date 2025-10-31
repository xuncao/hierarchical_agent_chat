<template>
  <div class="main-content">
    <!-- 对话消息区域 -->
    <ChatMessages
      :messages="currentConversation?.messages || []"
      :is-loading="isLoading"
      @scroll-to-bottom="handleScrollToBottom"
    />

    <!-- 输入控制区域 -->
    <ChatInput
      v-model="inputText"
      :is-loading="isLoading"
      :selected-model="currentConversation?.model || defaultModel"
      :deep-think="currentConversation?.deepThink || false"
      :use-search="currentConversation?.useSearch || false"
      @send-message="handleSendMessage"
      @update-model="handleModelChange"
      @toggle-deep-think="handleToggleDeepThink"
      @toggle-search="handleToggleSearch"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useConversationStore } from '@/stores/conversation'
import ChatMessages from '../ChatMessages/index.vue'
import ChatInput from '../ChatInput/index.vue'

const conversationStore = useConversationStore()

// 响应式数据
const inputText = ref('')
const isLoading = ref(false)

// 计算属性
const currentConversation = computed(() => conversationStore.currentConversation)
const defaultModel = computed(() => conversationStore.defaultModel)

// 方法
const handleSendMessage = async (content: string) => {
  if (!content.trim() || isLoading.value) return

  isLoading.value = true

  try {
    // 发送消息（conversation.ts中会自动处理新对话创建）
    await conversationStore.sendMessage(content)

    // 清空输入框
    inputText.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
  }
}

const handleModelChange = (model: string) => {
  if (currentConversation.value) {
    conversationStore.updateConversationSettings({
      model,
    })
  }
}

const handleToggleDeepThink = (deepThink: boolean) => {
  if (currentConversation.value) {
    conversationStore.updateConversationSettings({
      deepThink,
    })
  }
}

const handleToggleSearch = (useSearch: boolean) => {
  if (currentConversation.value) {
    conversationStore.updateConversationSettings({
      useSearch,
    })
  }
}

const handleScrollToBottom = () => {
  // 滚动到底部的逻辑将在ChatMessages组件中实现
}

// 监听当前对话变化，清空输入框
watch(currentConversation, (newConversation, oldConversation) => {
  if (newConversation?.id !== oldConversation?.id) {
    inputText.value = ''
  }
})
</script>

<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  height: 100vh;
  flex: 1;
  background-color: #f5f5f5;
}
</style>