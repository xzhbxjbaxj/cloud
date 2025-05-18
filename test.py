
import os
import asyncio
import random
from playwright.async_api import async_playwright
import json


USERNAME = "abb295390@gmail.com"
PASSWORD ="123456789zyZY"
async def load_cookies(context):
    with open("auth.json", "r") as f:
        cookies = json.load(f)  # 关键解析步骤
        await context.add_cookies(cookies)
async def human_behavior_simulation(page):
    await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """)
    await page.emulate_media(color_scheme="dark")

async def handle_loading(page):
    """处理加载提示"""
    try:
        loading = await page.wait_for_selector("text='just a moment'", timeout=5000)
        if loading:
            print("⏳ 检测到加载提示，等待5秒...")
            await asyncio.sleep(5)
            return True
    except:
        return False

async def renew_service(max_retries=3):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./chrome_profile",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1366, "height": 768}
        )

        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await human_behavior_simulation(page)
            
            if not os.path.exists("auth.json"):
                await page.goto("https://freecloud.ltd/login", wait_until="networkidle")
                await page.fill('input[name="username"]', USERNAME)
                await page.fill('input[name="password"]', PASSWORD)
                await asyncio.sleep(random.uniform(1, 2))
                await page.click('button[type="submit"]')
                await context.storage_state(path="auth.json")
            else:
                load_cookies(context)

            for attempt in range(1, max_retries+1):
                try:
                    print(f"🔄 第{attempt}次尝试")
                    await page.goto("https://freecloud.ltd/server/detail/2378/renew", timeout=30000)
                    
                    # 处理可能的加载提示
                    if await handle_loading(page):
                        await page.reload(wait_until="networkidle")
                    
                    submit_btn = await page.wait_for_selector(
                        "button[type='submit']", 
                        state="attached",
                        timeout=15000
                    )
                    await submit_click_handler(page, submit_btn)
                    return
                    
                except Exception as e:
                    print(f"⚠️ 尝试失败: {str(e)}")
                    if attempt == max_retries:
                        raise

        finally:
            await context.close()

async def submit_click_handler(page, element):
    """优化的点击处理"""
    await element.scroll_into_view_if_needed()
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await element.click(delay=random.randint(300, 800))
    
    # 双重验证结果
    try:
        await asyncio.wait_for(
            page.wait_for_selector(".success-toast", timeout=20000),
            timeout=25
        )
        print("✅ 操作成功")
    except:
        await asyncio.wait_for(
            page.wait_for_selector("text=续费成功", timeout=20000),
            timeout=25
        )
        print("✅ 操作成功")

if __name__ == "__main__":
    asyncio.run(renew_service())
