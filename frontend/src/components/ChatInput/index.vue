<template>
  <div class="chat-input">
    <!-- 控制按钮区域 -->
    <div class="control-bar">
      <!-- 模型选择 -->
      <div class="control-item">
        <span class="control-label">模型:</span>
        <el-select
          :model-value="selectedModel"
          :disabled="isLoading"
          placeholder="选择模型"
          size="small"
          style="width: 160px"
          @update:model-value="handleModelChange"
        >
          <el-option
            v-for="model in availableModels"
            :key="model.id"
            :label="model.name"
            :value="model.id"
          />
        </el-select>
      </div>

      <!-- 深度思考按钮 -->
      <div class="control-item">
        <el-button
          :type="deepThink ? 'primary' : 'default'"
          :disabled="isLoading"
          size="small"
          @click="handleDeepThinkToggle(!deepThink)"
          class="toggle-button"
        >
          <el-icon><Clock /></el-icon>
          深度思考
        </el-button>
      </div>

      <!-- 联网搜索按钮 -->
      <div class="control-item">
        <el-button
          :type="useSearch ? 'primary' : 'default'"
          :disabled="isLoading"
          size="small"
          @click="handleSearchToggle(!useSearch)"
          class="toggle-button"
        >
          <el-icon><Link /></el-icon>
          联网搜索
        </el-button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="localValue"
        type="textarea"
        :placeholder="placeholder"
        :disabled="isLoading"
        :autosize="{ minRows: 3, maxRows: 6 }"
        @keydown="handleKeydown"
        @input="handleInput"
        class="text-input"
        resize="none"
      />

      <el-button
        type="primary"
        @click="handleSend"
        :disabled="!canSend"
        :loading="isLoading"
        class="send-button"
        size="large"
      >
        {{ isLoading ? '发送中...' : '发送' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Model } from '@/types'
import { chatAPI } from '@/api'
import { Link, Clock } from '@element-plus/icons-vue'

interface Props {
  modelValue: string
  isLoading?: boolean
  selectedModel: string | null | undefined
  deepThink: boolean
  useSearch: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'send-message', content: string): void
  (e: 'update-model', model: string): void
  (e: 'toggle-deep-think', deepThink: boolean): void
  (e: 'toggle-search', useSearch: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const localValue = ref(props.modelValue)
const availableModels = ref<Model[]>([])

// 计算属性
const canSend = computed(() => {
  return localValue.value.trim().length > 0 && !props.isLoading
})

const placeholder = computed(() => {
  return props.isLoading ? 'AI正在回复中...' : '输入消息...'
})

// 方法
const handleSend = () => {
  if (canSend.value) {
    const content = localValue.value.trim()
    emit('send-message', content)
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

const handleInput = () => {
  emit('update:modelValue', localValue.value)
}

const handleModelChange = (modelId: string) => {
  emit('update-model', modelId)
}

const handleDeepThinkToggle = (value: boolean) => {
  emit('toggle-deep-think', value)
}

const handleSearchToggle = (value: boolean) => {
  emit('toggle-search', value)
}

// 加载可用模型
const loadAvailableModels = async () => {
  try {
    availableModels.value = await chatAPI.getModels()
  } catch (error) {
    console.error('加载模型列表失败:', error)
    // 使用默认模型作为备选
    availableModels.value = [
      { id: 'deepseek-chat', name: 'DeepSeek Chat' },
    ]
  }
}

// 监听props变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== localValue.value) {
      localValue.value = newValue
    }
  }
)

// 组件挂载时加载模型
loadAvailableModels()
</script>

<style scoped>
.chat-input {
  background-color: #ffffff;
  border-top: 1px solid #e4e7ed;
  padding: 16px 20px;
}

.control-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.input-area {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.text-input {
  flex: 1;
}

.send-button {
  min-width: 80px;
  height: 60px;
}

/* 按钮样式 */
.toggle-button {
  min-width: 100px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .control-bar {
    gap: 12px;
  }

  .control-item {
    flex: 1;
    min-width: 120px;
  }

  .input-area {
    flex-direction: column;
  }

  .send-button {
    width: 100%;
    height: 44px;
  }

  .toggle-button {
    min-width: 80px;
    font-size: 12px;
  }
}
</style>