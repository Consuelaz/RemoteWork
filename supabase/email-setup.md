# 邮箱登录配置（Supabase）

登录方式：**邮箱登录链接（Magic Link）**（`signInWithOtp` + `emailRedirectTo`，用户点击邮件里的链接直接回站完成登录，无需输入验证码）。

## 1. 打开邮箱登录

Supabase 控制台 → Authentication → Providers → Email
- ✅ `Allow new users to sign up`（对应 `shouldCreateUser: true`）
- `Confirm email` 开关对魔法链接登录无阻断影响（链接本身即完成确认+登录），保持默认即可

## 2. 关键：邮件模板必须带 `{{ .ConfirmationURL }}`

Authentication → Emails → 模板 `Magic Link`，确认正文里的按钮/链接指向：

```
{{ .ConfirmationURL }}
```

默认模板是有的。如果你改过模板把它删了，用户点不到登录链接，就登录不了。
注意：模板里需要的是 `{{ .ConfirmationURL }}`（完整链接），**不是** `{{ .Token }}`（那是 6 位验证码用的）。

同时确认：Authentication → Sign In / Providers → Email → `Magic Link Expiry` 建议 3600 秒（1 小时），太短用户点邮件晚了几分钟就过期。

## 3. 邮件发送：内置服务够不够？

Supabase 内置 SMTP 有限额（免费项目约每小时个位数封），且发件域名是 supabase 的，
进垃圾箱概率高。**正式上线前换成自定义 SMTP**：

Authentication → Emails → SMTP Settings

| 服务商 | 适合 | 备注 |
|---|---|---|
| Resend | 海外用户为主 | 免费额度 3000 封/月，配置最简单 |
| 阿里云邮件推送 | 国内用户为主 | 需域名备案，按量计费 |
| 腾讯云 SES | 国内用户为主 | 需域名备案 |

## 4. URL 白名单（重要）

Authentication → URL Configuration
- Site URL：你的正式域名（如 `https://junes.example.com`）
- Redirect URLs：加上 `https://你的域名/account.html`

本地调试时加 `http://127.0.0.1:8765/account.html`。
不加白名单，魔法链接会被跳到 Site URL 而不是你要的页面。
前端 `emailRedirectTo` 固定指回 `/account.html`，登录态由 Supabase 客户端
（`detectSessionInUrl: true`）从回调 URL 自动接管。

## 5. 用户表

`schema.sql` 里 `profiles.email` 由 `handle_new_user()` 触发器在注册时自动写入，
`phone` 列保留为 nullable，将来加手机号绑定时直接用。

## 6. 自建 profile 兜底

如果触发器因为某些原因没建 profile，`my_membership` / `redeem_code` 仍然可用
（这两个 RPC 只看 `auth.uid()` 和 `memberships` 表）。但为保险，可手动补：

```sql
insert into public.profiles (id, email)
select u.id, u.email from auth.users u
on conflict (id) do nothing;
```
