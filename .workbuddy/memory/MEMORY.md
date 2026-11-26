# 项目长期记忆

## 项目
- Junes 远程工作聚合站 `/Users/qisoong/WorkBuddy/20260317141747/`，纯静态 HTML/CSS/JS + `scrape.sh` 爬虫
- 数据文件：jobs-cn.js（国内）/ jobs-global.js（海外，上限2000）/ jobs-featured.js（每日精选，手动维护）/ jobs-mainlist.js（手动内推）/ money.xlsx（本地，不入库）
- 品牌绿 `#2C5530`

## 数据源（2026-11 生效）
**海外**：Remote OK（url 已是完整 URL，勿重复拼接）、Remotive（直连超时，必须走代理）、远程岛（desc 含完整 HTML，必须截断 500 字，曾撑到 347MB）、Working Nomads（JSON `api/exposed_jobs/`，约39条）、Himalayas（RSS，公司名在 `himalayasJobs:companyName` 而非 `<company>`）

**国内**：V2EX（需代理 7892，内推）、who-is-hiring（JSON，字段可能全为 null，需 `or ""` 兜底，内推）、智联招聘（居家办公+远程办公**双词**，黑名单剔「远程面试」+ 白名单命中；`noFeature:True` 只进库不进精选）、远程.work（SSR + JSON-LD，分页 `/page/2` 无尾斜杠）、远程工作网（`yuanchenggongzuo.net` 公开 API，pageSize 钳 20 拉 40 页，**有频控：必须串行 + sleep 1.5s**，约800条/次）

**已弃**：remote-china.com（2026-10-27 源码+存量全删）、电鸭（死代码已删）、BOSS直聘（SPA+签名，否决）、豆瓣小组（详情 403，未接入）

## 实操铁律
- Python 用 venv：`/Users/qisoong/.workbuddy/binaries/python/envs/default/bin`
- git push 必须 `GIT_SSH_COMMAND="ssh -o ControlMaster=no"`
- 代理桥已入库 `scripts/proxy_bridge.py`（7892 → v2ray 实际 8001）；V2EX 列表页与详情页统一 7892
- 所有 curl 带 `--connect-timeout 12 --max-time 30`；详情页必须 `ThreadPoolExecutor` 并发（串行是最大时间黑洞）
- `filter_fresh()` 合并后丢弃 >89 天岗位（对齐前端 `MAX_JOB_AGE_DAYS=90`），别只靠前端过滤
- money.xlsx 在 `.gitignore` 且 `git rm --cached`，只读写不提交；`.gitignore` 另有 `money.xlsx.*` 覆盖备份副本
- money.xlsx 写入必须**先按 sourceUrl 去重再 insert_rows**（2026-11-26 事故：每日重复插 435 条 Rebase 帖子 → 28033 行 / 60MB sheet XML，save 卡死 80 分钟，进程被杀后文件被截断）。健康状态：约 480 行 / 392KB，save < 1s
- openpyxl `insert_rows` 在万行级表上是性能地雷；`wb.save()` 中途被 kill 会直接截断目标文件，写前务必 `.bak`
- 非招聘帖过滤走 scrape.sh 的 `TITLE_BLACKLIST`，勿手删 jobs-cn.js（下次会回来）
- 批量删改 jobs-*.js：状态机切顶层对象块（勿用正则），保留块原样文本拼回，连接符 `',\n  '`；校验 `git diff | grep '^+{'` 应为空

## UI 与数据规范
- 列表页/详情页**禁止出现任何数据源或网站名称**
- `description` ≤500 字符；`company` 兜底：V2EX → `"海外公司"`
- `sourceUrl` 为去重唯一键；前端按日期倒序
- 内推源 V2EX + who-is-hiring，`canRefer: true` 显示「内推岗」

## 每日精选（jobs-featured.js）
- id `featured-YYYYMMDD-NN`，展示近 7 天，默认露 6 条其余折叠
- **必须从普通列表排除**：`featuredIdSet` + `featuredSourceUrlSet()`（`notFeatured()`）双排除；精选条目务必填 `sourceUrl` 否则双份展示、付费墙失效
- 流程：候选进 `jobs-featured-pending.js` → 本地 `review.html` 审核台过审（可改写摘要）→ 导出覆盖。宁缺毋滥
- `review.html` 是本地工具**绝不可部署**（`.vercelignore` 已排除）
- 含明文权益数据，提交前必跑 `scripts/strip-gated-fields.mjs --apply`

## 会员与兑换（Supabase）
- `supabase/schema.sql` 幂等；`is_member()` 必须先于引用它的 RLS 策略创建
- `redeem_code()` 用 `SELECT ... FOR UPDATE` + redemptions.code 唯一约束防重复；redeem_codes 不给 RLS 策略
- **顺序**：先导入 job-access.csv，再跑 strip-gated-fields（反了丢数据）
- 会员字段（apply_url/contact）只存 `job_access` 表
- 登录用邮箱 Magic Link（非验证码）；`emailRedirectTo` 必须在 Supabase Redirect URLs 白名单内
- anon key 可提交，service_role 只放 `.env.local`

## 内容板块
- `ai-indie/`（AI独立派，index.html 内 `ARTICLES` 数组，`sync-articles.sh` 同步）
- `indie-money-samples/`（一人公司赚钱样本，4 篇）
- `ai-news/`（AI 资讯，`gen-from-feed.py` 生成）

## 自动化（4 个）
- ✅ `automation` 每日职位数据更新 7:30；✅ `ai-7` AI 资讯每日生成 7:30
- ⏸ `ai-4` AI独立派文章 6:00；⏸ `automation-1780474022669` 一人公司样本 9:00
- 改状态后 nextRunAt 可能残留旧值，做一次 PAUSED→ACTIVE 切换强制刷新

## 竞品 remote-china.com（greatghoul）
半自动采集 + 人工把关，非纯爬虫；运营者本人读 JD 写摘要，日均仅 6-10 条；积分闭环（签到得分、投稿花1返3）；岗位页公示举报与审核。启示：在千条全自动之外强化「每日精选」层 + AI 摘要 + 举报公示。

## 规模趋势
- CN：2026-04 的 537 → 2026-09 的 1168 → 2026-11-18 接入远程工作网后 1098
- 海外源长期顶格 2000；V2EX 每次 0-5 条；who-is-hiring 约 430 条为主增量
