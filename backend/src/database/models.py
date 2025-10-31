"""
数据库模型定义
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Conversation(Base):
    """对话模型"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="新对话")
    user_id = Column(String(100), nullable=True, index=True)  # 支持多用户
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关系
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    meta_info = Column(JSON, default=dict)  # 存储额外信息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")


class UserPreference(Base):
    """用户偏好设置"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    default_model = Column(String(100), default="gpt-3.5-turbo")
    default_temperature = Column(Integer, default=70)  # 0-100范围
    default_max_tokens = Column(Integer, default=2048)
    preferred_team = Column(String(50), default="auto")  # auto, research, writing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelConfig(Base):
    """模型配置"""
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(100), nullable=False, unique=True, index=True)
    provider = Column(String(50), nullable=False)  # openai, cohere, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_tokens = Column(Integer, default=4096)
    capabilities = Column(JSON, default=list)  # 支持的功能列表
    is_available = Column(Boolean, default=True)
    requires_api_key = Column(Boolean, default=True)
    config = Column(JSON, default=dict)  # 模型特定配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UsageStat(Base):
    """使用统计"""
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    model_id = Column(String(100), nullable=False, index=True)
    request_type = Column(String(50), nullable=False)  # chat, stream, etc.
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AgentSession(Base):
    """代理会话记录"""
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    agent_type = Column(String(50), nullable=False)  # research, writing, supervisor
    initial_state = Column(JSON, default=dict)
    final_state = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ToolUsage(Base):
    """工具使用记录"""
    __tablename__ = "tool_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CacheEntry(Base):
    """缓存条目"""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)


class SystemLog(Base):
    """系统日志"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)