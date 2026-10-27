# 项目长期记忆

## 项目概况
- **Junes远程工作聚合网站**，路径 `/Users/qisoong/WorkBuddy/20260317141747/`
- 技术栈：纯静态 HTML/CSS/JS + Python 爬虫脚本（`scrape.sh`）
- 数据文件：`jobs-cn.js`（国内）、`jobs-global.js`（海外，上限2000）、`jobs-featured.js`（每日精选）、`jobs-mainlist.js`（手动内推）、`money.xlsx`（本地，不入库）

## 数据源
| 数据源 | 类型 | 要点 | 内推 |
|--------|------|------|------|
| Remote OK | 海外 | JSON API；url 已是完整 URL，勿重复拼接 | 否 |
| Remotive | 海外 | JSON API 直连 | 否 |
| 远程岛 | 海外 | description 含完整 HTML，必须截断到 500 字（曾撑到 347MB 超 GitHub 100MB 限制） | 否 |
| Working Nomads | 海外 | 公开 JSON API `api/exposed_jobs/`，约39条/次，字段齐全(url/title/desc/company_name/location/pub_date) | 否 |
| Himalayas | 海外 | 公开 RSS `jobs/rss`，约20条/次。**公司名在命名空间字段 `himalayasJobs:companyName`**（不是 `<company>`） | 否 |
| ~~remote-china.com~~ | — | **已彻底移除（2026-10-27）**：抓取源代码（下载段/解析段/合并引用）与线上 529 条存量数据全部删除。曾长期被注释写作「远程中文网」，实为同一站点，勿当成两个源 | — |
| **智联招聘** | 国内 | HTML + `__INITIAL_STATE__` → `positionList[]`，顶层直接有 name/companyName/salary60/workCity/positionUrl/publishTime。**必须严格过滤，见下**。**只进库、不进精选池**：字段 `noFeature: True`，审核台按 `noFeature` 或 source 含 zhaopin 排除（存量旧数据无该字段，靠 source 兜底） | 否 |
| V2EX | 国内 | HTML 抓取，需代理 `127.0.0.1:7892` | ✅ |
| who-is-hiring | 国内 | JSON API，**所有字段可能为 null**，用 `or ""`/`or []` 兜底 | ✅ |
| ~~电鸭~~ | — | **死代码已删**（2026-10-27）：只有 open 无 curl，每日志报"文件不存在"。788 行 eleduck 外链识别属 V2EX 正文逻辑，保留 | — |
| ~~BOSS直聘~~ | — | **评估后否决（2026-10-27）**：curl 只返回 9.6KB SPA 空壳、零 JSON，数据需 JS 渲染 + `__zp_stoken__` 签名破解。投入产出比极差，不建议碰 | — |

**智联招聘严格过滤（2026-10-27 实测）**：搜索词命中率差异极大 —— `居家办公` **19/20**、 `远程办公` 11/20、`远程` 仅 9/20（后者大量命中「远程面试」陷阱 + 开票会计等无关岗）。**必须用「居家办公」+「远程办公」双词抓取，不要用「远程」**。过滤逻辑：先剔黑名单 `远程面试`（面试远程 ≠ 工作远程），再要求命中白名单（远程办公/居家办公/在家办公/可远程/远程工作/全远程/远程岗/线上远程/纯远程/远程授课/线上作业/远程兼职 等）。实测两词合并去重后约 30 条/次。注意：智联岗位偏兼职零工（数据标注/游戏讲解/网店上品），与海外源的 Senior 级白领岗有质量落差。

**remote-china.com 改版要点（2026-10-27 修复）**：列表项从 `<a class="job-item">` 变为 `<div class="job-item">`，链接下移到子 `<a class="job-link">`，故 `soup.select('a.job-item')` 会静默匹配 0 条。另有独立 `.job-salary` 真实薪资、`<time datetime>` 真实发布日（取前10位，兜底 DATE）。**页面再次改版时优先复查这几个选择器**。

## 实操铁律（踩过的坑）
- **Python 路径**：sandbox 中 `python3` 会解析到 pip 损坏的 managed 3.14.3，必须用 venv `/Users/qisoong/.workbuddy/binaries/python/envs/default/bin`
- **git push**：必须 `GIT_SSH_COMMAND="ssh -o ControlMaster=no" git push`，否则 SSH ControlMaster 挂起
- **V2EX 代理**：列表页与详情页 curl 代理必须统一为 `7892`（曾因详情页硬编码 7897 全量失败）；实际 v2ray HTTP 在 `8001`，需手动起 7892→8001 TCP 转发桥
- **JS 数组读写**：读取单引号字符串值后立即 unescape，禁止用正则直接 patch JS 字符串字段（二次转义曾致海外显示 0）
- **money.xlsx 不入库**：已在 `.gitignore` + `git rm --cached`，scrape.sh 只读写本地不提交；git status 看不到它是正常的
- **非招聘帖过滤**：统一走 `scrape.sh` 约 1139 行 `TITLE_BLACKLIST` 追加关键词，不要手删 jobs-cn.js（下次抓取会回来）

## UI 与数据规范
- 列表页/详情页**不可出现任何数据源或网站名称字样**
- `description` 一律截断 500 字符；`company` 兜底：V2EX→`"海外公司"`，远程中文网→`""`
- `sourceUrl` 为去重唯一键；前端 `getCurrentJobs()` 按日期倒序，`merge_jobs()` 新数据在前
- 内推源：V2EX + who-is-hiring；`canRefer: true` 显示"内推岗"标签，详情页按钮改"加入社群内推"
- 手动内推岗写入 `jobs-mainlist.js` 顶部（不被 scrape.sh 覆盖），id 用 `manual-YYYYMMDD-NN`，date 填当天

## 每日精选板块（jobs-featured.js）
- 手动维护，id 规范 `featured-YYYYMMDD-NN`，展示最近 7 天，默认露 6 条其余折叠
- **精选岗必须从普通列表排除**（`getCurrentJobs()` 过滤 featuredIdSet），否则付费墙失效
- 会员门控已移除（2026-10-26），与普通岗统一走 `renderJobAccess()`；`contact`/`apply_url` 字段保留待启用
- 含明文权益数据，**提交前必须先跑 `scripts/strip-gated-fields.mjs --apply`**
- **人工把关流程（2026-10-27 起，推荐路径）**：候选先进 `jobs-featured-pending.js` 待审池 → 本地 `review.html` 审核台逐条过审（可改写 description 人工摘要、淘汰离谱的）→ 点「上线」自动填 id/date=当天 → 底部「导出」覆盖 `jobs-featured.js` 与 pending 文件。标准学 remote-china：宁缺毋滥
- `review.html` 是本地工具，**绝不可部署**（会暴露待审池与 contact/apply_url），已在 `.vercelignore` 排除；换部署方式需手动排除。预览：`python3 -m http.server 8765` → `http://localhost:8765/review.html`
- 导出序列化要点：null 要写成 `null`（不能变空串）、`_from`/`_srcId` 内部字段导出时剔除

## 会员权益与兑换系统
- Supabase + PostgreSQL；核心：`supabase/schema.sql`、`config.js`、`auth.js`、`account.html/js`
- **防重复兑换**：`redeem_code()` 内 `SELECT ... FOR UPDATE` 行锁 + `redemptions.code` 唯一约束
- `redeem_codes` 表不给任何 RLS 策略 → 用户只能走 RPC，无法枚举兑换码
- 会员数据（`apply_url`/`contact`）只存 `job_access` 表，前端 jobs-*.js 必须剥离
- **执行顺序**：先导入 job-access.csv，**再**跑 strip-gated-fields.mjs --apply（反了丢数据）
- **schema.sql 顺序**：`is_member()` 必须先于引用它的 RLS 策略创建（第6节 vs 第7节），整体幂等可重跑
- 密钥：anon key 可提交；service_role 只放 `.env.local`。`DEV_MODE` 仅 localhost 生效
- **登录用邮箱 Magic Link**（非验证码、非短信）。坑：`emailRedirectTo`（`https://remotework.asia/account.html`）必须在 Supabase 控制台 Redirect URLs 白名单内，否则静默回退 localhost；模板须含 `{{ .ConfirmationURL }}`
- 内置 SMTP 每小时仅个位数封，上线前换自定义 SMTP（海外 Resend / 国内阿里云）
- 接线清单见 `supabase/setup-checklist.md`

## 内容板块
- **AI独立派**（`ai-indie/`）：24+ 篇，`index.html` 内 `ARTICLES` 数组；同步脚本 `sync-articles.sh`
- **一人公司赚钱样本**（`indie-money-samples/`）：4 篇（#001 levelsio / #002 typingmind / #003 bibly / DataFast）。两板块统一品牌绿 `#2C5530`
- **AI 资讯**（`ai-news/`）：生成脚本 `gen-from-feed.py`，X 推文最多 8 位建造者

## 自动化任务
- `jobs-scrape`：每天 7:30 `bash scrape.sh`（当前 PAUSED）
- `ai-news`：每天 7:30 `python3 gen-all.py 1`

## 竞品参考（2026-10-27 分析 remote-china.com）
- 个人站（greatghoul，西安），方法论在 `/about` 公开：**半自动采集 + 人工把关**，非纯爬虫
- 工具链进化：小书签 → 油猴脚本 → Chrome 扩展（自动发 TG/豆瓣）
- 有效性核心：运营者本人读每条 JD 写人工摘要（DeepSeek 仅补充），**日均仅发 6-10 条**，标准"看起来不至于太离谱"
- 积分闭环：签到得积分、投稿花1积分采纳返3（净+2）、积分解锁链接/邮件推送；既是反垃圾门槛也降低爬虫价值
- 透明化：岗位页公示用户举报与审核记录；robots 禁 AI 训练爬虫，有公开 API/RSS
- 对本站启示：在全自动 1000+ 条之外强化"每日精选"层 + AI 摘要 JD + 社区举报公示

## 数据规模趋势
- CN 从 2026-04 的 537 增长到 2026-09 的 1168，Global 稳定 2000 上限
- V2EX 每次通常 0-5 条（大量非今日帖被跳过）；who-is-hiring 单次约 430 条是主要增量
- 远程岛/远程中文网长期不稳定，多次返回 0 条
