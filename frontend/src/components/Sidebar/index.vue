<template>
  <el-aside
    :width="windowWidth < 900 ? '0' : isCollapsed ? '60px' : '300px'"
    class="sidebar-container"
  >
    <div class="sidebar-content">
      <!-- 头部区域 -->
      <div class="sidebar-header">
        <h2 v-if="!isCollapsed" class="sidebar-title">对话历史</h2>
        <el-button
          class="collapse-btn"
          @click="handleToggleCollapse"
          :icon="isCollapsed ? 'ArrowRight' : 'ArrowLeft'"
          circle
          size="small"
          text
        />
      </div>

      <!-- 新建对话按钮 -->
      <div class="new-conversation-section" v-if="!isCollapsed">
        <el-button
          type="primary"
          @click="handleNewConversation"
          class="new-conversation-btn"
          :icon="Plus"
          style="width: 100%"
        >
          新建对话
        </el-button>
      </div>

      <!-- 对话列表 -->
      <div class="conversation-list" v-if="!isCollapsed">
        <el-scrollbar height="calc(100vh - 160px)">
          <div
            v-for="conversation in sortedConversations"
            :key="conversation.id"
            :class="['conversation-item', { active: conversation.id === currentConversationId }]"
            @click="handleSelectConversation(conversation.id)"
          >
            <div class="conversation-content">
              <div class="conversation-title">
                {{ conversation.title || '新对话' }}
              </div>
              <div class="conversation-preview">
                {{ conversation.messages[conversation.messages.length - 1]?.content || '空对话' }}
              </div>
              <div class="conversation-meta">
                <span class="conversation-date">
                  {{ formatDate(conversation.updatedAt) }}
                </span>
                <span class="conversation-model">
                  {{ getModelName(conversation.model) }}
                </span>
              </div>
            </div>
            <el-button
              class="delete-btn"
              @click="handleDeleteConversation(conversation.id, $event)"
              :icon="Close"
              circle
              size="small"
              type="danger"
              link
            />
          </div>
        </el-scrollbar>

        <!-- 空状态 -->
        <div v-if="sortedConversations.length === 0" class="empty-state">
          <p>暂无对话记录</p>
          <p>点击"新建对话"开始聊天</p>
        </div>
      </div>

      <!-- 折叠状态下的最小化视图 -->
      <div class="minimized-view" v-if="isCollapsed && windowWidth >= 900">
        <el-button
          class="new-conversation-btn minimized"
          @click="handleNewConversation"
          :icon="Plus"
          circle
          size="small"
          type="primary"
        />
        <div class="conversation-dots">
          <div
            v-for="conversation in sortedConversations.slice(0, 5)"
            :key="conversation.id"
            :class="['conversation-dot', { active: conversation.id === currentConversationId }]"
            @click="handleSelectConversation(conversation.id)"
            :title="conversation.title || '新对话'"
          ></div>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Conversation } from '@/types'
import { formatDate } from '@/utils'
import { Plus, Close } from '@element-plus/icons-vue'

interface Props {
  conversations: Conversation[]
  currentConversationId: string | null
  isCollapsed: boolean
}

interface Emits {
  (e: 'select-conversation', id: string): void
  (e: 'delete-conversation', id: string): void
  (e: 'new-conversation'): void
  (e: 'toggle-collapse'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 窗口宽度状态
const windowWidth = ref(window.innerWidth)

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 按更新时间排序对话
const sortedConversations = computed(() => {
  return [...props.conversations].sort((a, b) => b.updatedAt - a.updatedAt)
})

// 处理对话选择
const handleSelectConversation = (id: string) => {
  emit('select-conversation', id)
}

// 处理删除对话
const handleDeleteConversation = (id: string, event: Event) => {
  event.stopPropagation()
  emit('delete-conversation', id)
}

// 处理新建对话
const handleNewConversation = () => {
  emit('new-conversation')
}

// 处理侧边栏切换
const handleToggleCollapse = () => {
  emit('toggle-collapse')
}

// 根据模型ID获取模型名称
const getModelName = (modelId: string): string => {
  const modelMap: Record<string, string> = {
    'deepseek-chat': 'DeepSeek Chat',
  }
  return modelMap[modelId] || modelId
}
</script>

<style scoped>
.sidebar-container {
  height: 100vh;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.sidebar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.new-conversation-section {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.conversation-list {
  flex: 1;
  padding: 8px;
}

.conversation-item {
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.conversation-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.conversation-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.conversation-content {
  flex: 1;
  min-width: 0;
  margin-right: 8px;
}

.conversation-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-preview {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #909399;
}

.conversation-model {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.3s;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #909399;
}

.empty-state p {
  margin: 8px 0;
  font-size: 14px;
}

.minimized-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  gap: 16px;
}

.conversation-dots {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.conversation-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dcdfe6;
  cursor: pointer;
  transition: all 0.3s;
}

.conversation-dot:hover {
  background: #c0c4cc;
}

.conversation-dot.active {
  background: #409eff;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .sidebar-container {
    width: 100% !important;
    height: auto;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar-container:not(.el-aside--collapsed) {
    transform: translateX(0);
  }
}
</style>