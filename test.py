import os
import asyncio
import random
from playwright.async_api import async_playwright

USERNAME = "abb295390@gmail.com"
PASSWORD = "123456789zyZY"

async def human_behavior_simulation(page):
    # 模拟人类行为以减少被检测为自动化脚本的风险
    await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """)
    await page.emulate_media(color_scheme="dark")

async def handle_loading(page):
    """处理加载提示"""
    try:
        loading = await page.wait_for_selector("text='just a moment'", timeout=5000)
        if loading:
            print("⏳ 检测到加载提示，等待1秒...")
            await asyncio.sleep(1)
            return True
    except:
        return False

async def submit_click_handler(page, element):
    """优化的点击处理"""
    await element.scroll_into_view_if_needed()
    await asyncio.sleep(random.uniform(0.3, 0.8))  # 减少等待时间以加快执行速度
    await element.click(delay=random.randint(100, 300))  # 减少点击延迟

    # 双重验证结果
    try:
        await asyncio.wait_for(
            page.wait_for_selector(".success-toast", timeout=10000),
            timeout=15
        )
        print("✅ 操作成功")
    except:
        await asyncio.wait_for(
            page.wait_for_selector("text=续费成功", timeout=10000),
            timeout=15
        )
        print("✅ 操作成功")

async def renew_service(max_retries=1):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await human_behavior_simulation(page)

        # 尝试访问续费页面
        await page.goto("https://freecloud.ltd/server/detail/2378/renew", wait_until="networkidle")
        await asyncio.sleep(1)  # 减少等待时间

        # 检查是否被重定向到登录页面
        if "login" in page.url:
            print("🔐 未登录，执行登录操作...")
            await page.goto("https://freecloud.ltd/login", wait_until="networkidle")
            await page.fill('input[name="username"]', USERNAME)
            await page.fill('input[name="password"]', PASSWORD)
            await asyncio.sleep(random.uniform(0.5, 1.0))  # 减少等待时间
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            # 登录成功后，重新导航到续费页面
            await page.goto("https://freecloud.ltd/server/detail/2378/renew", wait_until="networkidle")
            await asyncio.sleep(0.5)  # 减少等待时间

        for attempt in range(1, max_retries+1):
            try:
                print(f"🔄 第{attempt}次尝试")

                # 处理可能的加载提示
                if await handle_loading(page):
                    await page.reload(wait_until="networkidle")

                submit_btn = await page.wait_for_selector(
                    "button[type='submit']",
                    state="attached",
                    timeout=10000  # 减少等待时间
                )
                await submit_click_handler(page, submit_btn)
                return

            except Exception as e:
                print(f"⚠️ 尝试失败: {str(e)}")
                if attempt == max_retries:
                    raise

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(renew_service())
