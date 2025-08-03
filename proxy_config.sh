# 永久代理配置
# 将此文件内容添加到 ~/.bashrc 或 ~/.zshrc

# 获取 Windows 主机 IP
WINDOWS_HOST=$(grep nameserver /etc/resolv.conf | awk '{print $2}')

# 设置代理环境变量
export http_proxy=http://$WINDOWS_HOST:7890
export https_proxy=http://$WINDOWS_HOST:7890
export all_proxy=socks5://$WINDOWS_HOST:7891
export HTTP_PROXY=http://$WINDOWS_HOST:7890
export HTTPS_PROXY=http://$WINDOWS_HOST:7890
export ALL_PROXY=socks5://$WINDOWS_HOST:7891

# 配置 Git 代理
git config --global http.proxy http://$WINDOWS_HOST:7890
git config --global https.proxy http://$WINDOWS_HOST:7890

# 配置 npm 代理（如果需要）
# npm config set proxy http://$WINDOWS_HOST:7890
# npm config set https-proxy http://$WINDOWS_HOST:7890

# 配置 pip 代理（如果需要）
# pip config set global.proxy http://$WINDOWS_HOST:7890

echo "代理已配置: $http_proxy" 