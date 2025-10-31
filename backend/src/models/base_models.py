"""基础数据模型定义"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AgentType(str, Enum):
    """代理类型枚举"""
    RESEARCH = "research"
    WRITING = "writing"
    COORDINATOR = "coordinator"


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    DEEPSEEK = "deepseek"
    COHERE = "cohere"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class StreamingMode(str, Enum):
    """流式模式枚举"""
    NONE = "none"
    SSE = "sse"
    WEBSOCKET = "websocket"


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="请求是否成功")
    error: str = Field(..., description="错误信息")
    code: str = Field(..., description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(..., description="数据项列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


class TimestampMixin(BaseModel):
    """时间戳混合模型"""
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class IDMixin(BaseModel):
    """ID混合模型"""
    id: str = Field(..., description="唯一标识符")