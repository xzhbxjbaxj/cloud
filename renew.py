import os
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

async def main():
    async with async_playwright() as p:
        # ✅ 启动 headless + 绕过检测参数
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ]
        )

        context = await browser.new_context()

        # ✅ 注入脚本绕过 navigator.webdriver 检测
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = await context.new_page()

        print("🔐 打开登录页")
        

  

        print("📝 填写表单")
        await page.locator('input[placeholder="用户名/邮箱/手机号"]').fill(USERNAME)
        await page.locator('input[placeholder="请输入登录密码"]').fill(PASSWORD)
        await page.click('button[type="submit"]')

        # ✅ 等待跳转到登录成功后的页面
        await page.wait_for_url("**/member/index")

        print("🔁 跳转续费页")
        await page.goto("https://freecloud.ltd/server/detail/2378/renew")

        print("📨 提交续费")
        await page.click('button[type="submit"]')

        await page.wait_for_timeout(2000)
        print("✅ 续费完成")

        await browser.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise ValueError("环境变量 FC_USERNAME 和 FC_PASSWORD 未设置")
    asyncio.run(main())
