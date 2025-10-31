#!/usr/bin/env python3
"""
Hierarchical Agent Teams 后端服务启动脚本
简便可复用的启动方式
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    import platform
    version = platform.python_version()
    required_version = (3, 11, 9)
    current_version = tuple(map(int, version.split('.')))
    
    if current_version < required_version:
        print(f"❌ Python版本过低，需要3.11.9或更高版本，当前版本: {version}")
        sys.exit(1)
    else:
        print(f"✅ Python版本检查通过: {version}")


def check_dependencies():
    """检查依赖"""
    print("📦 检查Python依赖...")
    
    try:
        import fastapi
        import uvicorn
        import langgraph
        import langchain
        print("✅ 核心依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")


def setup_environment():
    """设置环境变量"""
    print("🔧 设置环境变量...")
    
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ 已创建.env文件，请编辑配置API密钥")
        else:
            print("⚠️  未找到.env.example文件，使用默认配置")
    else:
        print("✅ 环境变量文件存在")


def create_static_directory():
    """创建静态文件目录"""
    static_dir = Path("static")
    if not static_dir.exists():
        static_dir.mkdir(exist_ok=True)
        print("✅ 创建静态文件目录")


def run_migrations():
    """运行数据库迁移"""
    print("🗄️  检查数据库...")
    
    try:
        # 检查是否需要运行迁移
        from src.database.database import engine
        from src.database.models import Base
        
        async def check_tables():
            import asyncio
            from sqlalchemy import inspect
            
            async with engine.begin() as conn:
                inspector = inspect(conn)
                tables = inspector.get_table_names()
                
                if not tables:
                    print("📊 创建数据库表...")
                    await conn.run_sync(Base.meta_info.create_all)
                    print("✅ 数据库表创建完成")
                else:
                    print("✅ 数据库表已存在")
        
        import asyncio
        asyncio.run(check_tables())
        
    except Exception as e:
        print(f"⚠️  数据库检查失败: {e}")
        print("继续启动服务...")


def start_service(mode="dev", host="0.0.0.0", port=8000):
    """启动服务"""
    print(f"🚀 启动服务...")
    print(f"   模式: {mode}")
    print(f"   地址: {host}")
    print(f"   端口: {port}")
    
    # 设置环境变量
    os.environ["APP_ENV"] = mode
    os.environ["APP_HOST"] = host
    os.environ["APP_PORT"] = str(port)
    
    if mode == "prod":
        os.environ["DEBUG"] = "False"
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.main:app",
            "--host", host,
            "--port", str(port),
            "--workers", "4"
        ]
    else:
        os.environ["DEBUG"] = "True"
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.main:app",
            "--reload",
            "--host", host,
            "--port", str(port)
        ]
    
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"❤️  健康检查: http://{host}:{port}/health")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Hierarchical Agent Teams 后端服务启动脚本")
    parser.add_argument("-m", "--mode", choices=["dev", "prod"], default="dev", 
                        help="运行模式: dev (开发) 或 prod (生产)")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="绑定地址")
    parser.add_argument("-p", "--port", type=int, default=8000, help="绑定端口")
    parser.add_argument("--check-only", action="store_true", help="只进行检查，不启动服务")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 Hierarchical Agent Teams 后端服务")
    print("=" * 60)
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    # 执行检查
    check_python_version()
    check_dependencies()
    setup_environment()
    create_static_directory()
    run_migrations()
    
    if args.check_only:
        print("✅ 检查完成，服务未启动")
        return
    
    # 启动服务
    start_service(args.mode, args.host, args.port)


if __name__ == "__main__":
    main()