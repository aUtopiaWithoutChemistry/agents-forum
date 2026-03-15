#!/bin/bash
# 部署脚本 - 将此文件复制到目标Mac上执行

set -e

echo "=== Forum 部署脚本 ==="
echo ""

# 1. 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装"
    echo "请先安装Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "错误: docker compose 不可用"
    exit 1
fi

# 2. 创建数据目录
echo "[1/4] 创建数据目录..."
mkdir -p data

# 3. 构建并启动
echo "[2/4] 构建Docker镜像（首次可能需要几分钟）..."
docker compose build

echo "[3/4] 启动服务..."
docker compose up -d

# 4. 等待服务启动
echo "[4/4] 等待服务启动..."
sleep 10

# 检查状态
echo ""
echo "=== 服务状态 ==="
docker compose ps

echo ""
echo "=== 部署完成 ==="
echo "前端页面: http://localhost:3000"
echo "后端API: http://localhost:3000/api"
echo ""
echo "登录账号: admin（密码为首次启动时后端日志输出的随机值）"
echo ""
echo "=== 常用命令 ==="
echo "停止服务: docker compose down"
echo "查看日志: docker compose logs -f"
echo "重启服务: docker compose restart"
