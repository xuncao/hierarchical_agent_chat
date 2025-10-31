/**
 * TypeScript类型定义文件
 * 用于前后端接口一致性
 */

// 基础枚举类型
export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
  TOOL = "tool"
}

export enum AgentType {
  RESEARCH = "research",
  WRITING = "writing",
  COORDINATOR = "coordinator"
}

export enum ModelProvider {
  DEEPSEEK = "deepseek",
  COHERE = "cohere",
  OPENAI = "openai",
  ANTHROPIC = "anthropic"
}

export enum StreamingMode {
  NONE = "none",
  SSE = "sse",
  WEBSOCKET = "websocket"
}

// 基础响应接口
export interface BaseResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ErrorResponse {
  success: false;
  error: string;
  code: string;
  details?: Record<string, any>;
}

// 分页相关接口
export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 聊天相关接口
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string;
  meta_info?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  agent_type: AgentType;
  model_provider: ModelProvider;
  model_name: string;
  streaming: boolean;
  streaming_mode: StreamingMode;
  max_tokens: number;
  temperature: number;
  use_search: boolean;
  deep_thought: boolean;
  custom_prompt?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  is_complete: boolean;
  timestamp: string;
  meta_info?: Record<string, any>;
}

export interface StreamingChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  is_complete: boolean;
  timestamp: string;
}

// 对话管理接口
export interface Conversation {
  id: string;
  title: string;
  user_id?: string;
  agent_type: AgentType;
  model_provider: ModelProvider;
  model_name: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  meta_info?: Record<string, any>;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  token_count: number;
  model_name: string;
  is_user_message: boolean;
  created_at: string;
  updated_at: string;
  meta_info?: Record<string, any>;
}

export interface ConversationHistory {
  conversation: Conversation;
  messages: ConversationMessage[];
  total_messages: number;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  page: number;
  page_size: number;
}

// 代理相关接口
export enum ToolType {
  SEARCH = "search",
  WEB_SCRAPER = "web_scraper",
  FILE_OPERATION = "file_operation",
  PYTHON_REPL = "python_repl",
  CHART_GENERATION = "chart_generation",
  NOTE_TAKING = "note_taking",
  DOCUMENT_WRITING = "document_writing"
}

export enum AgentRole {
  SUPERVISOR = "supervisor",
  WORKER = "worker",
  COORDINATOR = "coordinator"
}

export interface ToolDefinition {
  name: string;
  type: ToolType;
  description: string;
  parameters: Record<string, any>;
  is_enabled: boolean;
  meta_info?: Record<string, any>;
}

export interface AgentDefinition {
  name: string;
  role: AgentRole;
  agent_type: AgentType;
  description: string;
  model_provider: ModelProvider;
  model_name: string;
  temperature: number;
  max_tokens: number;
  tools: ToolDefinition[];
  capabilities: string[];
  is_enabled: boolean;
  meta_info?: Record<string, any>;
}

export interface TeamDefinition {
  name: string;
  agent_type: AgentType;
  description: string;
  supervisor: AgentDefinition;
  workers: AgentDefinition[];
  workflow_config: Record<string, any>;
  is_enabled: boolean;
  meta_info?: Record<string, any>;
}

export interface AgentStatus {
  agent_type: AgentType;
  is_available: boolean;
  last_activity: string;
  queue_size: number;
  error_count: number;
}

// 模型管理接口
export interface ModelInfo {
  provider: ModelProvider;
  name: string;
  display_name: string;
  max_tokens: number;
  is_available: boolean;
  supports_streaming: boolean;
  supports_search: boolean;
  description?: string;
}

export interface UsageStats {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  total_tokens: number;
  avg_response_time: number;
  last_updated: string;
}

// WebSocket事件类型
export enum WebSocketEventType {
  CHAT_MESSAGE = "chat_message",
  AGENT_STATUS = "agent_status",
  WORKFLOW_UPDATE = "workflow_update",
  ERROR = "error"
}

export interface WebSocketMessage<T = any> {
  type: WebSocketEventType;
  data: T;
  timestamp: string;
}

// API端点常量
export const API_ENDPOINTS = {
  // 聊天相关
  CHAT: "/api/chat",
  CHAT_STREAM: "/api/chat/stream",
  
  // 对话管理
  CONVERSATIONS: "/api/conversations",
  CONVERSATION_DETAIL: "/api/conversations/{id}",
  
  // 模型管理
  MODELS: "/api/models",
  MODEL_USAGE: "/api/models/{id}/usage",
  
  // 代理管理
  AGENTS: "/api/agents",
  AGENT_STATUS: "/api/agents/status",
  
  // WebSocket
  WS_CHAT: "/ws/chat",
  WS_AGENTS: "/ws/agents"
} as const;

// 配置常量
export const DEFAULT_CONFIG = {
  AGENT_TYPE: AgentType.COORDINATOR,
  MODEL_PROVIDER: ModelProvider.DEEPSEEK,
  MODEL_NAME: "deepseek-chat",
  STREAMING: true,
  STREAMING_MODE: StreamingMode.SSE,
  MAX_TOKENS: 2000,
  TEMPERATURE: 0.7,
  USE_SEARCH: false,
  DEEP_THOUGHT: false
} as const;

// 错误代码常量
export const ERROR_CODES = {
  // 通用错误
  VALIDATION_ERROR: "VALIDATION_ERROR",
  INTERNAL_ERROR: "INTERNAL_ERROR",
  NOT_FOUND: "NOT_FOUND",
  UNAUTHORIZED: "UNAUTHORIZED",
  FORBIDDEN: "FORBIDDEN",
  
  // 聊天相关错误
  CONVERSATION_NOT_FOUND: "CONVERSATION_NOT_FOUND",
  MESSAGE_TOO_LONG: "MESSAGE_TOO_LONG",
  MODEL_NOT_AVAILABLE: "MODEL_NOT_AVAILABLE",
  
  // 代理相关错误
  AGENT_NOT_AVAILABLE: "AGENT_NOT_AVAILABLE",
  AGENT_TIMEOUT: "AGENT_TIMEOUT",
  WORKFLOW_ERROR: "WORKFLOW_ERROR",
  
  // 工具相关错误
  TOOL_EXECUTION_ERROR: "TOOL_EXECUTION_ERROR",
  SEARCH_ERROR: "SEARCH_ERROR",
  FILE_OPERATION_ERROR: "FILE_OPERATION_ERROR"
} as const;