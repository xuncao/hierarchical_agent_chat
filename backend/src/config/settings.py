"""应用配置设置"""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = "Hierarchical Agent Chat Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(False, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field("0.0.0.0", env="APP_HOST")
    PORT: int = Field(8000, env="APP_PORT")
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Hierarchical Agent Chat API"
    
    # CORS配置
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        env="ALLOWED_ORIGINS"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """将ALLOWED_ORIGINS字符串转换为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # 数据库配置
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./hierarchical_agent.db", env="DATABASE_URL")
    
    # JWT配置
    JWT_SECRET_KEY: str = Field("your_jwt_secret_key_here", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(1440, env="JWT_EXPIRE_MINUTES")
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: str = Field("", env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    
    # Cohere配置
    COHERE_API_KEY: str = Field("", env="COHERE_API_KEY")
    
    # Tavily配置
    TAVILY_API_KEY: str = Field("", env="TAVILY_API_KEY")
    
    # 代理配置
    DEFAULT_AGENT_TYPE: str = "coordinator"
    DEFAULT_MODEL_PROVIDER: str = "deepseek"
    DEFAULT_MODEL_NAME: str = "deepseek-chat"
    
    # 流式配置
    STREAMING_ENABLED: bool = True
    STREAMING_CHUNK_SIZE: int = 1024
    STREAMING_TIMEOUT: int = 300
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5分钟
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 安全配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 1分钟
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
        extra = "ignore"


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings