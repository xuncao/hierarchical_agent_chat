#!/bin/bash

# 依赖安装脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_warn "未找到Python3，请先安装Python 3.11.9或更高版本"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python版本: $python_version"
}

# 检查pip
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        log_warn "未找到pip3，尝试安装..."
        python3 -m ensurepip --upgrade
    fi
    
    pip_version=$(pip3 --version 2>&1 | awk '{print $2}')
    log_info "pip版本: $pip_version"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 升级pip
    pip3 install --upgrade pip
    
    # 安装核心依赖
    pip3 install -r requirements.txt
    
    # 安装开发依赖（可选）
    if [[ "$1" == "--dev" ]]; then
        log_info "安装开发依赖..."
        pip3 install pytest pytest-cov pytest-asyncio
        pip3 install black isort flake8 mypy
    fi
    
    log_info "依赖安装完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 检查核心包
    packages=("fastapi" "uvicorn" "langgraph" "langchain" "pydantic")
    
    for package in "${packages[@]}"; do
        if pip3 show "$package" > /dev/null 2>&1; then
            log_info "✓ $package 安装成功"
        else
            log_warn "✗ $package 安装失败"
        fi
    done
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  --dev          安装开发依赖"
    echo ""
    echo "示例:"
    echo "  $0             # 安装生产依赖"
    echo "  $0 --dev      # 安装开发依赖"
}

# 主函数
main() {
    local install_dev=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --dev)
                install_dev=true
                shift
                ;;
            *)
                echo "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "开始安装依赖..."
    
    check_python
    check_pip
    
    if [[ "$install_dev" == true ]]; then
        install_dependencies --dev
    else
        install_dependencies
    fi
    
    verify_installation
    
    log_info "安装完成！"
    echo ""
    echo "下一步:"
    echo "1. 复制环境配置: cp .env.example .env"
    echo "2. 编辑.env文件，配置API密钥"
    echo "3. 启动服务: ./scripts/start.sh"
}

# 运行主函数
main "$@"