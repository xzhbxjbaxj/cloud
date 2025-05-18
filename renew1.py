
import os
import asyncio
import random
import json
from playwright.async_api import async_playwright

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

async def human_behavior_simulation(page):
    """增强的人类行为模拟"""
    await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """)
    await page.emulate_media(color_scheme="dark")
    # 添加随机鼠标移动
    await page.mouse.move(
        random.randint(0, 300),
        random.randint(0, 300)
    )

async def renew_service(max_retries=3):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./chrome_profile",
            headless=False,  # 调试时可设为False
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
            
            # 改进的登录状态处理
            if not os.path.exists("auth.json"):
                print("🔐 开始初次登录流程")
                await page.goto("https://freecloud.ltd/login", wait_until="networkidle")
                await page.fill('input[name="username"]', USERNAME)
                await page.fill('input[name="password"]', PASSWORD)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                await page.click('button[type="submit"]')
                await page.wait_for_url("https://freecloud.ltd/server/lxc, timeout=15000)
                await context.storage_state(path="auth.json")
            else:
                print("🔄 加载已有登录状态")
                with open("auth.json", "r") as f:
                    cookies = json.load(f)["cookies"]
                    await context.add_cookies(cookies)

            # 增强的重试机制
            for attempt in range(1, max_retries+1):
                try:
                    print(f"🔄 第{attempt}次续费尝试")
                    await page.goto("https://freecloud.ltd/server/detail/2378/renew", 
                                  wait_until="networkidle", 
                                  timeout=20000)
                    
                    # 更可靠的按钮定位方式
                    submit_btn = await page.wait_for_selector(
                        "button[type='submit']", 
                        state="visible", 
                        timeout=10000
                    )
                    await submit_btn.click(delay=random.randint(200, 800))
                    
                    # 多种成功条件判断
                    try:
                        await page.wait_for_selector(".success-toast", timeout=10000)
                        print("✅ 续费操作成功")
                        return
                    except:
                        await page.wait_for_selector("text=续费成功", timeout=10000)
                        print("✅ 续费操作成功")
                        return
                        
                except Exception as e:
                    print(f"⚠️ 第{attempt}次尝试失败: {str(e)}")
                
                  

        except Exception as e:
            print(f"❌ 续费流程失败: {str(e)}")
            
        finally:
            await context.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        raise ValueError("请设置 FC_USERNAME 和 FC_PASSWORD 环境变量")
    
    asyncio.run(renew_service())
