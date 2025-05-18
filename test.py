import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

USERNAME = "abb295390@gmail.com"
PASSWORD = "123456789zyZY"

async def human_behavior_simulation(page):
    # 模拟人类行为：隐藏 navigator.webdriver 特征、模拟深色模式
    await page.evaluate("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined});""")
    await page.emulate_media(color_scheme="dark")

async def handle_loading(page):
    """检测并处理 'just a moment' 加载提示"""
    try:
        # 等待文本 "just a moment" 出现，最长 5 秒
        loading = await page.wait_for_selector("text='just a moment'", timeout=5000)
        if loading:
            print("⏳ 检测到加载提示，等待1秒...")
            await asyncio.sleep(1)
            return True
    except PlaywrightTimeoutError:
        return False

async def submit_click_handler(page, element):
    """优化的点击处理：先滚动到可见，再短暂随机等待后点击"""
    await element.scroll_into_view_if_needed()
    await asyncio.sleep(random.uniform(0.3, 0.8))          # 随机等待，模拟人类操作
    await element.click(delay=random.randint(100, 300))    # 随机点击延迟

    # 尝试两种“续费成功”提示
    try:
        await asyncio.wait_for(
            page.wait_for_selector(".success-toast", timeout=10000),
            timeout=15
        )
        print("✅ 操作成功（success-toast）")
    except PlaywrightTimeoutError:
        await asyncio.wait_for(
            page.wait_for_selector("text=续费成功", timeout=10000),
            timeout=15
        )
        print("✅ 操作成功（文字提醒）")

async def renew_service(max_retries: int = 3):
    async with async_playwright() as p:
        # 无头模式，适配 CI 环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await human_behavior_simulation(page)

        # 第一次尝试导航到续费页面
        print("🚀 尝试导航到续费页面...")
        try:
            await page.goto(
                "https://freecloud.ltd/server/detail/2378/renew",
                wait_until="load",    # 只等待主体加载完成
                timeout=60000          # 超时调整至 60 秒
            )
        except PlaywrightTimeoutError:
            print("⚠️ 首次导航到续费页面时超时，将尝试后续逻辑。")

        await asyncio.sleep(1)  # 短暂等待，确保页面稳定

        # 如果被重定向至登录页，则执行登录
        if "login" in page.url:
            print("🔐 未登录，执行登录操作...")
            try:
                await page.goto(
                    "https://freecloud.ltd/login",
                    wait_until="load",
                    timeout=60000
                )
            except PlaywrightTimeoutError:
                print("⚠️ 导航到登录页面时超时，继续尝试填充表单。")

            # 填充并提交登录表单
            await page.fill('input[name="username"]', USERNAME)
            await page.fill('input[name="password"]', PASSWORD)
            await asyncio.sleep(random.uniform(0.5, 1.0))  # 随机等待
            await page.click('button[type="submit"]')

            # 等待登录后页面加载完成
            try:
                await page.wait_for_load_state("load", timeout=60000)
            except PlaywrightTimeoutError:
                print("⚠️ 登录后加载续费页面超时，稍后重试。")

            print("✅ 登录成功，重新导航到续费页面...")
            try:
                await page.goto(
                    "https://freecloud.ltd/server/detail/2378/renew",
                    wait_until="load",
                    timeout=60000
                )
            except PlaywrightTimeoutError:
                print("⚠️ 重新导航到续费页面时超时，稍后重试。")

            await asyncio.sleep(0.5)

        # 登录后或已登录状态下，执行续费尝试
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🔄 第 {attempt} 次续费尝试")

                # 检测并处理 “just a moment” 加载提示
                if await handle_loading(page):
                    await page.reload(wait_until="load", timeout=60000)
                    await asyncio.sleep(0.5)

                # 等待提交按钮出现，然后点击
                submit_btn = await page.wait_for_selector(
                    "button[type='submit']",
                    state="attached",
                    timeout=10000  # 10 秒超时
                )
                await submit_click_handler(page, submit_btn)
                return  # 成功后退出

            except PlaywrightTimeoutError as e:
                print(f"⚠️ 第 {attempt} 次尝试失败（超时）: {e}")
            except Exception as e:
                print(f"⚠️ 第 {attempt} 次尝试失败: {e}")

            # 失败且未达到最大重试次数时，等待 1 秒后重试
            if attempt < max_retries:
                await asyncio.sleep(1)
            else:
                raise RuntimeError("❌ 续费操作在多次重试后仍未成功。")

        # 关闭上下文与浏览器
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(renew_service())
