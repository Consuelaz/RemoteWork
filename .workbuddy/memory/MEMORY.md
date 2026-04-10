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
- V2EX 数据：`canRefer: true`，放 `jobs-cn.js` 最顶部

## money.xlsx 结构
- 第1行：标题"数字游民Junes 远程工作共创群"
- 第2行：表头（12列）：公司、行业、职位类别、职位名称、地区、申请链接、内推、日期、工作职责&任职要求、薪资、内推方式、来源
- 每天 V2EX 新帖 + who-is-hiring 数据插入第3行起

## 数据历史（近期）
| 日期 | CN | Global | 备注 |
|------|-----|--------|------|
| 2026-04-10 | 566 | 1688 | V2EX 2条，手动触发 |
| 2026-04-09 | 557 | 1617 | 自动更新，修复海外显示0 |
| 2026-04-08 | 548 | 1566 | V2EX 3条，手动触发 |
| 2026-04-07 | 537 | 1505 | 修复 NoneType + 文件过大 |
