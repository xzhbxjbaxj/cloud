from playwright.sync_api import sync_playwright
import os
import requests
# from dotenv import load_dotenv
from datetime import datetime
import traceback
import time

# 定义视频保存目录
video_dir = "test-results/videos" # 你可以根据需要更改这个路径

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()


def check_renewal_status(page,selector, invalid_texts,max_num=10):
    num =1
    result_text=""
    while num< max_num:
        try:
            num+=1
            time.sleep(1)
            # 尝试查找元素(设置1秒超时避免长时间阻塞)
            element = page.wait_for_selector(
                selector,
                timeout=500,
                state="visible"
            )
            if not element:
                continue
            # 获取元素文本
            current_text = element.inner_text().strip()
            print(f"{current_text}")
            # 检查文本是否有效
            if current_text and current_text not in invalid_texts:
                result_text = current_text
                break  # 获取到有效结果，退出循环
        
        except Exception as e:
            # 可以记录日志，但不需要处理
            print(f"查询尝试失败: {e}")
        
    
    return f"{result_text}"

def login_koyeb(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            # 设置视频保存目录
            record_video_dir=video_dir,
            # 可选：配置其他视频选项，例如大小
            # record_video_size={"width": 640, "height": 480},
            # trace='on' # 启用跟踪
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"

        )
        # context.tracing.start()
        page = context.new_page()

        try:
            page.bring_to_front()  # 将页面带到最前

            # 打开登录页
            page.goto("https://freecloud.ltd/login", timeout=60000)
            page.wait_for_selector("text=点击登录", timeout=60000)

            # 填写邮箱和密码
            page.get_by_placeholder("用户名/邮箱/手机号").fill(email)
            page.get_by_placeholder("请输入登录密码").fill(password)

            # 勾选协议
            checkbox = "input[name='agree']"
            if not page.is_checked(checkbox):
                page.check(checkbox)
            # 点击登录
            page.click("text=点击登录")

            # 错误提示
            try:
                error_sel = '//div[contains(@class, "jq-icon-error") and contains(@style, "display: block")]'
                error = page.wait_for_selector(error_sel, timeout=8000)
                if error:
                    return f"账号 `{email}` 登录失败：{error.inner_text().strip()}"
            except :
                pass

            # 登录成功跳转
            page.wait_for_url("https://freecloud.ltd/member/index", timeout=30000)

            # 访问续费页面
            page.locator('a[href="https://freecloud.ltd/server/lxc"]').first.click()
            page.wait_for_selector('a[data-modal*="/server/detail/"][data-modal*="/renew"]').click()
            page.wait_for_selector("#submitRenew").click()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            page.screenshot(path=f"failure_screenshot_{timestamp}.png")
            with open(f"failure_page_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            result = check_renewal_status(page,'.layui-layer.layui-layer-dialog.layui-layer-msg',["", "无结果", "null", "undefined", "加载中"] )
            result_text = result if result else "续费失败"


            return f"✅ 账号 `{email}` {result_text}"

        except Exception as e:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            page.screenshot(path=f"failure_screenshot_{timestamp}.png")
            with open(f"failure_page_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            traceback.print_exc()
            return f"❌ 账号 `{email}` 登录失败：{str(e)}（已保存调试信息）"

        finally:
            # context.tracing.stop()
            context.close()
            browser.close()


def main():
    # load_dotenv()
    accounts = os.environ.get('WEBHOST', '').split()
    results = []

    if not accounts:
        error = "⚠️ 未配置任何账号（WEBHOST 变量为空）"
        print(error)
        send_telegram_message(error)
        return

    for account in accounts:
        try:
            email, password = account.split(":")
            result = login_koyeb(email.strip(), password.strip())
        except ValueError:
            result = f"❌ 账号配置格式错误: `{account}`"
        results.append(result)
        print(result)

    
