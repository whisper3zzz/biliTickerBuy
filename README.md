<div align="center">
  <a href="https://github.com/mikumifa/biliTickerBuy" target="_blank">
    <img width="160" src="assets/icon.ico" alt="logo">
  </a>
  <h2 id="koishi">biliTickerBuy</h1>

<p>
  <!-- GitHub Downloads -->
  <a href="https://github.com/mikumifa/biliTickerBuy/releases">
    <img src="https://img.shields.io/github/downloads/mikumifa/biliTickerBuy/total" alt="GitHub all releases">
  </a>
  <!-- GitHub Release Version -->
  <a href="https://github.com/mikumifa/biliTickerBuy/releases">
    <img src="https://img.shields.io/github/v/release/mikumifa/biliTickerBuy" alt="GitHub release (with filter)">
  </a>
  <!-- GitHub Issues -->
  <a href="https://github.com/mikumifa/biliTickerBuy/issues">
    <img src="https://img.shields.io/github/issues/mikumifa/biliTickerBuy" alt="GitHub issues">
  </a>
  <!-- GitHub Stars -->
  <a href="https://github.com/mikumifa/biliTickerBuy/stargazers">
    <img src="https://img.shields.io/github/stars/mikumifa/biliTickerBuy" alt="GitHub Repo stars">
  </a>
</p>
<a href="https://trendshift.io/repositories/11145" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11145" alt="mikumifa%2FbiliTickerBuy | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

这是一个开源免费，简单易用的 B 站会员购辅助工具

</div>

## 💻 快速安装

方法一: 从 github 上[下载](https://github.com/mikumifa/biliTickerBuy/releases)

方法二: 如果没有您使用系统的已构建版本，请前往[指南](https://github.com/mikumifa/biliTickerBuy/wiki/Docker%E8%BF%90%E8%A1%8C%E6%96%B9%E6%B3%95)

方法三: 仓库支持通过 `pip install bilitickerbuy` 安装，安装后可以直接使用 `btb` 命令运行。示例：

```bash
# 直接启动ui
btb
# 根据配置文件购票
btb buy ./your_config.json
```

## 🖥️ 命令行模式（适用于远程 Linux 服务器）

本项目支持纯命令行操作，无需图形界面，适合在远程服务器上使用。

### 基础使用流程

```bash
# 1. 扫码登录（在终端显示二维码）
btb login

# 2. 查询票务信息
btb info https://show.bilibili.com/platform/detail.html?id=84096

# 3. 交互式生成抢票配置
btb config

# 4. 开始抢票
btb buy ./your_config.json

# 5. 定时抢票（指定开售时间）
btb buy ./your_config.json --time_start 2024-01-01T10:00:00
```

### 命令详细说明

#### 1. 登录相关命令

```bash
# 扫码登录（推荐）
btb login

# 查看当前登录状态
btb login --status

# 注销当前账号
btb login --logout

# 使用 cookies 文件登录
btb login --cookies ./cookies.json
```

#### 2. 配置生成命令

```bash
# 交互式生成抢票配置文件
btb config

# 指定使用特定的 cookies 文件
btb config --cookies_file ./cookies.json
```

#### 3. 票务信息查询

```bash
# 查询票务信息
btb info https://show.bilibili.com/platform/detail.html?id=84096
```

#### 4. 抢票命令（完整选项）

```bash
# 基础抢票
btb buy ./tickets.json

# 设置请求间隔（毫秒），默认 1000ms
btb buy ./tickets.json --interval 500

# 定时开始抢票
btb buy ./tickets.json --time_start 2024-01-01T10:00:00

# 使用代理
btb buy ./tickets.json --https_proxys http://127.0.0.1:8080

# 自定义 endpoint URL
btb buy ./tickets.json --endpoint_url https://your-endpoint.com

# 启用 Web UI 界面（在网页中查看日志）
btb buy ./tickets.json --web

# 隐藏失败时的随机消息
btb buy ./tickets.json --hide_random_message
```

> **日志显示方式说明：** 在 Web UI 的"开始抢票"页面，可选择日志显示方式：
> - **网页**：日志实时显示在浏览器页面中（所有平台均支持）
> - **终端**：在独立终端窗口中显示日志（支持 Windows 和 macOS）
>   - Windows：在新的命令提示符窗口中运行
>   - macOS：通过 Terminal.app 打开新窗口运行，任务结束后按 Enter 关闭

#### 5. 通知配置

抢票成功/失败时可通过多种方式推送通知：

```bash
# 音频通知
btb buy ./tickets.json --audio_path ./success.mp3

# PushPlus 推送
btb buy ./tickets.json --pushplusToken YOUR_TOKEN

# ServerChan 推送
btb buy ./tickets.json --serverchanKey YOUR_KEY

# ServerChan3 推送
btb buy ./tickets.json --serverchan3ApiUrl YOUR_API_URL

# Bark 推送（iOS）
btb buy ./tickets.json --barkToken YOUR_TOKEN

# Ntfy 推送
btb buy ./tickets.json --ntfy_url https://ntfy.sh/your-topic --ntfy_username user --ntfy_password pass
```

#### 6. Web UI 模式（图形界面）

```bash
# 启动 Web UI（默认 127.0.0.1:7860）
btb

# 自定义端口和地址
btb --server_name 0.0.0.0 --port 8080

# 公网分享（生成临时公网链接）
btb --share
```

### 环境变量配置

命令行参数也可以通过环境变量设置（适合 Docker 部署）：

| 环境变量 | 对应参数 | 说明 |
|---------|---------|------|
| `BTB_SHARE` | `--share` | 是否分享公网链接 |
| `BTB_SERVER_NAME` | `--server_name` | 服务器地址 |
| `BTB_PORT` | `--port` | 服务器端口 |
| `BTB_ENDPOINT_URL` | `--endpoint_url` | Endpoint URL |
| `BTB_TIME_START` | `--time_start` | 开始时间 |
| `BTB_HTTPS_PROXYS` | `--https_proxys` | HTTPS 代理 |
| `BTB_AUDIO_PATH` | `--audio_path` | 音频文件路径 |
| `BTB_PUSHPLUSTOKEN` | `--pushplusToken` | PushPlus Token |
| `BTB_SERVERCHANKEY` | `--serverchanKey` | ServerChan Key |
| `BTB_SERVERCHAN3APIURL` | `--serverchan3ApiUrl` | ServerChan3 API URL |
| `BTB_BARKTOKEN` | `--barkToken` | Bark Token |
| `BTB_NTFY_URL` | `--ntfy_url` | Ntfy 服务器 URL |
| `BTB_NTFY_USERNAME` | `--ntfy_username` | Ntfy 用户名 |
| `BTB_NTFY_PASSWORD` | `--ntfy_password` | Ntfy 密码 |

示例：

```bash
export BTB_PORT=8080
export BTB_SERVER_NAME=0.0.0.0
btb
```

### Docker 部署示例

```bash
# 使用环境变量运行
docker run -d \
  -p 7860:7860 \
  -e BTB_SERVER_NAME=0.0.0.0 \
  -e BTB_PUSHPLUSTOKEN=your_token \
  -v $(pwd)/config:/app/config \
  bilitickerbuy:latest

# 命令行模式运行
docker run -it \
  -v $(pwd)/config:/app/config \
  bilitickerbuy:latest \
  btb buy /app/config/tickets.json --interval 500
```

## 👀 使用说明书

前往飞书： https://n1x87b5cqay.feishu.cn/wiki/Eg4xwt3Dbiah02k1WqOcVk2YnMd

## ❗ 项目问题

程序使用问题： [点此链接前往 discussions](https://github.com/mikumifa/biliTickerBuy/discussions)

反馈程序 BUG 或者提新功能建议： [点此链接向项目提出反馈 BUG](https://github.com/mikumifa/biliTickerBuy/issues/new/choose)

## 📩 免责声明

本项目遵循 MIT License 许可协议，仅供个人学习与研究使用。请勿将本项目用于任何商业牟利行为，亦严禁用于任何形式的代抢、违法行为或违反相关平台规则的用途。由此产生的一切后果均由使用者自行承担，与本人无关。

若您 fork 或使用本项目，请务必遵守相关法律法规与目标平台规则。

## 💡 关于访问频率与并发控制

本项目在设计时严格遵循「非侵入式」原则，避免对目标服务器（如 Bilibili）造成任何干扰。

所有网络请求的时间间隔均由用户自行配置，默认值模拟正常用户的手动操作速度。程序默认单线程运行，无并发任务。遇到请求失败时，程序会进行有限次数的重试，并在重试之间加入适当的延时，避免形成高频打点。项目完全依赖平台公开接口及网页结构，不含风控规避、API 劫持等破坏性手段。

## 🛡️ 平台尊重声明

本程序设计时已尽可能控制请求频率，避免对 Bilibili 服务器造成任何明显负载或影响。项目仅作为学习用途，不具备大规模、高并发的能力，亦无任何恶意行为或干扰服务的企图。

如本项目中存在侵犯 Bilibili 公司合法权益的内容，请通过邮箱 [1055069518@qq.com](mailto:1055069518@qq.com) 与我联系，我将第一时间下架相关内容并删除本仓库。对此造成的不便，我深表歉意，感谢您的理解与包容。

## 🤩 项目贡献者

<a href="https://github.com/mikumifa/biliTickerBuy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=mikumifa/biliTickerBuy&preview=true&max=&columns=" />
</a>
<br /><br />

## ⭐️ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mikumifa/biliTickerBuy&type=Date)](https://www.star-history.com/#mikumifa/biliTickerBuy&Date)
