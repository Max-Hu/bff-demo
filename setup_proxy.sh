#!/bin/bash

# WSL 代理配置脚本
# 使用方法: source setup_proxy.sh

# 获取 Windows 主机 IP
WINDOWS_HOST=$(grep nameserver /etc/resolv.conf | awk '{print $2}')

# Clash 默认端口
HTTP_PORT=7890
SOCKS_PORT=7891

echo "Windows 主机 IP: $WINDOWS_HOST"
echo "正在配置代理..."

# 设置代理环境变量
export http_proxy=http://$WINDOWS_HOST:$HTTP_PORT
export https_proxy=http://$WINDOWS_HOST:$HTTP_PORT
export all_proxy=socks5://$WINDOWS_HOST:$SOCKS_PORT
export HTTP_PROXY=http://$WINDOWS_HOST:$HTTP_PORT
export HTTPS_PROXY=http://$WINDOWS_HOST:$HTTP_PORT
export ALL_PROXY=socks5://$WINDOWS_HOST:$SOCKS_PORT

# 测试代理连接
echo "测试代理连接..."
if curl -s --connect-timeout 5 --proxy http://$WINDOWS_HOST:$HTTP_PORT https://www.google.com > /dev/null 2>&1; then
    echo "✅ 代理配置成功！"
    echo "HTTP 代理: $http_proxy"
    echo "HTTPS 代理: $https_proxy"
    echo "SOCKS 代理: $all_proxy"
else
    echo "❌ 代理连接失败"
    echo "请检查 Clash 是否启用了 '允许局域网连接' 选项"
    echo "或者检查 Clash 的端口配置"
fi

# 配置 Git 代理（可选）
echo "配置 Git 代理..."
git config --global http.proxy http://$WINDOWS_HOST:$HTTP_PORT
git config --global https.proxy http://$WINDOWS_HOST:$HTTP_PORT

echo "代理配置完成！" 