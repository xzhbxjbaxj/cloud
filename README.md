# ☁️ FreeCloud 自动续费器

> 基于 [Cloudflare Workers](https://workers.cloudflare.com/) + Python 脚本，实现对 [FreeCloud](https://freecloud.ltd) 免费服务器的自动续费。

---

## 📌 项目简介

本项目通过模拟登录和续费请求，帮助你每天自动续费 FreeCloud 提供的免费服务器，防止因忘记续费而服务中断。

- 🌐 `_worker.js` 运行于 Cloudflare Workers 中，模拟浏览器登录并发起续费请求。
- 🐍 `main.py` 是一个 Python 脚本，用于通过 HTTP 访问 Workers 接口，触发续费逻辑。
- ✅ 已实现基本风控规避：随机 UA、延迟行为等。
- 🔐 支持通过环境变量配置登录信息，避免泄露敏感信息。

---

## 🗂️ 文件结构

```
.
├── _worker.js    # 主续费逻辑，部署在 Cloudflare Workers
├── main.py       # 本地触发脚本，用于访问 Worker 接口
├── README.md     # 项目说明文档（本文件）
🔧 环境变量
Cloudflare Workers 环境变量：

在你的 Worker 项目中配置以下变量（通过 Dashboard 或 Wrangler 设置）：

变量名	描述
FREECLOUD_USERNAME	登录邮箱账号
FREECLOUD_PASSWORD	登录密码
ISN	服务器编号（数字 ID）

Python 环境变量：

设置 Worker 的访问地址：


复制
编辑
export FC_URL="https://your-worker-name.username.workers.dev"
🚀 部署方法
1️⃣ 部署 Cloudflare Worker
登录 Cloudflare，创建一个新的 Worker 项目。

将 _worker.js 内容粘贴进去。

在“变量”页面添加上述 3 个环境变量（账号、密码、ISN）。

保存并部署。

2️⃣ 本地使用 Python 脚本触发续费
确保你已经安装 Python 和 requests：

pip install requests
然后运行：
python main.py
✅ 成功后将输出如：“✅续费成功：当前剩余xx天” 或 “❌还有3天，暂不续费”。

⏱️ 自动定时运行（可选）
你可以使用 GitHub Actions、Linux cron、或者腾讯云函数等方式每天定时运行 main.py。

示例：Linux cron 任务
crontab -e
添加如下行，每天凌晨 3 点执行续费：

0 3 * * * export FC_URL="https://your-worker-name.username.workers.dev" && /usr/bin/python3 /path/to/main.py >> /path/to/log.txt 2>&1
🛡️ 安全与风控说明
随机浏览器 UA，每次访问模拟不同设备。

延迟执行逻辑，模仿真实用户行为。

使用环境变量存储密码，避免硬编码泄露。

建议不要频繁访问，一天最多运行一次。

📮 注意事项
本项目仅供个人学习交流使用，禁止用于任何恶意或违规行为。

若 FreeCloud 修改接口、增加 JS Challenge 或验证码机制，本项目可能需要更新。

使用前请自行评估风险，作者不对账号封禁或其他后果负责。

🧊 License
MIT License

❤️ 鸣谢
感谢 FreeCloud 提供的免费服务器资源。
