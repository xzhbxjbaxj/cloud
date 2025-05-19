import os
import requests
import urllib3

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ 登录成功后导出的 Cookie，可以手动填入，或通过登录流程动态获取
COOKIES="sw110xy=hq17fleqsg3v09emh6dsij1tn6l5t6sq; cf_clearance=UBBlrexYwT..4zZIo87.V4n.1JjH9ZHihlx.0wuZFxY-1747619845-1.2.1.1-SO0kn6KLGpaKvt.AdsCtMpQclLKFbLke6J2ltHA50bp7BeuV6fJz8WUq6dZRu9sjgHS5tQDVj7Gmr_mvZjkVGjHK0PHg6j7eFULJnwaXLlcgw4Hi.oUW5oV.ZXK.54Ohjb7eSfhH.bjcwgpxACaRQyC8Fhz28NAkkfTIq1CNb8P0wA.maWm9lxLIywiqjHWc9J1vfXO0Kn6XxtArSTqC32F8Mo.ES_XzcAQe8NEhWb2_CEHTmaU1aaHXY5n6FJYBF1BW7Hl14BAA6b90D5fmXZ_V9V0Df_W5ZDB9ynsTPeHYaD7J3uWN7azn1K4IvG.1.OIlJNa6ghgKPAELHxPPPLzgfUDBm2w2qQgX06kZ94k"

def parse_cookie(cookie_str):
    cookies = {}
    for item in cookie_str.strip().split(";"):
        if "=" in item:
            k, v = item.strip().split("=", 1)
            cookies[k] = v
    return cookies

cookies = parse_cookie(COOKIES)

# 🌐 请求目标地址
RENEW_API = "https://freecloud.ltd/server/detail/2378/renew"

# 📦 请求载荷
RENEW_PAYLOAD = {
    "month": "1",
    "calculate_only": "1",
    "submit": "1",
    "no_use_activity": "0"
}

# 🚀 请求头（模拟浏览器行为）
HEADERS = {
    "Referer": "https://freecloud.ltd/server/detail/2378/renew",
    "Origin": "https://freecloud.ltd",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def renew():
    session = requests.Session()
    # session.cookies.update(COOKIES)

    try:
        print("📡 正在发起续费请求...")
        response = session.post(RENEW_API, data=RENEW_PAYLOAD, headers=HEADERS, cookies=cookies,verify=False)
        print(response.text)
        response.raise_for_status()

        data = response.json()

        if data.get("code") == 1:
            print("✅ 续费成功！")
            print("🔁 响应数据：", data)
        elif data.get("code") == 0:
            print("⚠️ 不在可续期范围内")
            print("🕒 到期时间戳：", data.get("time_end"))
        else:
            print("❌ 续费失败：", data)

    except requests.exceptions.SSLError as ssl_err:
        print("❌ SSL 错误：", ssl_err)
    except requests.exceptions.HTTPError as http_err:
        print("❌ HTTP 错误：", http_err)
    except Exception as e:
        print("❌ 其他错误：", e)

if __name__ == "__main__":
    renew()

