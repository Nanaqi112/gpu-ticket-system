#!/bin/bash

# GPU维修工单系统管理脚本

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 显示帮助信息
show_help() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    GPU维修工单系统管理脚本${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "用法: ${YELLOW}./gpu-tickets.sh <命令>${NC}"
    echo ""
    echo -e "可用命令:"
    echo -e "  ${GREEN}start${NC}     启动服务（构建镜像+初始化数据库+创建管理员）"
    echo -e "  ${GREEN}stop${NC}      停止服务"
    echo -e "  ${GREEN}restart${NC}   重启服务"
    echo -e "  ${GREEN}status${NC}    查看服务状态"
    echo -e "  ${GREEN}logs${NC}      查看服务日志"
    echo -e "  ${GREEN}init${NC}      初始化管理员账号"
    echo -e "  ${GREEN}help${NC}      显示此帮助信息"
    echo ""
}

# 检查Docker环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: 未安装Docker，请先安装Docker${NC}"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: 未安装Docker Compose，请先安装${NC}"
        exit 1
    fi
}

# 启动服务
start() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    GPU维修工单系统 - 启动服务${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    check_docker

    # 停止可能存在的旧容器
    echo -e "${YELLOW}[1/6] 清理旧容器...${NC}"
    docker compose down 2>/dev/null || true

    # 构建镜像
    echo -e "${YELLOW}[2/6] 构建Docker镜像...${NC}"
    docker compose build

    # 启动服务
    echo -e "${YELLOW}[3/6] 启动服务...${NC}"
    docker compose up -d

    # 等待数据库就绪
    echo -e "${YELLOW}[4/6] 等待数据库就绪...${NC}"
    sleep 15

    # 初始化数据库
    echo -e "${YELLOW}[5/6] 初始化数据库...${NC}"
    docker compose exec -T app python manage.py migrate --run-syncdb 2>/dev/null || true

    # 创建管理员账号
    echo -e "${YELLOW}[6/6] 创建管理员账号...${NC}"
    docker compose exec -T app python manage.py init_admin

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    系统启动成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "访问地址:"
    echo -e "  前端页面:     ${GREEN}http://localhost${NC}"
    echo -e "  后端API:      ${GREEN}http://localhost/api/${NC}"
    echo -e "  管理后台:     ${GREEN}http://localhost/admin/${NC}"
    echo ""
    echo -e "管理后台账号: ${GREEN}admin${NC}"
    echo -e "管理后台密码: ${GREEN}admin2026${NC}"
    echo ""
}

# 停止服务
stop() {
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}    GPU维修工单系统 - 停止服务${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""

    docker compose down

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    服务已停止${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 重启服务
restart() {
    echo -e "${BLUE}正在重启服务...${NC}"
    echo ""
    stop
    echo ""
    start
}

# 查看状态
status() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    GPU维修工单系统 - 服务状态${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    docker compose ps
    echo ""
}

# 查看日志
logs() {
    docker compose logs -f
}

# 初始化管理员
init_admin() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    初始化管理员账号${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    docker compose exec app python manage.py init_admin

    echo ""
    echo -e "管理员账号: ${GREEN}admin${NC}"
    echo -e "管理员密码: ${GREEN}admin2026${NC}"
    echo ""
}

# 主逻辑
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    init)
        init_admin
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac