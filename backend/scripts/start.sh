#!/bin/bash

# Hierarchical Agent Teams 后端服务启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python_version() {
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local required_version="3.11.9"
    
    if [[ "$python_version" < "$required_version" ]]; then
        log_error "Python版本过低，需要3.11.9或更高版本，当前版本: $python_version"
        exit 1
    else
        log_info "Python版本检查通过: $python_version"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查Python依赖..."
    
    if ! pip show fastapi uvicorn langgraph langchain > /dev/null 2>&1; then
        log_warn "缺少核心依赖，开始安装..."
        pip install -r requirements.txt
    else
        log_info "核心依赖检查通过"
    fi
}

# 检查环境变量
check_env() {
    log_info "检查环境变量配置..."
    
    if [[ ! -f ".env" ]]; then
        log_warn "未找到.env文件，使用默认配置"
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log_info "已创建.env文件，请编辑配置API密钥"
        fi
    else
        log_info "环境变量文件存在"
    fi
}

# 启动服务
start_service() {
    local mode="${1:-dev}"
    local host="${2:-0.0.0.0}"
    local port="${3:-8000}"
    
    log_info "启动服务..."
    log_info "模式: $mode"
    log_info "地址: $host"
    log_info "端口: $port"
    
    if [[ "$mode" == "prod" ]]; then
        uvicorn src.main:app --host "$host" --port "$port" --workers 4
    else
        uvicorn src.main:app --reload --host "$host" --port "$port"
    fi
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help           显示帮助信息"
    echo "  -m, --mode MODE       运行模式 (dev|prod)，默认: dev"
    echo "  -H, --host HOST       绑定地址，默认: 0.0.0.0"
    echo "  -p, --port PORT       绑定端口，默认: 8000"
    echo "  --check-only         只进行检查，不启动服务"
    echo ""
    echo "示例:"
    echo "  $0                    # 开发模式启动"
    echo "  $0 -m prod -p 8080   # 生产模式，端口8080"
}

# 主函数
main() {
    local mode="dev"
    local host="0.0.0.0"
    local port="8000"
    local check_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -m|--mode)
                mode="$2"
                shift 2
                ;;
            -H|--host)
                host="$2"
                shift 2
                ;;
            -p|--port)
                port="$2"
                shift 2
                ;;
            --check-only)
                check_only=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证模式参数
    if [[ "$mode" != "dev" && "$mode" != "prod" ]]; then
        log_error "无效的运行模式: $mode，必须是dev或prod"
        exit 1
    fi
    
    # 执行检查
    check_python_version
    check_dependencies
    check_env
    
    if [[ "$check_only" == true ]]; then
        log_info "检查完成，服务未启动"
        exit 0
    fi
    
    # 启动服务
    start_service "$mode" "$host" "$port"
}

# 捕获中断信号
trap 'log_info "服务停止"; exit 0' INT TERM

# 运行主函数
main "$@"