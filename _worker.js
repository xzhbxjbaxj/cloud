export default {
  // 每次 HTTP 请求触发时执行
  async fetch(request, env, ctx) {
    // 从环境变量中读取用户名和密码
    const USERNAME = env.FREECLOUD_USERNAME;
    const PASSWORD = env.FREECLOUD_PASSWORD;

    // 相关接口 URL
    const port="2378"
    const LOGIN_URL = "https://freecloud.ltd/login";
    const CONSOLE_URL = "https://freecloud.ltd/member/index"; // 登录后跳转页面
    const RENEW_URL = f"https://freecloud.ltd/server/detail/{port}/renew"; // 续费接口

    // 随机选择一个常见浏览器 User-Agent，模拟正常用户行为
    const userAgents = [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ];
    const UA = userAgents[Math.floor(Math.random() * userAgents.length)];

    // 公共请求头（登录和后续请求共用）
    const headers = {
      "User-Agent": UA,
      "Content-Type": "application/x-www-form-urlencoded",
      "Referer": "https://freecloud.ltd/login",
      "Origin": "https://freecloud.ltd",
      "Sec-Fetch-Site": "same-origin",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Dest": "document",
      "Upgrade-Insecure-Requests": "1",
    };

    // 登录表单数据（使用 URL 编码格式）
    const loginPayload = new URLSearchParams({
      username: USERNAME,
      password: PASSWORD,
      mobile: "",
      captcha: "",
      verify_code: "",
      agree: "1",
      login_type: "PASS",
      submit: "1",
    });

    // 续费请求数据
    const renewPayload = new URLSearchParams({
      month: "1",        // 续费 1 个月
      submit: "1",
      coupon_id: "0",    // 无优惠券
    });

    // Step 1: 登录获取 Cookie
    const loginResp = await fetch(LOGIN_URL, {
      method: "POST",
      headers,
      body: loginPayload,
      redirect: "manual",  // 不自动跟随跳转
    });

    // 获取登录后的 Set-Cookie 头，用于后续操作
    const cookie = loginResp.headers.get("set-cookie");
    if (!cookie) {
      return new Response("❌ 执行失败，未获取 Cookie，响应头无效：" + cookie);
    }

    // Step 2: 访问登录后的控制台页，完成跳转并激活会话
    await fetch(CONSOLE_URL, {
      method: "GET",
      headers: {
        ...headers,
        Cookie: cookie,
      },
    });

    // Step 3: 模拟人类行为 —— 随机等待 1~3 秒
    await new Promise((r) => setTimeout(r, Math.floor(1000 + Math.random() * 2000)));

    // Step 4: 发起续费请求（POST）
    const renewResp = await fetch(RENEW_URL, {
      method: "POST",
      headers: {
        ...headers,
        Cookie: cookie,
        "X-Requested-With": "XMLHttpRequest", // 模拟 Ajax 请求
      },
      body: renewPayload,
    });

    // 尝试解析返回 JSON 内容
    const text = await renewResp.text();
    try {
      const json = JSON.parse(text);

      // 判断返回信息中是否提示「还有3天」 → 表示续费失败
      if (json.msg.includes("3天")) {
        return new Response("❌" + json.msg);
      } else {
        return new Response("✅" + json.msg);
      }
    } catch (e) {
      // JSON 解析失败时返回原始响应
      return new Response("⚠️ 无法解析: " + text, { status: 500 });
    }
  },
};
