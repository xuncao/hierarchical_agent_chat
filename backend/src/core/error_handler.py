"""
错误处理和监控系统
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

from ..database.database import get_db_session
from ..database.models import SystemLog, UsageStat


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def log_error(self, 
                       error: Exception, 
                       module: str = "unknown",
                       details: Optional[Dict[str, Any]] = None,
                       user_id: Optional[str] = None) -> None:
        """记录错误日志"""
        try:
            error_details = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if details:
                error_details.update(details)
            
            # 记录到系统日志
            async with get_db_session() as session:
                log_entry = SystemLog(
                    level="ERROR",
                    module=module,
                    message=f"{type(error).__name__}: {str(error)}",
                    details=error_details,
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            
            # 同时记录到标准日志
            self.logger.error(
                f"模块 {module} 发生错误: {error}",
                extra={"user_id": user_id, "details": error_details}
            )
            
        except Exception as log_error:
            # 如果日志记录失败，至少输出到控制台
            print(f"错误日志记录失败: {log_error}")
            print(f"原始错误: {error}")
    
    async def log_warning(self, 
                         message: str, 
                         module: str = "unknown",
                         details: Optional[Dict[str, Any]] = None,
                         user_id: Optional[str] = None) -> None:
        """记录警告日志"""
        try:
            warning_details = {
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if details:
                warning_details.update(details)
            
            # 记录到系统日志
            async with get_db_session() as session:
                log_entry = SystemLog(
                    level="WARNING",
                    module=module,
                    message=message,
                    details=warning_details,
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            
            # 同时记录到标准日志
            self.logger.warning(
                f"模块 {module} 警告: {message}",
                extra={"user_id": user_id, "details": warning_details}
            )
            
        except Exception as log_error:
            print(f"警告日志记录失败: {log_error}")
    
    async def log_info(self, 
                      message: str, 
                      module: str = "unknown",
                      details: Optional[Dict[str, Any]] = None,
                      user_id: Optional[str] = None) -> None:
        """记录信息日志"""
        try:
            info_details = {
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if details:
                info_details.update(details)
            
            # 记录到系统日志
            async with get_db_session() as session:
                log_entry = SystemLog(
                    level="INFO",
                    module=module,
                    message=message,
                    details=info_details,
                    created_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
            
            # 同时记录到标准日志
            self.logger.info(
                f"模块 {module}: {message}",
                extra={"user_id": user_id, "details": info_details}
            )
            
        except Exception as log_error:
            print(f"信息日志记录失败: {log_error}")


def error_handler(module: str = "unknown", log_error: bool = True):
    """
    错误处理装饰器
    
    Args:
        module: 模块名称
        log_error: 是否记录错误日志
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            
            try:
                return await func(*args, **kwargs)
            
            except Exception as error:
                if log_error:
                    # 提取用户ID（如果存在）
                    user_id = None
                    for arg in args:
                        if hasattr(arg, 'user_id'):
                            user_id = arg.user_id
                            break
                    
                    # 记录错误
                    await error_handler.log_error(
                        error=error,
                        module=module,
                        details={
                            "function": func.__name__,
                            "args": str(args),
                            "kwargs": str(kwargs)
                        },
                        user_id=user_id
                    )
                
                # 重新抛出异常
                raise
        
        return wrapper
    
    return decorator


def performance_monitor(operation_name: str):
    """
    性能监控装饰器
    
    Args:
        operation_name: 操作名称
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error_handler = ErrorHandler()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = int((time.time() - start_time) * 1000)  # 毫秒
                
                # 记录性能信息
                await error_handler.log_info(
                    message=f"{operation_name} 执行完成",
                    module="performance",
                    details={
                        "operation": operation_name,
                        "execution_time_ms": execution_time,
                        "function": func.__name__
                    }
                )
                
                return result
            
            except Exception as error:
                execution_time = int((time.time() - start_time) * 1000)
                
                # 记录错误性能信息
                await error_handler.log_error(
                    error=error,
                    module="performance",
                    details={
                        "operation": operation_name,
                        "execution_time_ms": execution_time,
                        "function": func.__name__,
                        "status": "failed"
                    }
                )
                
                raise
        
        return wrapper
    
    return decorator


class UsageTracker:
    """使用情况跟踪器"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
    
    async def track_usage(self, 
                         model_id: str,
                         request_type: str,
                         input_tokens: int = 0,
                         output_tokens: int = 0,
                         response_time_ms: int = 0,
                         success: bool = True,
                         error_message: Optional[str] = None,
                         user_id: Optional[str] = None,
                         meta_info: Optional[Dict[str, Any]] = None) -> None:
        """跟踪使用情况"""
        try:
            usage_stat = UsageStat(
                user_id=user_id,
                model_id=model_id,
                request_type=request_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message,
                meta_info=meta_info or {},
                created_at=datetime.utcnow()
            )
            
            async with get_db_session() as session:
                session.add(usage_stat)
                await session.commit()
            
        except Exception as error:
            await self.error_handler.log_error(
                error=error,
                module="usage_tracker",
                details={
                    "model_id": model_id,
                    "request_type": request_type,
                    "user_id": user_id
                }
            )


# 全局错误处理器实例
error_handler_instance = ErrorHandler()
usage_tracker = UsageTracker()