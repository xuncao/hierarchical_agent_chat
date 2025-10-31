"""
缓存系统 - 提供内存和数据库缓存支持
"""

import asyncio
import json
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps

from ..database.database import get_db_session
from ..database.models import CacheEntry


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.memory_cache = {}
        self.default_ttl = 3600  # 默认缓存时间1小时
    
    async def get(self, key: str, use_db: bool = True) -> Optional[Any]:
        """获取缓存值"""
        # 先检查内存缓存
        if key in self.memory_cache:
            cached_data, expires_at = self.memory_cache[key]
            if expires_at > time.time():
                return cached_data
            else:
                # 内存缓存过期，删除
                del self.memory_cache[key]
        
        # 检查数据库缓存
        if use_db:
            async with get_db_session() as session:
                cache_entry = await session.query(CacheEntry).filter(
                    CacheEntry.key == key,
                    CacheEntry.expires_at > datetime.utcnow()
                ).first()
                
                if cache_entry:
                    # 更新访问时间和计数
                    cache_entry.accessed_at = datetime.utcnow()
                    cache_entry.access_count += 1
                    await session.commit()
                    
                    # 同时更新到内存缓存
                    value = json.loads(cache_entry.value)
                    expires_at = cache_entry.expires_at.timestamp() if cache_entry.expires_at else None
                    if expires_at:
                        self.memory_cache[key] = (value, expires_at)
                    
                    return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, use_db: bool = True) -> bool:
        """设置缓存值"""
        try:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            # 设置内存缓存
            self.memory_cache[key] = (value, expires_at)
            
            # 设置数据库缓存
            if use_db:
                expires_dt = datetime.utcnow() + timedelta(seconds=ttl)
                cache_value = json.dumps(value)
                
                async with get_db_session() as session:
                    cache_entry = await session.query(CacheEntry).filter(
                        CacheEntry.key == key
                    ).first()
                    
                    if cache_entry:
                        # 更新现有缓存
                        cache_entry.value = cache_value
                        cache_entry.expires_at = expires_dt
                        cache_entry.accessed_at = datetime.utcnow()
                        cache_entry.access_count += 1
                    else:
                        # 创建新缓存
                        cache_entry = CacheEntry(
                            key=key,
                            value=cache_value,
                            expires_at=expires_dt,
                            accessed_at=datetime.utcnow(),
                            access_count=1
                        )
                        session.add(cache_entry)
                    
                    await session.commit()
            
            return True
            
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str, use_db: bool = True) -> bool:
        """删除缓存值"""
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除数据库缓存
            if use_db:
                async with get_db_session() as session:
                    cache_entry = await session.query(CacheEntry).filter(
                        CacheEntry.key == key
                    ).first()
                    
                    if cache_entry:
                        await session.delete(cache_entry)
                        await session.commit()
            
            return True
            
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    async def clear_expired(self) -> int:
        """清理过期缓存"""
        try:
            cleared_count = 0
            
            # 清理内存缓存
            current_time = time.time()
            expired_keys = [
                key for key, (_, expires_at) in self.memory_cache.items()
                if expires_at <= current_time
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleared_count += 1
            
            # 清理数据库缓存
            async with get_db_session() as session:
                expired_entries = await session.query(CacheEntry).filter(
                    CacheEntry.expires_at <= datetime.utcnow()
                ).all()
                
                for entry in expired_entries:
                    await session.delete(entry)
                    cleared_count += 1
                
                await session.commit()
            
            return cleared_count
            
        except Exception as e:
            print(f"清理过期缓存失败: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 内存缓存统计
            memory_stats = {
                "total_entries": len(self.memory_cache),
                "memory_usage": sum(len(str(v)) for v in self.memory_cache.values())
            }
            
            # 数据库缓存统计
            async with get_db_session() as session:
                db_stats = await session.query(CacheEntry).count()
                active_entries = await session.query(CacheEntry).filter(
                    CacheEntry.expires_at > datetime.utcnow()
                ).count()
            
            return {
                "memory_cache": memory_stats,
                "database_cache": {
                    "total_entries": db_stats,
                    "active_entries": active_entries
                }
            }
            
        except Exception as e:
            print(f"获取缓存统计失败: {e}")
            return {}


def cache_result(ttl: int = 3600, key_func: Optional[callable] = None):
    """
    缓存装饰器 - 缓存函数结果
    
    Args:
        ttl: 缓存时间（秒）
        key_func: 自定义缓存键生成函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认缓存键：函数名 + 参数哈希
                import hashlib
                param_str = f"{args}_{kwargs}"
                param_hash = hashlib.md5(param_str.encode()).hexdigest()
                cache_key = f"{func.__module__}.{func.__name__}:{param_hash}"
            
            # 尝试从缓存获取
            cache_manager = CacheManager()
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    
    return decorator


# 全局缓存管理器实例
cache_manager = CacheManager()