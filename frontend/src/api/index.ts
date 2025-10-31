import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type { ChatRequest, ChatResponse, Model } from '@/types'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)

    // 详细的错误处理
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('认证失败，请重新登录')
          break
        case 403:
          console.error('权限不足')
          break
        case 404:
          console.error('API接口不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        case 502:
          console.error('网关错误，后端服务不可用')
          break
        case 503:
          console.error('服务暂时不可用')
          break
        default:
          console.error('请求失败，状态码:', error.response.status)
      }
    } else if (error.request) {
      console.error('网络错误，请检查网络连接')
    } else {
      console.error('请求配置错误:', error.message)
    }

    return Promise.reject(error)
  }
)

// API接口定义
export const chatAPI = {
  // 获取模型列表
  getModels: async (): Promise<Model[]> => {
    try {
      const response: AxiosResponse<any> = await api.get('/models')
      // 后端返回格式为 { success: boolean, message: string, data: { models: Model[] } }
      if (response.data.success && response.data.data.models) {
        return response.data.data.models.map((model: any) => ({
          id: model.name,
          name: model.display_name,
          description: model.description,
          maxTokens: model.max_tokens
        }))
      }
      throw new Error('API返回格式错误')
    } catch (error) {
      console.warn('使用模拟模型数据:', error)
      // 返回默认模型列表作为fallback
      return [
        {
          id: 'deepseek-chat',
          name: 'DeepSeek Chat',
          description: '高性能、免费的AI助手',
          maxTokens: 32768,
        },
      ]
    }
  },

  // 发送对话请求（流式响应）
  sendMessage: async (
    request: ChatRequest,
    onChunk?: (chunk: string) => void,
    onComplete?: (response: ChatResponse) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    try {
      const token = localStorage.getItem('auth_token')
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }

      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      // 使用流式聊天接口
      const response = await fetch(`${api.defaults.baseURL}/chat/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message: request.message,
          model_name: request.model,
          deep_thought: request.deepThink,
          use_search: request.useSearch,
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法读取响应流')
      }

      let accumulatedContent = ''
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)

            if (data === '[DONE]') {
              // 流式传输完成
              if (onComplete) {
                onComplete({
                  id: Date.now().toString(),
                  content: accumulatedContent,
                  model: request.model,
                  timestamp: Date.now(),
                })
              }
              return
            }

            try {
              // 后端流式输出格式为纯文本，直接使用内容
              accumulatedContent += data
              if (onChunk) {
                onChunk(data)
              }
            } catch (e) {
              console.warn('解析数据块失败:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat API error:', error)
      if (onError) {
        onError(error as Error)
      } else {
        // 如果没有提供错误处理回调，使用模拟API
        console.warn('使用模拟API进行回复')
        await chatAPI.sendMessageMock(request, onChunk, onComplete, onError)
      }
    }
  },

  // 模拟对话API（用于开发测试）
  sendMessageMock: async (
    request: ChatRequest,
    onChunk?: (chunk: string) => void,
    onComplete?: (response: ChatResponse) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 500))

      const thinkingProcess = request.deepThink ?
        '\n\n🤔 深度思考过程：\n- 分析问题背景\n- 检索相关知识\n- 构建回答框架\n- 完善细节内容\n' : ''

      const searchInfo = request.useSearch ?
        '\n🔍 已启用联网搜索，获取最新信息...\n' : ''

      const mockResponse = `这是${request.model}的回复：${request.message}${thinkingProcess}${searchInfo}\n\n当前设置：\n- 模型：${request.model}\n- 深度思考：${request.deepThink ? '开启' : '关闭'}\n- 联网搜索：${request.useSearch ? '开启' : '关闭'}`

      // 模拟流式输出
      const chunks = mockResponse.split('')
      let accumulatedContent = ''

      for (const chunk of chunks) {
        await new Promise(resolve => setTimeout(resolve, 20 + Math.random() * 30))
        accumulatedContent += chunk
        if (onChunk) {
          onChunk(chunk)
        }
      }

      if (onComplete) {
        onComplete({
          id: Date.now().toString(),
          content: accumulatedContent,
          model: request.model,
          timestamp: Date.now()
        })
      }
    } catch (error) {
      console.error('Mock API error:', error)
      if (onError) {
        onError(error as Error)
      }
    }
  }
}

// 工具函数：检查API连接状态
export const checkApiStatus = async (): Promise<boolean> => {
  try {
    const response = await api.get('/system/health')
    return response.status === 200 && response.data.success
  } catch (error) {
    return false
  }
}

// 工具函数：获取API基本信息
export const getApiInfo = async () => {
  try {
    const response = await api.get('/system/info')
    if (response.data.success) {
      return response.data.data
    }
    throw new Error('API返回格式错误')
  } catch (error) {
    return {
      name: 'Mock API',
      version: '1.0.0',
      status: '模拟模式',
      message: '后端API不可用，使用模拟数据'
    }
  }
}

// 导出默认实例
export default api