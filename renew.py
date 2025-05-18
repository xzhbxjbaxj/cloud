import os
import asyncio
import random
from playwright.async_api import async_playwright

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

async def human_behavior_simulation(page):
    """模拟人类操作模式"""
    await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """)
    await page.emulate_media(color_scheme="dark")  # 模拟暗色模式偏好:ml-citation{ref="6" data="citationList"}

async def renew_service(max_retries=3):
    async with async_playwright() as p:
        # 持久化浏览器上下文配置:ml-citation{ref="3,4" data="citationList"}
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./chrome_profile",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ],
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )

        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await human_behavior_simulation(page)
            
            # 初始化登录状态检查:ml-citation{ref="7" data="citationList"}
            if not os.path.exists("auth.json"):
                print("🔐 开始初次登录流程")
                await page.goto("https://freecloud.ltd/login", wait_until="networkidle")
                await page.fill('input[name="username"]', USERNAME)
                await page.fill('input[name="password"]', PASSWORD)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                await page.click('button[type="submit"]')
                
                await context.storage_state(path="auth.json")
            else:
                print("🔄 加载已有登录状态")
                await context.add_cookies(open("auth.json", "r").read())

            # 续费操作重试逻辑:ml-citation{ref="1,5" data="citationList"}
            for attempt in range(1, max_retries+1):
                try:
                    print(f"🔄 第{attempt}次续费尝试")
                    await page.goto("https://freecloud.ltd/server/detail/2378/renew", timeout=15000)
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    # 动态等待按钮可点击:ml-citation{ref="6" data="citationList"}
                    submit_btn = page.locator("button[type='submit']")
                    await submit_btn.wait_for(state="visible", timeout=5000)
                    await submit_btn.click(delay=random.randint(200, 500))
                    
                    # 验证操作结果:ml-citation{ref="5" data="citationList"}
                    await page.wait_for_selector(".success-toast", timeout=10000)
                    print("✅ 续费操作成功")
                    return
                except Exception as e:
                    print(f"⚠️ 第{attempt}次尝试失败: {str(e)}")
                    if attempt == max_retries:
                        raise
                    await asyncio.sleep(attempt * 5)  # 指数退避策略:ml-citation{ref="1" data="citationList"}

        finally:
            await context.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise ValueError("请设置 FC_USERNAME 和 FC_PASSWORD 环境变量")
    
    asyncio.run(renew_service())
