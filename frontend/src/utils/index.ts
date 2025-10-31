import { type Conversation, type Message, type Model, STORAGE_KEYS } from '@/types'

// 生成唯一ID
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 格式化时间
export const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期
export const formatDate = (timestamp: number): string => {
  const now = new Date()
  const date = new Date(timestamp)
  
  if (date.toDateString() === now.toDateString()) {
    return '今天'
  }
  
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }
  
  return date.toLocaleDateString('zh-CN')
}

// 生成对话标题
export const generateConversationTitle = (firstMessage: string): string => {
  if (firstMessage.length <= 20) {
    return firstMessage
  }
  return firstMessage.substring(0, 20) + '...'
}

// 本地存储操作
export const storage = {
  // 保存对话列表
  saveConversations: (conversations: Conversation[]): void => {
    localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations))
  },
  
  // 获取对话列表
  getConversations: (): Conversation[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  },
  
  // 保存当前对话ID
  saveCurrentConversationId: (id: string | null): void => {
    if (id) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID, id)
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID)
    }
  },
  
  // 获取当前对话ID
  getCurrentConversationId: (): string | null => {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID)
  },
  
  // 保存模型列表
  saveModels: (models: Model[]): void => {
    localStorage.setItem(STORAGE_KEYS.MODELS, JSON.stringify(models))
  },
  
  // 获取模型列表
  getModels: (): Model[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.MODELS)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  }
}

// 默认模型列表
export const DEFAULT_MODELS: Model[] = [
  {
    id: 'deepseek-chat',
    name: 'DeepSeek Chat',
    description: '高性能、免费的AI助手',
    maxTokens: 32768
  },
]

// 创建新对话
export const createNewConversation = (model: string = DEFAULT_MODELS[0]!.id): Conversation => {
  const id = generateId()
  return {
    id,
    title: '新对话',
    messages: [],
    model,
    deepThink: false,
    useSearch: false,
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
}

// 创建新消息
export const createMessage = (role: 'user' | 'assistant', content: string): Message => {
  return {
    id: generateId(),
    role,
    content,
    timestamp: Date.now()
  }
}

// 模拟流式输出
export const simulateStreaming = async (
  content: string,
  onChunk: (chunk: string) => void,
  chunkDelay: number = 50
): Promise<void> => {
  const chunks = content.split('')
  
  for (const chunk of chunks) {
    await new Promise(resolve => setTimeout(resolve, chunkDelay))
    onChunk(chunk)
  }
}

// 获取默认模型
export const getDefaultModel = (): string => {
  const deepseekModel = DEFAULT_MODELS.find(model => model.id === 'deepseek-chat')
  return deepseekModel ? deepseekModel.id : DEFAULT_MODELS[0]!.id
}

// 保存到本地存储
export const saveToLocalStorage = (key: string, data: any): void => {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error('保存到本地存储失败:', error)
  }
}

// 从本地存储加载
export const loadFromLocalStorage = (key: string): any => {
  try {
    const data = localStorage.getItem(key)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('从本地存储加载失败:', error)
    return null
  }
}