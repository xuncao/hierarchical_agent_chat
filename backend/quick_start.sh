#!/bin/bash

# Hierarchical Agent Teams 后端服务快速启动脚本
# 一键启动，适合开发和测试环境

set -e

echo "🚀 Hierarchical Agent Teams 后端服务快速启动"
echo "=========================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11.9"

if [[ "$python_version" < "$required_version" ]]; then
    echo "❌ Python版本过低，需要3.11.9或更高版本，当前版本: $python_version"
    exit 1
else
    echo "✅ Python版本检查通过: $python_version"
fi

# 检查并安装依赖
echo "📦 检查依赖..."
if ! pip show fastapi uvicorn langgraph langchain > /dev/null 2>&1; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖检查通过"
fi

# 设置环境变量
echo "🔧 设置环境..."
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "✅ 已创建.env文件，请编辑配置API密钥"
    else
        echo "⚠️  未找到.env.example文件，使用默认配置"
    fi
else
    echo "✅ 环境变量文件存在"
fi

# 创建静态目录
mkdir -p static

# 启动服务
echo "🚀 启动服务..."
echo "   模式: 开发模式"
echo "   地址: 0.0.0.0"
echo "   端口: 8000"
echo ""
echo "📡 服务地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "❤️  健康检查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 启动服务
python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000