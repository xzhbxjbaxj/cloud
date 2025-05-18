import asyncio
import random
from playwright.async_api import async_playwright

USERNAME = "abb295390@gmail.com"
PASSWORD = "123456789zyZY"

async def human_behavior_simulation(page):
    # 模拟人类行为：隐藏 webdriver 特征、模拟深色模式
    await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)
    await page.emulate_media(color_scheme="dark")

async def handle_loading(page):
    """检测并处理 'just a moment' 加载提示"""
    try:
        loading = await page.wait_for_selector("text='just a moment'", timeout=5000)
        if loading:
            print("⏳ 检测到加载提示，等待1秒...")
            await asyncio.sleep(1)
            return True
    except:
        return False

async def submit_click_handler(page, element):
    """优化的点击处理：先滚动到可见，再短暂随机等待后点击"""
    await element.scroll_into_view_if_needed()
    await asyncio.sleep(random.uniform(0.3, 0.8))         # 减少等待时间
    await element.click(delay=random.randint(100, 300))   # 减少点击延迟

    # 尝试等待两种成功提示
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

async def renew_service(max_retries: int = 3):
    async with async_playwright() as p:
        # 使用无头模式，适配 GitHub Actions 等 CI 环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await human_behavior_simulation(page)

        # 第一次尝试导航到续费页面
        print("🚀 尝试导航到续费页面...")
        await page.goto(
            "https://freecloud.ltd/server/detail/2378/renew",
            wait_until="load",          # 等待页面主体加载完成 :contentReference[oaicite:4]{index=4}
            timeout=60000                # 将超时设置为 60 秒 :contentReference[oaicite:5]{index=5}
        )
        await asyncio.sleep(1)           # 短暂等待，确保页面稳定

        # 如果被重定向到登录页，则执行登录操作
        if "login" in page.url:
            print("🔐 未登录，执行登录操作...")
            await page.goto(
                "https://freecloud.ltd/login",
                wait_until="load",
                timeout=60000
            )
            # 填充用户名和密码
            await page.fill('input[name="username"]', USERNAME)
            await page.fill('input[name="password"]', PASSWORD)
            await asyncio.sleep(random.uniform(0.5, 1.0))  # 短暂随机等待
            await page.click('button[type="submit"]')

            # 等待登录后页面加载完成
            await page.wait_for_load_state("load", timeout=60000)
            print("✅ 登录成功，重新导航到续费页面...")
            await page.goto(
                "https://freecloud.ltd/server/detail/2378/renew",
                wait_until="load",
                timeout=60000
            )
            await asyncio.sleep(0.5)

        # 在登录之后，执行续费尝试逻辑
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🔄 第 {attempt} 次续费尝试")

                # 检测并处理可能的 'just a moment' 加载提示
                if await handle_loading(page):
                    await page.reload(wait_until="load", timeout=60000)
                    await asyncio.sleep(0.5)

                # 等待提交按钮出现，然后点击
                submit_btn = await page.wait_for_selector(
                    "button[type='submit']",
                    state="attached",
                    timeout=10000  # 减少等待时间 :contentReference[oaicite:6]{index=6}
                )
                await submit_click_handler(page, submit_btn)
                return  # 成功后退出

            except Exception as e:
                print(f"⚠️ 第 {attempt} 次尝试失败: {e}")
                if attempt == max_retries:
                    raise
                # 若尝试失败，短暂等待并重试
                await asyncio.sleep(1)

        # 关闭上下文与浏览器
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(renew_service())
