// 消息类型定义
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  isStreaming?: boolean;
}

// 模型类型定义
export interface Model {
  id: string;
  name: string;
  description?: string;
  maxTokens?: number;
}

// 对话类型定义
export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  model: string;
  deepThink: boolean;
  useSearch: boolean;
  createdAt: number;
  updatedAt: number;
}

// API请求参数
export interface ChatRequest {
  messages: Message[];
  model: string;
  deepThink: boolean;
  useSearch: boolean;
  conversationId?: string;
  message?: string;
}

// API响应类型
export interface ChatResponse {
  id: string;
  content: string;
  model: string;
  timestamp: number;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

// 对话设置类型
export interface ConversationSettings {
  model?: string;
  deepThink?: boolean;
  useSearch?: boolean;
}

// 本地存储键名
export const STORAGE_KEYS = {
  CONVERSATIONS: 'llm_conversations',
  CURRENT_CONVERSATION_ID: 'llm_current_conversation_id',
  MODELS: 'llm_models'
} as const;

// 应用状态类型
export interface AppState {
  conversations: Conversation[];
  currentConversationId: string | null;
  models: Model[];
  isLoading: boolean;
  isSidebarCollapsed: boolean;
}

// 组件Props类型
export interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

export interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

export interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean;
  selectedModel: string | null | undefined;
  onModelChange: (model: string) => void;
  deepThink: boolean;
  onDeepThinkChange: (value: boolean) => void;
  useSearch: boolean;
  onUseSearchChange: (value: boolean) => void;
  models: Model[];
}