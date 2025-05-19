import asyncio
from playwright.async_api import async_playwright
import requests
import time

USERNAME = "abb295390@gmail.com"
PASSWORD = "123456789zyZY"

RENEW_URL = "https://freecloud.ltd/server/detail/2378/renew"

RENEW_PAYLOAD = {
    "month": "1",
    "calculate_only": "1",
    "submit": "1",
    "no_use_activity": "0"
}

HEADERS = {
    "Origin": "https://freecloud.ltd",
    "Referer": "https://freecloud.ltd/server/detail/2378/renew",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

async def get_cookies_via_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://freecloud.ltd/login", timeout=30000)
        await page.fill('input[name="username"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/member/index", timeout=15000)

        cookies = await context.cookies()
        await browser.close()
        return {cookie['name']: cookie['value'] for cookie in cookies}

def send_renew_request(cookies: dict):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(cookies)

    response = session.post(RENEW_URL, data=RENEW_PAYLOAD, verify=False)
    print("📨 响应状态码:", response.status_code)
    print("📨 响应内容:", response.text)

    try:
        data = response.json()
        if data.get("code") == 1:
            print("✅ 续费成功！")
        elif data.get("code") == 0:
            print("⚠️ 不在续费期内")
        else:
            print("❌ 续费失败：", data)
    except Exception as e:
        print("❌ 解析失败:", e)

async def main():
    cookies = await get_cookies_via_browser()
    send_renew_request(cookies)

if __name__ == "__main__":
    asyncio.run(main())

