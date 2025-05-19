export default {
  async fetch(request, env, ctx) {
    const USERNAME = env.FREECLOUD_USERNAME;
    const PASSWORD = env.FREECLOUD_PASSWORD;

    const LOGIN_URL = "https://freecloud.ltd/login";
    const CONSOLE_URL = "https://freecloud.ltd/member/index";
    const RENEW_URL = "https://freecloud.ltd/server/detail/2378/renew";

    const userAgents = [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ];
    const UA = userAgents[Math.floor(Math.random() * userAgents.length)];

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

    const renewPayload = new URLSearchParams({
      month: "1",
      submit: "1",
      coupon_id: "0",
    });

    // Step 1: 
    const loginResp = await fetch(LOGIN_URL, {
      method: "POST",
      headers,
      body: loginPayload,
      redirect: "manual",
    });
    const cookie = loginResp.headers.get("set-cookie");
    if (!cookie ) {
      return new Response("❌ 执行失败，cook无效果"+cookie);
    }
  

    // Step 2: 
    await fetch(CONSOLE_URL, {
      method: "GET",
      headers: {
        ...headers,
        Cookie: cookie,
      },
    });

    // Step 3: 
    await new Promise((r) => setTimeout(r, Math.floor(1000 + Math.random() * 2000)));

    // Step 4: 
    const renewResp = await fetch(RENEW_URL, {
      method: "POST",
      headers: {
        ...headers,
        Cookie: cookie,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: renewPayload,
    });

    const text = await renewResp.text();
    try {
      const json = JSON.parse(text);
      if (json.msg.includes("3天")) {
        return new Response("❌" + json.msg);
      } else {
        return new Response("✅" + json.msg);}
    } catch (e) {
      return new Response("⚠️ 无法解析: " + text, { status: 500 });
    }
  },
};
