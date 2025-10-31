"""
数据库连接和会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..config.settings import settings

# 创建异步数据库引擎
if settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
else:
    # 开发环境使用SQLite
    engine = create_async_engine(
        "sqlite+aiosqlite:///./hierarchical_agent.db",
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库，创建所有表
    """
    from .models import Base
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.meta_info.create_all)
    
    print("数据库初始化完成")


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
    print("数据库连接已关闭")