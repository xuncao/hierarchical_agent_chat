<template>
  <div class="chat-messages" ref="messagesContainer">
    <!-- 空状态 -->
    <div v-if="!messages.length" class="empty-state">
      <el-empty description="开始新的对话" :image-size="200">
        <template #image>
          <div class="empty-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
        </template>
        <p class="empty-description">在下方输入消息开始与AI对话</p>
      </el-empty>
    </div>

    <!-- 消息列表 -->
    <div v-else class="messages-list">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', `message-${message.role}`]"
      >
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="message-user">
          <el-avatar class="avatar" size="small">👤</el-avatar>
          <div class="bubble">
            <div class="content">{{ message.content }}</div>
            <div class="timestamp">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- AI消息 -->
        <div v-else class="message-assistant">
          <el-avatar class="avatar" size="small">🤖</el-avatar>
          <div class="bubble">
            <div class="content">
              <!-- 流式输出显示 -->
              <span v-if="message.isStreaming" class="streaming-content">
                {{ message.displayContent }}
                <span class="cursor">|</span>
              </span>
              <span v-else>{{ message.content }}</span>
            </div>
            <div class="timestamp">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>

      <!-- 加载指示器 -->
      <div v-if="isLoading" class="loading-indicator">
        <el-avatar class="avatar" size="small">🤖</el-avatar>
        <div class="loading-content">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span class="loading-text">AI正在思考...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUpdated } from 'vue'
import type { Message } from '@/types'
import { formatTime } from '@/utils'

interface Props {
  messages: Message[]
  isLoading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'scroll-to-bottom': []
}>()

const messagesContainer = ref<HTMLDivElement>()

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(
  () => props.messages.length,
  async (newLength, oldLength) => {
    if (newLength > oldLength) {
      await scrollToBottom()
    }
  }
)

// 监听加载状态变化
watch(
  () => props.isLoading,
  async (newLoading, oldLoading) => {
    if (newLoading && !oldLoading) {
      await scrollToBottom()
    }
  }
)

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom()
})

// 组件更新时滚动到底部
onUpdated(() => {
  scrollToBottom()
})

// 暴露滚动方法给父组件
const handleScrollToBottom = () => {
  scrollToBottom()
}

defineExpose({
  handleScrollToBottom,
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-top: 77px;
  background-color: #ffffff;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-description {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.messages-list {
  margin: 0 auto;
}

.message {
  margin-bottom: 24px;
}

.message-user {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 12px;
}

.message-assistant {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 12px;
}

.avatar {
  flex-shrink: 0;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  position: relative;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-user .bubble {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-assistant .bubble {
  background-color: #f4f4f5;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.content {
  word-wrap: break-word;
  line-height: 1.5;
  white-space: pre-wrap;
}

.streaming-content {
  position: relative;
}

.cursor {
  animation: blink 1s infinite;
  color: #409eff;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}

.timestamp {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.7;
}

.message-user .timestamp {
  text-align: right;
}

.loading-indicator {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  max-width: 200px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}
.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-text {
  font-size: 14px;
  color: #606266;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>