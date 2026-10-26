# 项目长期记忆

## 项目概况
- **项目**：Junes远程工作聚合网站
- **路径**：`/Users/qisoong/WorkBuddy/20260317141747/`
- **技术栈**：纯静态 HTML/CSS/JS + Python 爬虫脚本（`scrape.sh`）
- **数据文件**：`jobs-cn.js`（国内）、`jobs-global.js`（海外）、`money.xlsx`（内推记录）

## 数据源
| 数据源 | 类型 | 说明 | 内推 |
|--------|------|------|------|
| Remote OK | 海外 | JSON API 直连，description 截断 500 字 | 否 |
| Remotive | 海外 | JSON API 直连 | 否 |
| 远程岛 | 海外 | JSON API，description 含完整 HTML 必须截断 | 否 |
| 远程中文网 | 国内 | HTML 抓取，直连 | 否 |
| V2EX | 国内 | HTML 抓取，需代理 `http://127.0.0.1:7892` | ✅ |
| who-is-hiring（Rebase） | 国内 | JSON API，所有字段可能为 null | ✅ |
| 电鸭 | 国内 | JS渲染，curl 无法抓取，跳过 | 否 |

## 关键 Bug 修复记录

### ✅ scrape.sh V2EX 详情页代理端口不一致（2026-09-02）
- V2EX 列表页用 `7892`，但详情页 curl 硬编码 `-x http://127.0.0.1:7897`，导致 7897 旧代理失效时详情页全部下载失败
- 修复：将详情页 curl 代理统一改为 `7892`，与脚本 `PROXY` 变量一致

### ✅ scrape.sh 远程中文网 IndentationError（2026-07-10）
- `url_id` 和 `job = {...}` 缩进未进入 `if title and link:` 块，导致 Python 解析错误
- 修复：正确 4 空格嵌套后恢复 15 条入库

### ✅ scrape.sh 代理端口切换（2026-06-04）
- V2EX 代理从 `7897` 切到 `7892`；实际 v2ray HTTP 在 `8001`，需手动启动 7892→8001 TCP 转发桥

### ✅ scrape.sh Python 路径修复（2026-06-01）
- sandbox 中 `python3` 解析为 managed 3.14.3（pip 损坏），改用 venv：`/Users/qisoong/.workbuddy/binaries/python/envs/default/bin`

### ✅ scrape.sh git push SSH mux 挂起（2026-06-26）
- 添加 `export GIT_SSH_COMMAND="ssh -o ControlMaster=no"`，避免 SSH ControlMaster 拦截 git push

### ✅ scrape.sh git add 未包含 app.js/index.html（2026-05-15）
- `git add` 增加 `app.js index.html`，前端代码改动也能自动提交

### ✅ load_js_array 二次转义 + 海外岗位显示0（2026-04-09）
- 读取单引号字符串值后立即 unescape；禁止用正则直接 patch JS 字符串字段

### ✅ jobs-global.js 超过 GitHub 100MB 限制（2026-04-07）
- 远程岛 description 含完整 HTML，累积 347MB；统一截断到 500 字符后降至 2.5MB

### ✅ who-is-hiring NoneType 错误（2026-04-07）
- Rebase API 字段均可能为 null，全部用 `or ""` / `or []` 兜底；requirements 兼容 string/list/null

### ✅ Remote OK URL 重复拼接（2026-03-24）
- API 返回 url 已是完整 URL，判断是否以 http 开头，避免重复拼接

## UI 与数据规范
- **列表页和详情页不可出现任何数据源/网站名称字样**
- `description` 一律截断到 500 字符
- `company` 兜底：V2EX → `"海外公司"`，远程中文网 → `""`
- `sourceUrl` 为去重唯一键
- 内推数据源：V2EX + who-is-hiring；`canRefer: true` 显示"内推岗"标签，详情页按钮改为"加入社群内推"
- **非招聘帖过滤**：`scrape.sh` 约 1139 行 `TITLE_BLACKLIST` 是统一入口，命中关键词的 V2EX 标题直接跳过。已收录：`一直想做的远程工作集合网站`、`远程工作网站开放`、`从零开始远程工作指南`（2026-10-23 加入，付费课程推广帖）。发现新的非招聘/推广帖，往该列表追加关键词，而不是每次手删 jobs-cn.js（否则下次抓取会回来）
- **手动添加内推岗位**：统一写入 `jobs-mainlist.js` 数组顶部（该文件不被 scrape.sh 覆盖），id 用 `manual-YYYYMMDD-NN`，`date` 填当天（列表按日期倒序才会排在最前），`canRefer: true`

## 会员权益与兑换系统（2026-10-24 建立）
- 技术栈：Supabase + PostgreSQL；兑换码用脚本批量生成后导入
- 核心文件：`supabase/schema.sql`（表+RLS+`redeem_code()` 原子函数）、`config.js`、`auth.js`（window.Auth）、`account.html` + `account.js`
- 脚本：`scripts/gen-codes.mjs`（生成/导入兑换码）、`scripts/export-money-contacts.py` + `scripts/export-job-access.mjs`（导出权益数据）、`scripts/strip-gated-fields.mjs`（剥离前端敏感字段，需 --apply）
- **防重复兑换双重保险**：`redeem_code()` 内 `SELECT ... FOR UPDATE` 行锁 + `redemptions.code` 唯一约束（并发第二个事务直接回滚）
- `redeem_codes` 表**不给任何 RLS 策略** → 用户无法枚举兑换码，只能走 RPC
- 会员专属数据（`apply_url` / `contact`）只能存在 `job_access` 表；**前端 jobs-*.js 里的这些字段必须剥离**，否则会员权益形同虚设
- 执行顺序铁律：先导入 job-access.csv 到数据库，**再**跑 strip-gated-fields.mjs --apply，反了会丢数据
- 密钥分工：anon key 可提交（受 RLS 保护）；service_role key 只放 `.env.local`（已 gitignore）
- `config.js` 的 DEV_MODE 仅在 localhost 生效，线上自动失效（防止登录后门进生产）
- **登录方式：邮箱验证码**（2026-10-24 由手机号改）。原因：手机号需自配短信服务商+国内短信签名审核+按条计费+短信轰炸风险；邮箱开箱即用、0 成本、覆盖海外用户；防小号价值在本项目很低（未付费账号是空号）
- 邮箱登录配置见 `supabase/email-setup.md`。两个必踩的坑：①Supabase 勾了 `Confirm email` 会导致验证码登录被拦 ②邮件模板必须含 `{{ .Token }}`，否则收不到 6 位码
- 内置 SMTP 免费额度每小时仅个位数封，上线前换自定义 SMTP（海外 Resend，国内阿里云/腾讯云邮件推送）
- **schema.sql 顺序铁律**：`is_member()` 必须先于 RLS 策略创建（`job_access` 的 policy 引用它）。2026-10-26 首次在 Supabase SQL Editor 执行报 `42883 function public.is_member() does not exist`，已把函数移到第 6 节、RLS 顺延为第 7 节。脚本整体幂等，失败后可直接全文重跑
- 接线清单见 `supabase/setup-checklist.md`（建项目 → 执行 schema → 填 config.js → 配邮箱 → 生成兑换码 → 导入权益数据）
- 备选方案：`Auth.signInWithMagicLink(email)` 已实现，需要时暴露入口即可

## 每日精选板块（2026-10-26 建立）
- 数据源 `jobs-featured.js`：手动维护，scrape.sh 不覆盖；id 规范 `featured-YYYYMMDD-NN`，date 填当天（板块默认展示最近 7 天，窗口内无数据则退回最新 6 条，默认露 6 条其余折叠）
- 板块在岗位列表顶部，国内/海外两个 Tab 共享
- **精选岗必须从普通列表排除**（`getCurrentJobs()` 过滤 featuredIdSet）——否则用户从普通列表点开就能看到申请链接，付费墙失效
- **会员门控已移除（2026-10-26 用户决定）**：精选岗与普通岗统一走 `renderJobAccess()` → `defaultJobAction()`（内推岗→加入社群内推 / 有 applyUrl→申请职位 / 否则查看原帖 + 关闭），精选卡片无「会员解锁/已解锁」角标，板块头改为「每日人工筛选」。`jobs-featured.js` 里的 `contact`/`apply_url` 字段保留但前端暂不展示，将来恢复门控可直接启用
- 精选字段：内推岗填 `contact`，直申岗填 `apply_url`（下划线命名，区别于抓取数据的驼峰 `applyUrl`）
- `jobs-featured.js` 含明文权益数据，**提交前必须先跑 `strip-gated-fields.mjs --apply`**；scrape.sh 的 git add 已包含 jobs-featured.js 与 jobs-mainlist.js
- mainlist 里 3 条 `manual-20261023-*` 已迁到 featured（mainlist 剩 20 条老数据）

## 列表排序策略（2026-06-22）
- 前端 `getCurrentJobs()` 统一按日期倒序
- 数据写入 `merge_jobs()`：新数据放前面，现有数据追加后面

## money.xlsx 结构
- 第1行标题，第2行表头，第3行起为 V2EX + who-is-hiring 数据

## money.xlsx 版本管理规则（2026-10-23 确立，长期有效）
- **money.xlsx 只保留在本地机器，不提交到远程仓库**（含内推联系方式，敏感）
- 已加入根目录 `.gitignore`，并 `git rm --cached` 从索引移除（commit `d53b7aa`）
- `scrape.sh` 的 `git add` 已移除 money.xlsx，现仅提交 `jobs-cn.js jobs-global.js scrape.log app.js index.html .workbuddy/automations/automation/memory.md`
- 脚本仍会读写**本地** money.xlsx（追加 V2EX + who-is-hiring 数据），只是不再入库
- 注意：Git 历史中仍有旧版 money.xlsx，彻底清除需 `git filter-repo`（会改写历史，不轻易执行）
- 排查时若 `git status` 看到 money.xlsx 不再出现属正常现象

## AI 资讯功能
- 生成脚本：`ai-news/gen-from-feed.py`
- 内容规则：X 推文最多 8 位建造者、播客 1 段、博客 1 篇
- 页面结构：Navbar / Hero / 建造者动态 / 播客 / 博客 / 历史存档 / 页脚
- 入口：`index.html` 当天内容，`YYYY-MM-DD.html` 历史存档

## 自动化任务
- `jobs-scrape`：每天 7:30 运行 `bash scrape.sh`（当前 PAUSED）
- `ai-news`：每天 7:30 运行 `python3 gen-all.py 1`

## 数据历史（近期）
| 日期 | CN | Global | 备注 |
|------|-----|--------|------|
| 2026-09-08 | 1168 | 2000 | V2EX 1条（跳过19非今日帖），who-is-hiring 432条，7892→8001转发，自动化触发 |
| 2026-09-02 | 1151 | 2000 | V2EX 1条（跳过19非今日帖），who-is-hiring 432条，7892→8001转发，修复V2EX详情页代理为7892 |
| 2026-08-17 | 1128 | 2000 | V2EX 0条（跳过20非今日帖），who-is-hiring 432条，7892→8001转发，自动推送成功 |
| 2026-08-14 | 1120 | 2000 | V2EX 1条，所有数据源正常，7892→8001转发 |
| 2026-08-12 | 1110 | 2000 | V2EX 2条，所有数据源正常，7892→8001转发 |
| 2026-08-07 | 1092 | 2000 | V2EX 2条，远程岛/远程中文网恢复正常，手动触发 7892→8001 转发 |
| 2026-07-31 | 1072 | 2000 | V2EX 0条，远程岛/远程中文网0条(异常)，手动触发 7892→7897 转发 |
| 2026-07-27 | 1070 | 2000 | V2EX 2条，远程岛/远程中文网0条(异常)，手动触发 |
| 2026-07-15 | 1064 | 2000 | V2EX 2条，远程岛/远程中文网0条(异常)，代理7897可用，手动触发 |
| 2026-07-10 | 1058 | 2000 | 远程岛/远程中文网修复IndentationError后恢复，V2EX代理不可用0条，手动触发 |
| 2026-07-08 | 1101 | 2000 | V2EX 2条，远程岛/远程中文网0条(异常)，手动触发7892→7897转发 |
| 2026-07-07 | 1097 | 2000 | V2EX 3条，远程岛/远程中文网0条(异常)，手动触发7892→7897转发 |
| 2026-07-06 | 1094 | 2000 | V2EX 1条，远程岛/远程中文网0条(异常)，手动触发7892→7897转发 |
| 2026-07-03 | 1087 | 2000 | V2EX 5条，所有数据源正常，手动触发 |
| 2026-07-01 | 1064 | 2000 | V2EX 3条，who-is-hiring JSON损坏解析失败0条，手动触发 |
| 2026-06-29 | 1042 | 2000 | V2EX 0条，手动触发（自动化任务状态 PAUSED） |
| 2026-06-26 | 1034 | 2000 | V2EX 0条，who-is-hiring 429条，手动触发并修复 SSH mux 推送挂起 |
| 2026-06-22 | 1006 | 2000 | V2EX 2条，自动化触发 |
| 2026-06-18 | 995 | 2000 | V2EX 0条，手动触发（自动化间隔2天未跑） |
| 2026-06-16 | 982 | 2000 | V2EX 0条，手动触发 |
| 2026-06-11 | 963 | 2000 | V2EX 1条，自动更新 |
| 2026-06-07 | 941 | 2000 | V2EX 0条（跳过20非今日帖），自动化触发 |
| 2026-06-04 | 927 | 2000 | V2EX代理切7892恢复4条，手动触发 |
| 2026-06-03 | 912 | 2000 | V2EX代理不可用，自动更新 |
| 2026-06-01 | 901 | 2000 | V2EX 2条，自动更新 |
| 2026-04-25 | 696 | 2000 | V2EX 1条，自动更新 |
| 2026-04-14 | 583 | 1957 | V2EX 1条，自动更新 |
| 2026-04-10 | 566 | 1688 | V2EX 2条，手动触发 |
| 2026-04-09 | 557 | 1617 | 自动更新，修复海外显示0 |
| 2026-04-08 | 548 | 1566 | V2EX 3条，手动触发 |
| 2026-04-07 | 537 | 1505 | 修复 NoneType + 文件过大 |
