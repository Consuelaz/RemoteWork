# 会员系统接真清单（从本地模拟 → Supabase 真实）

按 1→6 顺序执行。第 6 步内部还有一条**不可颠倒**的子顺序。

---

## 1. 创建 Supabase 项目

1. 打开 `https://supabase.com`，注册/登录（GitHub 账号可直接登）
2. New project：Organization 随便建，Region 选 **Singapore（东南亚）** —— 国内访问比东京/美西快
3. 数据库密码设一个，记下来（后面基本不用，但丢不了找回麻烦）
4. 等约 2 分钟项目初始化完成

## 2. 执行数据库 schema

1. 左侧 **SQL Editor** → New query
2. 把 `supabase/schema.sql` 全文粘贴进去 → Run
3. 确认无报错。它会创建：

| 对象                 | 作用                                   |
| ------------------ | ------------------------------------ |
| `profiles`         | 用户资料（id 对应 auth.users）               |
| `memberships`      | 会员有效期                                |
| `redeem_codes`     | 兑换码（**无任何 RLS 策略**，用户枚举不到）           |
| `redemptions`      | 兑换流水，`code` 唯一约束 = 防重复兑换双保险          |
| `job_access`       | 会员专属数据（申请链接、内推联系方式）                  |
| `redeem_code()`    | 兑换 RPC，`SELECT ... FOR UPDATE` 行锁防并发 |
| `get_job_access()` | 批量取权益 RPC                            |
| `is_member()`      | 会员判定                                 |

## 3. 填 config.js（这步做完，登录自动变真）

Project Settings → API，复制两个值填进 `config.js`：

```
URL       = https://doytntlxfidljoszhyje.supabase.co         （形如 https://xxxx.supabase.co）
ANON_KEY  = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRveXRudGx4ZmlkbGpvc3poeWplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI5Nzc2MjUsImV4cCI6MjEwODU1MzYyNX0.lBmjNhocGApGDkeHwk0wHc5kO7b2wvkf-lkhuQznmpY   （很长的一串 JWT）
```

**填完不需要改任何代码**。`auth.js` 的检测逻辑是：有 key 就创建真实客户端，没有就走本地模拟。

anon key 是公开安全的（受 RLS 保护），可以提交到仓库。

## 4. 配置邮箱登录

1. Authentication → Providers → Email：**Enabled** 保持开启
2. **必须关掉 `Confirm email`** —— 勾着会让验证码登录被拦
3. Authentication → Emails → Magic Link 模板：确认正文含 `{{ .Token }}`（默认有）
4. Authentication → URL Configuration → Site URL 填你的站点地址，本地开发填 `http://127.0.0.1:8765`
5. Redirect URLs 加上 `http://127.0.0.1:8765/**` 和线上域名

> 内置 SMTP 免费项目每小时只能发个位数封，且容易被判垃圾邮件。  
> 正式上线前换自定义 SMTP：海外用户用 Resend（免费 3000 封/月），国内用户用阿里云/腾讯云邮件推送。  
> 详见 `supabase/email-setup.md`。

## 5. 生成兑换码

复制 `.env.local.example` 为 `.env.local`，填入 `SERVICE_ROLE_KEY`（Project Settings → API → service_role key，  
**最高权限，绝不提交、绝不写进前端**）。

```bash
# 只生成，输出 CSV 拿去其它渠道卖
node scripts/gen-codes.mjs --count 100 --days 30 --batch BATCH001

# 生成并直接写入数据库
node scripts/gen-codes.mjs --count 100 --days 30 --import
```

参数：`--count` 数量、`--days` 会员天数、`--plan` 套餐名、`--expires` 兑换码本身有效期（过期作废）。

## 6. 导入权益数据（顺序不可颠倒）

```bash
# 6.1 重新导出最新的权益数据（含 jobs-featured.js）
node scripts/export-job-access.mjs
```

Table Editor → `job_access` → Import data from CSV → 选 `supabase/job-access.csv`。

**确认导入成功、条数对得上之后**，再执行剥离：

```bash
# 6.2 预览（默认只预览，不改动文件）
node scripts/strip-gated-fields.mjs

# 6.3 确认无误后真正剥离前端明文
node scripts/strip-gated-fields.mjs --apply
```

> 反了会丢数据：先剥离就再也导不出来了。

---

## 验证清单

- [ ] 打开 `account.html`，输真实邮箱 → 收到 6 位验证码 → 登录成功
- [ ] 用一个真实兑换码激活 → 会员状态和有效期正确显示
- [ ] 同一个码再兑一次 → 提示「你已经兑换过这个兑换码了」
- [ ] 换一个浏览器/无痕窗口用同一个码 → 同样被拒（证明防重放是服务端生效的）
- [ ] Supabase → Table Editor → `redemptions` 里能看到兑换流水
- [ ] 用错误邮箱格式提交 → 前端直接拦下，不发请求

---

## 当前状态提醒

上一轮已移除精选岗的会员门控，所以**登录在站内目前没有任何可见差异**——  
不登录也能看全部岗位。要让会员真的「值钱」，需要先定会员能看到什么，  
再把对应的门控加回 `app.js` 的 `renderJobAccess()`。
