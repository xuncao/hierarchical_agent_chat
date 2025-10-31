import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Conversation, Message, ConversationSettings } from '@/types'
import { generateId, getDefaultModel, saveToLocalStorage, loadFromLocalStorage } from '@/utils'
import { chatAPI } from '@/api'

export const useConversationStore = defineStore('conversation', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<string | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const currentConversation = computed(() => {
    return conversations.value.find(conv => conv.id === currentConversationId.value) || null
  })

  const defaultModel = computed(() => getDefaultModel())

  // 方法
  const loadConversations = () => {
    const saved = loadFromLocalStorage('conversations')
    if (saved && Array.isArray(saved)) {
      conversations.value = saved
      
      // 如果没有当前对话，设置第一个对话为当前对话
      if (saved.length > 0 && !currentConversationId.value) {
        currentConversationId.value = saved[0].id
      }
    }
  }

  const saveConversations = () => {
    saveToLocalStorage('conversations', conversations.value)
  }

  const createNewConversation = async (settings?: Partial<ConversationSettings>) => {
    const newConversation: Conversation = {
      id: generateId(),
      title: '新对话',
      messages: [],
      model: settings?.model || defaultModel.value,
      deepThink: settings?.deepThink || false,
      useSearch: settings?.useSearch || false,
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    conversations.value.unshift(newConversation)
    currentConversationId.value = newConversation.id
    saveConversations()
    
    return newConversation
  }

  const switchConversation = (conversationId: string) => {
    const conversation = conversations.value.find(conv => conv.id === conversationId)
    if (conversation) {
      currentConversationId.value = conversationId
      // 保存当前对话ID到本地存储
      saveToLocalStorage('currentConversationId', conversationId)
    }
  }

  const deleteConversation = (conversationId: string) => {
    const index = conversations.value.findIndex(conv => conv.id === conversationId)
    if (index !== -1) {
      conversations.value.splice(index, 1)
      
      // 如果删除的是当前对话，切换到其他对话或清空
      if (currentConversationId.value === conversationId) {
        if (conversations.value.length > 0) {
          currentConversationId.value = conversations.value[0].id
        } else {
          currentConversationId.value = null
        }
      }
      
      saveConversations()
    }
  }

  // 删除空对话
  const deleteEmptyConversations = () => {
    conversations.value = conversations.value.filter(conv => 
      conv.messages.length > 0
    )
    saveConversations()
  }

  const updateConversationTitle = (conversationId: string, title: string) => {
    const conversation = conversations.value.find(conv => conv.id === conversationId)
    if (conversation) {
      conversation.title = title
      conversation.updatedAt = Date.now()
      saveConversations()
    }
  }

  const updateConversationSettings = (settings: Partial<ConversationSettings>) => {
    if (!currentConversation.value) return
    
    const conversation = conversations.value.find(conv => conv.id === currentConversation.value!.id)
    if (conversation) {
      if (settings.model) conversation.model = settings.model
      if (settings.deepThink !== undefined) conversation.deepThink = settings.deepThink
      if (settings.useSearch !== undefined) conversation.useSearch = settings.useSearch
      conversation.updatedAt = Date.now()
      saveConversations()
    }
  }

  const addMessage = (conversationId: string, message: Message) => {
    const conversation = conversations.value.find(conv => conv.id === conversationId)
    if (conversation) {
      conversation.messages.push(message)
      conversation.updatedAt = Date.now()
      
      // 如果是第一条消息，更新对话标题
      if (conversation.messages.length === 1 && message.role === 'user') {
        conversation.title = message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
      }
      
      saveConversations()
    }
  }

  const sendMessage = async (content: string) => {
    isLoading.value = true
    
    try {
      // 如果没有当前对话，创建新对话
      if (!currentConversation.value) {
        await createNewConversation()
      }
      
      // 添加用户消息
      const userMessage: Message = {
        id: generateId(),
        role: 'user',
        content: content,
        timestamp: Date.now()
      }
      
      addMessage(currentConversation.value!.id, userMessage)
      
      // 创建AI消息（流式输出）
      const aiMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        isStreaming: true,
        displayContent: ''
      }
      
      addMessage(currentConversation.value.id, aiMessage)
      
      // 发送API请求
      await chatAPI.sendMessage(
        {
          messages: [userMessage],
          model: currentConversation.value.model,
          deepThink: currentConversation.value.deepThink,
          useSearch: currentConversation.value.useSearch,
          conversationId: currentConversation.value.id,
          message: content
        },
        // 流式输出回调
        (chunk: string) => {
          // 更新流式内容
          const conversation = conversations.value.find(conv => conv.id === currentConversation.value!.id)
          if (conversation) {
            const message = conversation.messages.find(msg => msg.id === aiMessage.id)
            if (message) {
              message.displayContent += chunk
            }
          }
        },
        // 完成回调
        (response) => {
          // 完成流式输出
          const conversation = conversations.value.find(conv => conv.id === currentConversation.value!.id)
          if (conversation) {
            const message = conversation.messages.find(msg => msg.id === aiMessage.id)
            if (message) {
              message.content = response.content
              message.isStreaming = false
              delete message.displayContent
              conversation.updatedAt = Date.now()
              saveConversations()
            }
          }
        },
        // 错误回调
        (error) => {
          console.error('发送消息失败:', error)
          
          // 处理错误情况
          const conversation = conversations.value.find(conv => conv.id === currentConversation.value!.id)
          if (conversation) {
            const message = conversation.messages.find(msg => msg.role === 'assistant' && msg.isStreaming)
            if (message) {
              message.content = '抱歉，AI回复时出现了错误。请稍后重试。'
              message.isStreaming = false
              delete message.displayContent
              conversation.updatedAt = Date.now()
              saveConversations()
            }
          }
        }
      )
      
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 处理错误情况
      const conversation = conversations.value.find(conv => conv.id === currentConversation.value!.id)
      if (conversation) {
        const message = conversation.messages.find(msg => msg.role === 'assistant' && msg.isStreaming)
        if (message) {
          message.content = '抱歉，AI回复时出现了错误。请稍后重试。'
          message.isStreaming = false
          delete message.displayContent
          conversation.updatedAt = Date.now()
          saveConversations()
        }
      }
    } finally {
      isLoading.value = false
    }
  }

  const clearAllConversations = () => {
    conversations.value = []
    currentConversationId.value = null
    saveConversations()
  }

  // 清空当前对话（用于新建对话）
  const clearCurrentConversation = () => {
    currentConversationId.value = null
    saveToLocalStorage('currentConversationId', null)
  }

  // 初始化时加载对话
  loadConversations()

  return {
    // 状态
    conversations: computed(() => conversations.value),
    currentConversation,
    currentConversationId: computed(() => currentConversationId.value),
    isLoading: computed(() => isLoading.value),
    
    // 方法
    loadConversations,
    saveConversations,
    createNewConversation,
    switchConversation,
    deleteConversation,
    updateConversationTitle,
    updateConversationSettings,
    addMessage,
    sendMessage,
    clearAllConversations,
    clearCurrentConversation
  }
})