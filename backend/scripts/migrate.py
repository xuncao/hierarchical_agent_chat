#!/usr/bin/env python3
"""
数据库迁移脚本
"""

import asyncio
from src.database.database import engine, Base
from src.database.models import Conversation, Message, UserPreference, ModelConfig, UsageStat


async def create_tables():
    """创建数据库表"""
    print("开始创建数据库表...")
    
    async with engine.begin() as conn:
        # 删除现有表（开发环境）
        # await conn.run_sync(Base.meta_info.drop_all)
        
        # 创建新表
        await conn.run_sync(Base.meta_info.create_all)
    
    print("数据库表创建完成！")


async def seed_data():
    """种子数据（可选）"""
    print("添加种子数据...")
    
    # 这里可以添加一些初始数据
    # 例如默认模型配置、系统设置等
    
    print("种子数据添加完成！")


async def main():
    """主函数"""
    print("=" * 50)
    print("数据库迁移工具")
    print("=" * 50)
    
    try:
        await create_tables()
        await seed_data()
        
        print("=" * 50)
        print("数据库迁移完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"迁移失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())