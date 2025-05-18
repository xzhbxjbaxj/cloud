import os
import asyncio
import random
from playwright.async_api import async_playwright

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

async def human_behavior_simulation(page):
    await page.evaluate("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
    await page.emulate_media(color_scheme="dark")

async def handle_loading(page):
    try:
        loading = await page.wait_for_selector("text='just a moment'", timeout=4000)
        if loading:
            print("⏳ 检测到加载提示，等待1秒...")
            await asyncio.sleep(1)
            return True
    except:
        return False

async def submit_click_handler(page, element):
    await element.scroll_into_view_if_needed()
    await asyncio.sleep(random.uniform(0.3, 0.8))
    await element.click(delay=random.randint(100, 300))

    try:
        await asyncio.wait_for(
            page.wait_for_selector(".success-toast", timeout=2000),
            timeout=15
        )
        print("✅ 操作成功")
    except:
        await asyncio.wait_for(
            page.wait_for_selector("text=续费成功", timeout=2000),
            timeout=15
        )
        print("✅ 操作成功")

async def renew_action(page, max_retries):
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 第{attempt}次尝试")

            # await page.goto("https://freecloud.ltd/server/detail/2378/renew")
            # await asyncio.sleep(1)

            if await handle_loading(page):
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(1)

           # submit_btn = await page.wait_for_selector(
            #    "#submitRenew",
             #   timeout=4000
            #)
            submit_btn = await page.wait_for_selector(
                "button#submitRenew.btn.btn-primary",
                timeout=4000
            )
       #     await page.wait_for_selector("xpath//button[@id='submitRenew']", timeout=4000)


           #   submit_btn = await page.wait_for_selector(
            #     "button#submitRenew.btn.btn-primary",
             #     state="visible",
              #    timeout=4000
              #)
            await submit_click_handler(page, submit_btn)
            return True
        except Exception as e:
            print(f"⚠️ 尝试失败: {str(e)}")
            # if attempt == max_retries:
            #     raise
    return False

async def renew_service(max_retries=1):
    async with async_playwright() as p:
        # 【唯一修改点】将 headless=False 改为 headless=True
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./chrome_profile",
            headless=True,  # <— 由 False 改为 True，即启用无头模式 :contentReference[oaicite:0]{index=0}
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1366, "height": 768}
        )

        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await human_behavior_simulation(page)

            await page.goto("https://freecloud.ltd/server/detail/2378/renew")
            await asyncio.sleep(1)

            if "login" in page.url:
                print("🔐 未登录，执行登录操作...")
                await page.goto("https://freecloud.ltd/login", wait_until="networkidle")
                await page.fill('input[name="username"]', USERNAME)
                await page.fill('input[name="password"]', PASSWORD)
                await asyncio.sleep(random.uniform(0.5, 1.0))
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')

                # 等待登录状态同步
                await asyncio.sleep(1)

            # 登录后或已登录状态下都执行续费
            await renew_action(page, max_retries)

        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(renew_service())
