"""
API路由模块
"""

from .chat_router import router as chat_router
from .model_router import router as model_router
from .system_router import router as system_router

__all__ = [
    "chat_router",
    "model_router", 
    "system_router"
]