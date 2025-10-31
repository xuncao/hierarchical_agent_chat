"""FastAPI应用主入口"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from src.config.settings import settings
from src.models.base_models import BaseResponse, ErrorResponse

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("启动Hierarchical Agent Chat后端服务...")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
    # 初始化数据库连接
    # 初始化代理系统
    # 初始化缓存系统
    
    yield
    
    # 关闭时清理
    logger.info("关闭Hierarchical Agent Chat后端服务...")
    # 关闭数据库连接
    # 关闭代理系统
    # 清理缓存


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="基于LangGraph Hierarchical Agent Teams架构的大语言模型服务后端",
    docs_url=None if settings.APP_ENV == "production" else "/docs",
    redoc_url=None if settings.APP_ENV == "production" else "/redoc",
    openapi_url="/api/v1/openapi.json" if settings.APP_ENV != "production" else None,
    lifespan=lifespan
)


# 添加中间件

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 自定义异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    error_response = ErrorResponse(
        error=exc.detail,
        code="HTTP_ERROR",
        details={"status_code": exc.status_code}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    error_response = ErrorResponse(
        error="内部服务器错误",
        code="INTERNAL_ERROR",
        details={"message": str(exc)} if settings.DEBUG else {}
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


# 自定义文档页面
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI页面"""
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title=f"{settings.PROJECT_NAME} - API文档",
        swagger_favicon_url="/static/favicon.ico"
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return BaseResponse(
        success=True,
        message="服务运行正常",
        data={
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV
        }
    )


# API信息端点
@app.get("/api/v1/info")
async def api_info():
    """API信息端点"""
    return BaseResponse(
        success=True,
        message="API信息",
        data={
            "name": settings.PROJECT_NAME,
            "version": settings.APP_VERSION,
            "description": "基于LangGraph Hierarchical Agent Teams架构的大语言模型服务后端",
            "features": [
                "分层代理团队架构",
                "多模型支持（OpenAI、Cohere等）",
                "流式输出支持",
                "对话历史管理",
                "工具集成（搜索、文档处理等）"
            ],
            "supported_agents": ["research", "writing", "coordinator"],
            "supported_models": ["openai", "cohere"],
            "streaming_modes": ["sse", "websocket"]
        }
    )


# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# 导入路由
from src.api.routers import chat_router, model_router, system_router

# 注册路由
app.include_router(chat_router, prefix="/api/v1")
app.include_router(model_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )