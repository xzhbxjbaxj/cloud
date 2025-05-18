import os
import requests

# 从环境变量中读取用户名密码
USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

# 登录与续费 URL
LOGIN_URL = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL = "https://freecloud.ltd/server/detail/2378/renew"

# 浏览器头部伪装
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": LOGIN_URL,
    "Origin": "https://freecloud.ltd",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded"
}

# 登录表单字段
LOGIN_PAYLOAD = {
    "username": USERNAME,
    "password": PASSWORD,
    "mobile": "",
    "captcha": "",
    "verify_code": "",
    "agree": "1",
    "login_type": "PASS",
    "submit": "1"
}

# 续费表单字段
RENEW_PAYLOAD = {
    "month": "1",
    "calculate_only": "1",
    "submit": "1",
    "no_use_activity": "0"
}


def login_session():
    """模拟登录流程，返回已认证 session"""
    session = requests.Session()
    session.headers.update(HEADERS)

    print("📥 预加载登录页...")
    session.get(LOGIN_URL)  # 拿 cookie

    print("🔐 提交登录请求...")
    res = session.post(LOGIN_URL, data=LOGIN_PAYLOAD)
    res.raise_for_status()

    print("📦 登录成功，访问控制台...")
    session.get(CONSOLE_URL).raise_for_status()

    return session


def renew_server(session):
    """使用 session 发起续费请求"""
    print("🔁 发起续费请求...")
    res = session.post(RENEW_URL, data=RENEW_PAYLOAD)
    res.raise_for_status()

    try:
        resp = res.json()
    except Exception:
        print("❌ 非 JSON 响应：", res.text)
        raise

    if resp.get("code") == 1:
        print("✅ 续费成功：", resp)
    else:
        print("❌ 续费失败：", resp)
        raise RuntimeError("续费失败")


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise EnvironmentError("请设置环境变量 FC_USERNAME 和 FC_PASSWORD")
    sess = login_session()
    renew_server(sess)
