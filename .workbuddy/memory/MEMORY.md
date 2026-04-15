# 项目长期记忆

## 项目概况
- **项目**：Junes远程工作聚合网站
- **路径**：`/Users/qisoong/WorkBuddy/20260317141747/`
- **技术栈**：纯静态 HTML/CSS/JS + Python 爬虫脚本（`scrape.sh`）
- **数据文件**：`jobs-cn.js`（国内）、`jobs-global.js`（海外）、`money.xlsx`（V2EX内推记录）

## 数据源
| 数据源 | 类型 | 说明 |
|--------|------|------|
| Remote OK | 海外 | JSON API 直连，description 截断 500 字 |
| Remotive | 海外 | JSON API 直连 |
| 远程岛 | 海外 | JSON API，description 含完整 HTML 必须截断 |
| 远程中文网 | 国内 | HTML 抓取，直连 |
| V2EX | 国内 | HTML 抓取，需代理 `http://127.0.0.1:7897` |
| who-is-hiring（Rebase） | 国内 | JSON API，所有字段可能为 null |
| 电鸭 | 国内 | JS渲染，curl 无法抓取，跳过 |

## Bug 修复记录（重要，避免重蹈覆辙）

### ✅ scrape.sh 无 git 推送逻辑（已修复，2026-04-10）
- **现象**：脚本运行成功但数据未推送到 GitHub
- **根因**：脚本末尾没有 `git add/commit/push`
- **修复**：在脚本末尾加入 git 自动提交推送块（检查是否有变更才提交）
- **同步修复**：主 Python 段 `python3 << 'EOF'` 改为 `python3 << 'EOF' 2>&1 | tee -a $LOG_FILE`，错误信息写入日志

### ✅ load_js_array 二次转义 + 海外岗位显示0（已修复，2026-04-09）
- **根因①**：`load_js_array()` 读取时不还原 JS 转义 → 每次写回多一层转义
- **根因②**：用正则 patch JS 文件时遇到 `\'` 提前截断 → JS 语法错误
- **修复**：`load_js_array()` 第1281行，读取单引号字符串值后立即 unescape
- **教训**：**禁止用正则直接操作 JS 文件字符串字段**；description 截断必须在 Python 原始数据阶段完成

### ✅ jobs-global.js 超过 GitHub 100MB 限制（已修复，2026-04-07）
- **根因**：远程岛 description 含完整 HTML（单条最大 3.4MB），历史数据累积到 347MB
- **修复**：所有数据源 description 统一截断到 500 字符，文件 347MB→2.5MB
- **教训**：每次生成数据文件后检查文件大小；`description[:500]` 是硬性规则

### ✅ who-is-hiring NoneType 错误（已修复，2026-04-07）
- **根因**：Rebase API 字段（work_mode/company/requirements 等）均可能为 null
- **修复**：所有字段用 `or ""` / `or []` 兜底；requirements 兼容 string/list/null 三种类型
- **修复位置**：`scrape.sh` who-is-hiring 处理段（约659-730行）、`build_job_desc()` 函数

### ✅ Remote OK URL 重复拼接（已修复，2026-03-24）
- **根因**：API 返回的 url 已是完整 URL，代码又拼接了域名前缀
- **修复**：判断是否以 http 开头，避免重复拼接

## UI 规范（硬性要求）
> ⚠️ **列表页和详情页不可出现任何数据源/网站名称字样**

- 公司名无效值（`app.js` `formatCompany()`）：`（V2EX用户招聘）`、`远程中文网`、`Remote China`
- 描述无效值（`INVALID_DESCRIPTIONS`）：`来自V2EX远程工作社区的招聘帖子`、`来自远程中文网的远程工作机会`
- 职责/要求行过滤（`filterSourceLines()`）：含 `v2ex.com`、`remote-china.com` 的行

## 数据规范
- `description` 字段：一律截断到 500 字符，禁止填占位语
- `company` 兜底值：V2EX → `"海外公司"`，远程中文网 → `""` 空字符串
- `sourceUrl`：去重唯一键（不用 id）

## 列表排序策略（硬性规则）
**前端展示（`app.js`）**：`sortWithReferralFirst()` 函数统一处理
1. `canRefer: true` 的内推岗位强制置顶（不受日期影响）
2. 其余岗位按日期倒序（最新的在前）

**数据写入（`scrape.sh`）**：`merge_jobs()` 函数处理
- 新数据（V2EX → 远程中文网 → 电鸭 → who-is-hiring → 海外）放在 `jobs-cn.js` / `jobs-global.js` 最前面
- 现有数据追加在后面
- 最终文件内顺序与前端展示顺序一致

## money.xlsx 结构
- 第1行：标题"数字游民Junes 远程工作共创群"
- 第2行：表头（12列）：公司、行业、职位类别、职位名称、地区、申请链接、内推、日期、工作职责&任职要求、薪资、内推方式、来源
- 每天 V2EX 新帖 + who-is-hiring 数据插入第3行起

## AI 资讯功能（AI News）

### 功能概述
每天自动生成 AI 领域精选资讯网页，展示最有价值的深度内容。

### 内容生成规则（硬性规则）
| 内容类型 | 数量 | 来源 | 处理方式 |
|----------|------|------|----------|
| **X 推文** | 最多8位建造者 | Follow Builders | 按总点赞数排序，每位最多3条推文 |
| **播客** | 3 段 | Follow Builders | 分段提取精华（每段1500字符） |
| **博客** | 2 段 | Follow Builders | 分段提取精华（每段1500字符） |

### 数据源
- **数据源项目**：[Follow Builders](https://github.com/zarazhangrui/follow-builders)
- **数据文件路径**：`~/.workbuddy/skills/follow-builders/`
  - `feed-x.json` - X/Twitter 开发者动态
  - `feed-podcasts.json` - AI 播客内容
  - `feed-blogs.json` - 技术博客文章

### 技术实现（2026-04-15 定型版本）
- **生成脚本**：`ai-news/gen-index.py`
- **参考样式**：`/Users/qisoong/work/Work/remotework/ai-news/2026-04-13.html`（此为标准设计稿）
- **自动化任务**：每天 7:30 自动执行（Automation ID: `ai`）

### 页面结构（对标 2026-04-13.html，硬性规范）
1. **Navbar**：白色顶栏，含"远程岗位 / 科技公司 / AI资讯"链接 + 中英切换按钮 + 全文朗读
2. **Hero**：蓝色渐变大头部（`#1E3A5F → #2563EB`），含日期 + 建造者/推文/播客/博客统计徽章
3. **Section 建造者动态**：`tag 🐦 X / Twitter` + 建造者卡片（头像 + handle + bio + 多条推文）
4. **Section 播客**：`tag green 🎙️` + podcast-card（标题 + 来源 + 字幕摘要黄色背景区）
5. **Section 官方博客**：`tag purple 📝` + blog-card（来源 + 标题 + 链接）
6. **历史存档**：底部 archive-list 展示最近10个日期
7. **页脚**：数据来源 + 主站链接

### 中英文切换规范
- 所有中文内容包裹 `<span class="zh-text">` 或带 class `zh-text`
- 所有英文内容包裹 `<span class="en-text" style="display:none">`
- 切换逻辑：`setLang('zh'/'en')` 批量切换所有 `.zh-text` / `.en-text` 的 `display`
- 语音朗读按当前语言选读对应文本，语速 0.85x，音调 0.95

### 入口逻辑
- 首页导航 → AI资讯 → 直接进入当天资讯详情页
- `index.html` = 当天内容（每天自动更新）
- `YYYY-MM-DD.html` = 历史存档

## 自动化任务（2026-04-14）

### 每日职位数据更新
- **ID**: `jobs-scrape`
- **路径**: `.workbuddy/automations/jobs-scrape/automation.toml`
- **时间**: 每天 7:30
- **执行**: 运行 `bash scrape.sh`，抓取所有数据源职位并推送到 GitHub

### 每日AI资讯生成
- **ID**: `ai-news`
- **路径**: `.workbuddy/automations/ai-news/automation.toml`
- **时间**: 每天 7:30
- **执行**: 运行 `python3 gen-index.py`，生成当日 AI 资讯页面并推送到 GitHub

## 数据历史（近期）
| 日期 | CN | Global | 备注 |
|------|-----|--------|------|
| 2026-04-14 | 583 | 1957 | V2EX 1条，自动更新 |
| 2026-04-10 | 566 | 1688 | V2EX 2条，手动触发 |
| 2026-04-09 | 557 | 1617 | 自动更新，修复海外显示0 |
| 2026-04-08 | 548 | 1566 | V2EX 3条，手动触发 |
| 2026-04-07 | 537 | 1505 | 修复 NoneType + 文件过大 |
