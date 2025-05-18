import os
import requests

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

LOGIN_URL   = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL   = "https://freecloud.ltd/server/detail/2378/renew"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://freecloud.ltd",
    "Referer": "https://freecloud.ltd/login"
}

LOGIN_PAYLOAD = {
    "username": USERNAME,
    "password": PASSWORD,
    "mobile": "",
    "captcha": "",
    "verify_code": "",
    "agree": "1",
    "login_type": "PASS",
    "submit": "1",
}

RENEW_PAYLOAD = {
    "month": "1",
    "calculate_only": "1",
    "submit": "1",
    "no_use_activity": "0",
}

def login_session():
    session = requests.Session()
    res = session.post(LOGIN_URL, headers=HEADERS, data=LOGIN_PAYLOAD, allow_redirects=True)
    res.raise_for_status()
    session.get(CONSOLE_URL).raise_for_status()
    return session

def renew_server(session):
    r = session.post(RENEW_URL, data=RENEW_PAYLOAD)
    r.raise_for_status()
    try:
        resp = r.json()
    except Exception:
        print("❌ 非 JSON 响应：", r.text)
        raise

    if resp.get("code") == 1:
        print("✅ 续费成功：", resp)
    else:
        print("❌ 续费失败响应：", resp)
        raise RuntimeError("续费未成功")

if __name__ == "__main__":
    sess = login_session()
    renew_server(sess)
