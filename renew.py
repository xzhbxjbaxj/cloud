import os
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

async def stealth_config(context):
    """注入反检测脚本"""
    await context.add_init_script(
        script="""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
    )

async def handle_network_interception(route, request):
    """拦截网络请求处理异常"""
    if "captcha" in request.url:
        print("⚠️ 检测到验证码请求，建议人工介入")
    await route.continue_()

async def renew_service(max_retries=3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--user-data-dir=./chrome_profile",
                "--start-maximized"
            ],
            # 设置浏览器指纹参数:ml-citation{ref="3" data="citationList"}
            executable_path="/usr/bin/google-chrome-stable"
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            # 加载本地存储状态:ml-citation{ref="2" data="citationList"}
            storage_state="auth.json" if os.path.exists("auth.json") else None
        )

        # 注入反检测配置:ml-citation{ref="5" data="citationList"}
        await stealth_config(context)
        page = await context.new_page()
        
        # 设置请求拦截器:ml-citation{ref="7" data="citationList"}
        await page.route("**/*", handle_network_interception)

        try:
            print("🔐 模拟登录流程")
            await page.goto("https://freecloud.ltd/login", timeout=15000)
            await page.fill('input[name="username"]', USERNAME)
            await page.fill('input[name="password"]', PASSWORD)
            
            # 添加随机操作延迟:ml-citation{ref="6" data="citationList"}
            await asyncio.sleep(1.5)
            await page.click('button[type="submit"]')
            
            # 保存登录状态:ml-citation{ref="3" data="citationList"}
            await context.storage_state(path="auth.json")

            # 验证跳转状态:ml-citation{ref="1" data="citationList"}
            await page.wait_for_selector("#dashboard", state="visible", timeout=10000)
            
            print("🔁 执行续费操作")
            for attempt in range(max_retries):
                try:
                    await page.goto("https://freecloud.ltd/server/detail/2378/renew", timeout=10000)
                    await page.click('button[type="submit"]', delay=200)
                    
                    # 智能等待确认弹窗:ml-citation{ref="6" data="citationList"}
                    await page.wait_for_function(
                        "document.querySelector('.success-toast') !== null",
                        timeout=5000
                    )
                    print(f"✅ 第{attempt+1}次尝试续费成功")
                    break
                except Exception as e:
                    print(f"⚠️ 第{attempt+1}次尝试失败: {str(e)}")
                    if attempt == max_retries -1:
                        raise

        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise ValueError("环境变量 FC_USERNAME 和 FC_PASSWORD 未设置")
    
    # 添加异步重试逻辑:ml-citation{ref="1" data="citationList"}
    asyncio.run(renew_service())
