# WSL 代理配置指南

## 问题描述
WSL 在 NAT 模式下无法直接使用 Windows 上的 Clash 代理，需要特殊配置。

## 解决方案

### 方案 1: 配置 Clash 允许局域网连接

1. 打开 Clash for Windows
2. 进入 "General" 或 "设置" 页面
3. 找到 "Allow LAN" 或 "允许局域网连接" 选项并启用
4. 重启 Clash
5. 确认 Clash 监听端口（通常是 7890 和 7891）

### 方案 2: 使用代理配置脚本

```bash
# 运行代理配置脚本
source setup_proxy.sh
```

### 方案 3: 永久配置

将 `proxy_config.sh` 的内容添加到您的 shell 配置文件中：

```bash
# 添加到 ~/.bashrc
echo "source $(pwd)/proxy_config.sh" >> ~/.bashrc

# 或者添加到 ~/.zshrc（如果使用 zsh）
echo "source $(pwd)/proxy_config.sh" >> ~/.zshrc
```

### 方案 4: 手动配置

```bash
# 获取 Windows 主机 IP
WINDOWS_HOST=$(grep nameserver /etc/resolv.conf | awk '{print $2}')

# 设置代理环境变量
export http_proxy=http://$WINDOWS_HOST:7890
export https_proxy=http://$WINDOWS_HOST:7890
export all_proxy=socks5://$WINDOWS_HOST:7891
export HTTP_PROXY=http://$WINDOWS_HOST:7890
export HTTPS_PROXY=http://$WINDOWS_HOST:7890
export ALL_PROXY=socks5://$WINDOWS_HOST:7891
```

## 测试代理

```bash
# 测试 HTTP 代理
curl -I --proxy http://$WINDOWS_HOST:7890 https://www.google.com

# 测试 SOCKS 代理
curl -I --socks5 $WINDOWS_HOST:7891 https://www.google.com
```

## 常见问题

### 1. 连接被拒绝
- 检查 Clash 是否启用了"允许局域网连接"
- 检查防火墙设置
- 确认端口号是否正确

### 2. 代理不生效
- 确认环境变量已正确设置：`echo $http_proxy`
- 某些应用可能需要重启才能识别新的代理设置

### 3. Docker 使用代理
如果需要在 Docker 中使用代理，可以配置 Docker 代理：

```bash
# 创建 Docker 配置目录
sudo mkdir -p /etc/systemd/system/docker.service.d

# 创建代理配置文件
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=http://$WINDOWS_HOST:7890"
Environment="HTTPS_PROXY=http://$WINDOWS_HOST:7890"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# 重启 Docker 服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 注意事项

1. 每次 WSL 重启后，Windows 主机 IP 可能会变化
2. 确保 Clash 在 Windows 上正常运行
3. 某些应用可能需要特殊的代理配置
4. 建议在 `.bashrc` 或 `.zshrc` 中动态获取 Windows 主机 IP 