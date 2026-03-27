# 项目长期记忆

## 项目概况
- **项目**：Junes远程工作聚合网站
- **路径**：`/Users/qisoong/WorkBuddy/20260317141747/`
- **技术栈**：纯静态 HTML/CSS/JS + Python 爬虫脚本

## 已知 Bug 与修复记录

### ⚠️ Remote OK URL 重复拼接 Bug（已修复，2026-03-24）
- **位置**：`scrape.sh` 中 Python 处理 Remote OK 数据段
- **根本原因**：Remote OK API 返回的 `url` 字段本身已是完整 URL（如 `https://remoteok.com/remote-jobs/...`），但代码里又拼接了 `"https://remoteok.com" + url`，导致生成 `https://remoteok.comhttps://remoteok.com/...` 这样的错误链接
- **修复方案**：改为 `item.get("url","") if item.get("url","").startswith("http") else "https://remoteok.com" + item.get("url","")`
- **已修复文件**：`scrape.sh`（逻辑修复）、`jobs-global.js`（历史数据批量修复，共 100 处）
- **教训**：每次脚本生成 `jobs-global.js` 后，务必抽样检查 `sourceUrl` 是否为合法 URL

## 数据抓取脚本
- **脚本**：`scrape.sh`（Bash + 内嵌 Python）
- **数据源**：Remote OK（JSON API，直连）、远程中文网（HTML，直连）、V2EX（HTML，需代理）
- **代理配置**：V2EX 使用 HTTP 代理 `http://127.0.0.1:7897`
- **电鸭（eleduck.com）**：JavaScript 渲染，curl 无法直接抓取，暂时跳过
- **输出文件**：`jobs-cn.js`（国内）、`jobs-global.js`（海外）

### 远程中文网详情页抓取（2026-03-27 增强）
- `parse_remotechina_detail()` 函数扩展：除提取申请链接外，还从 `.markdown-content` 提取岗位描述、职责、要求
- 结构：`.markdown-content` 包含 AI 总结，按"岗位职责"/"技能要求"段落分类
- `company` 兜底：列表页 `.job-team-name` 无内容时填 `""`（不填"远程中文网"）
- `description` 填 `detail_info.get('description', '')`（不填占位语）


- 使用 `.topic_content` 作为正文块（替代 `#Main`），避免误抓回复内容
- 公司名提取优先级：正文`【公司名】` > `公司：xxx` > `我司是xxx` > 标题模式 > "海外公司"
- 工作职责：优先提取"岗位职责/任职要求"结构化段落；若为空，兜底取正文全部行（过滤联系方式，最多30行）
- **只保留当天帖子**：从列表页 `span[title]` 的 `title` 属性取时间戳，对比当日日期，非今天跳过
- **标题黑名单过滤（2026-03-27）**：在列表处理段新增 `TITLE_BLACKLIST`，过滤非招聘内容（如网站上线公告等），命中直接跳过
  - 当前黑名单：`一直想做的远程工作集合网站`、`远程工作网站开放`
  - 代码位置：`scrape.sh` V2EX 列表处理段，时间过滤之前
  - **如需新增黑名单关键词**，在 `scrape.sh` 的 `TITLE_BLACKLIST` 列表中追加即可

## 数据去重机制（2026-03-27）

### 去重规则
- **唯一键**：`sourceUrl`（原帖/职位详情页链接），非 `id`（id 可能因 hash 不同而不同）
- **优先级**：新抓取的数据优先（放前面），旧数据如 sourceUrl 重复则丢弃
- **触发时机**：每次 `scrape.sh` 运行，`merge_jobs()` 函数在合并新旧数据后自动去重

### 关键函数（scrape.sh）
```python
def dedup_by_source_url(jobs):
    """按 sourceUrl 去重，保留最新那条"""
    seen = {}
    result = []
    for job in jobs:
        key = job.get('sourceUrl', '') or job.get('id', '')
        if key and key not in seen:
            seen[key] = True
            result.append(job)
    return result

def merge_jobs(old_jobs, new_jobs):
    merged = new_jobs + old_jobs  # 新数据放前
    return dedup_by_source_url(merged)
```

### 历史数据清理（2026-03-27）
- jobs-cn.js：762 → 78 条（去重 684 条）
- jobs-global.js：2000 → 808 条（去重 1192 条）



> ⚠️ **不可在列表页和详情页中出现任何数据源/网站名称字样。** 这是硬性要求。

### 公司名过滤（app.js `formatCompany()`）
以下公司名视为无效，显示为空：
- `（V2EX用户招聘）`
- `远程中文网`
- `Remote China` / `remote-china`
- 如有新数据源公司名占位符，追加到 `INVALID_COMPANY_NAMES` 数组

### 岗位描述过滤（app.js `INVALID_DESCRIPTIONS`）
以下描述视为无效，不显示"岗位描述"区块：
- `来自V2EX远程工作社区的招聘帖子`
- `来自远程中文网的远程工作机会`

### 职责/要求列表过滤（app.js `filterSourceLines()`）
过滤 `responsibilities` / `requirements` 中含以下域名的行（避免原帖链接出现在详情页）：
- `v2ex.com`
- `remote-china.com`

### 数据源字段规范（scrape.sh）
- `company` 兜底值：V2EX → `"海外公司"`，远程中文网 → `""`（空字符串，不填占位符）
- `description` 兜底值：一律用 `""` 空字符串，**禁止填写"来自xxx网站"等占位语**

## UI 逻辑
- **分类标签**：`app.js` 中 `buildCategoryTags()` 动态从数据中读取，不依赖硬编码列表
- **内推按钮**：`canRefer: true` 的岗位显示"加入社群内推 →"并链接到 `community.html`；其他岗位显示"查看原帖投递 →"或"申请职位 →"
- **V2EX 岗位**：自动标记 `canRefer: true` 和 `tags: ["远程", "V2EX", "社群内推"]`，数据放在 `jobs-cn.js` 顶部
- **岗位排序**：按日期倒序（最新在前），通过 `getCurrentJobs()` 中的 `sort()` 实现
- **内推岗标识**：列表卡片显示 "👥 内推岗" 标签

### 列表展示优化（2026-03-24 下午）
- 列表中过滤掉 "V2EX"、"远程"、"社群内推" 等冗余标签
- 只保留"内推岗"标识（当 canRefer: true 时）
- 详情页标签也做同样过滤

### 详情页占位符修复（2026-03-24 下午）
- 公司介绍/岗位描述字段如果内容少于10个字符，不显示该区块
- 避免显示"公司背景"等无意义占位符
- 每次抓取后检查数据质量

## 数据更新流程（2026-03-24 更新）
- **抓取**：每天自动从 V2EX、远程中文网、Remote OK 抓取数据
- **处理**：
  - V2EX 数据自动标记为"社群内推"，放在 `jobs-cn.js` 最顶部
  - 自动推断职位分类（前端开发、后端开发、AI/算法等）
- **Excel 同步**：抓取的 V2EX 数据会自动插入 `money.xlsx` 表格顶部（公司、行业、职位类别、职位名称、地区、申请链接）

## money.xlsx 表格结构（2026-03-27 更新）
- 第1行：标题 "数字游民Junes 远程工作共创群"
- 第2行：表头（12列）：[公司, 行业, 职位类别, 职位名称, 地区, 申请链接, 内推（来源：Junes数字游民社群）, 日期, 工作职责&任职要求, 薪资, 内推方式, 来源]
- 第3行起：数据行，每天抓取的 V2EX 内推岗位会插入到此位置

### money.xlsx 各列写入规则（2026-03-27 确认）
| 列 | 字段 | 规则 |
|----|------|------|
| 1 | 公司 | 从页面/标题提取公司名；抓不到填 "海外公司" |
| 2 | 行业 | 固定填 "互联网" |
| 3 | 职位类别 | 自动推断（前端/后端/AI/算法等） |
| 4 | 职位名称 | 原始标题 |
| 5 | 地区 | 固定填 "Remote" |
| 6 | 申请链接 | 固定填 "内推岗" |
| 7 | 内推 | 固定填 "星球同学 私Junes内推" |
| 8 | 日期 | 抓取日期 |
| 9 | 工作职责&任职要求 | 岗位职责+任职要求，**去掉联系方式行** |
| 10 | 薪资 | 从详情页提取，抓不到填 "面议" |
| 11 | 内推方式 | 从详情页提取联系方式（邮箱/微信/电话）；抓不到填 "星球同学 私Junes内推" |
| 12 | 来源 | 原帖链接（V2EX 帖子 URL） |

### 联系方式提取逻辑（scrape.sh parse_v2ex_detail）
- 邮箱：正则 `[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}`
- 微信：`微信[：:\s]*xxx` / `wx[：:\s]*xxx` / `wechat[：:\s]*xxx`
- 电话：`(?:电话|手机|Tel|Phone)[：:\s]*[0-9\-\+\s]{7,15}`
- 其他：Telegram / 简历投递方式等
- 结果存入 `contact` 字段，写入"内推方式"列

## 2026-03-24 下午更新内容

### UI 列表显示优化
- **职位名称截断**：列表页超过28字符显示"..."，详情页超过50字符显示"..."
- **公司名处理**：超过20字符截断，V2EX用户招聘统一显示"V2EX用户招聘"
- **代码位置**：`app.js` 中 `renderJobs()` 和 `openModal()` 函数

### V2EX 公司名提取优化
- 使用多种正则模式匹配公司名：【公司名】、"公司名 招聘"、公司名-远程 等
- 黑名单过滤：排除"远程"、"全职远程"等无效公司名
- 代码位置：`scrape.sh` 中 V2EX 处理段

### Remote OK 详情页抓取（新增）
- 预下载前10个海外岗位的详情页
- 尝试提取职位描述、任职要求、福利待遇
- 代码位置：`scrape.sh` 中 `parse_remoteok_detail()` 函数

## Skill 创建
- **路径**：`~/.workbuddy/skills/junes-remote-jobs/`
- **包含**：项目结构说明、数据字段定义、常用操作指南、问题排查
- **用途**：后续数据更新和 UI 修改参考

### 移除 V2EX 显示文字（2026-03-24 下午 + 2026-03-25 更新）
- **问题**：列表页和详情页显示"（V2EX用户招聘）"字样，影响用户体验
- **修复**：
  - 列表页：`formatCompany()` 函数检测到"（V2EX用户招聘）"返回空字符串
  - 详情页：`openModal()` 中同样使用 `formatCompany()` 处理公司名显示
  - **2026-03-25 更新**：彻底移除所有 fallback 到 "V2EX用户招聘" 的显示逻辑
  - 标签过滤：已过滤 ['V2EX', '远程', '社群内推'] 冗余标签
- **数据文件**：`jobs-cn.js` 中 company 字段仍保留"（V2EX用户招聘）"，但前端不显示
- **代码位置**：`app.js` 第26-30行 `formatCompany()` 函数、列表和详情页公司名显示处

### 内推岗标识设计（2026-03-25）
- **设计**：使用 SVG icon（两人图标）替代 emoji 👥
- **代码**：`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`
- **样式**：`.refer-badge` 蓝色背景 (#dbeafe)，文字颜色 (#1e40af)
- **应用位置**：列表卡片、详情页标题旁

### 智能提取职位名称（2026-03-24 下午）
- **功能**：从完整标题中自动提取核心职位名（如"运维开发工程师"）
- **匹配类型**：
  - 高级职位：架构师、技术负责人、总监、VP
  - 管理职位：经理、主管、负责人、组长
  - 技术职位：全栈/后端/前端/客户端/算法/数据/安全/测试/运维/DevOps/SRE工程师
  - 开发职位：服务端/客户端/前端/后端/全栈/游戏/iOS/Android开发
  - 产品职位：产品经理、产品助理、产品
  - 设计职位：UI/UX/交互/视觉/平面设计师
  - 运营职位：用户/内容/活动/社群/数据运营、运营经理
  - 数据/AI职位：数据分析师、科学家、机器学习、AI、大模型、NLP、深度学习
  - 其他：专家、顾问、助理、实习、兼职
- **备用方案**：未匹配时截取前10个字符
- **代码位置**：`app.js` 第20-130行 `extractJobTitle()` 函数

### 数据抓取限制扩展（2026-03-24 15:21）
- **国内上限**: 2000条
- **海外上限**: 2000条  
- **V2EX**: 200条
- **总计上限**: 5000条
- **修改文件**: `scrape.sh`

### 新增数据源（2026-03-24 15:21）
- **Remotive**: 海外远程工作API (`https://remotive.com/api/remote-jobs`)
- 已添加到抓取脚本，与 Remote OK 数据合并

### Skill 维护计划
- **Skill 路径**: `~/.workbuddy/skills/junes-remote-jobs/`
- 包含完整的项目说明、数据源列表、添加新数据源步骤指南
- 待添加数据源：We Work Remotely、Jobspresso、RemoteCN 等

### 🔧 远程中文网申请链接抓取（已修复，2026-03-24 16:12）
- **问题**：远程中文网的岗位详情页显示"查看原帖投递"，而不是"申请职位"
- **根本原因**：远程中文网的 `applyUrl` 和 `sourceUrl` 相同（都是详情页链接），但详情页中有一个"申请职位"按钮指向第三方招聘网站（如 zhaopin.com）
- **修复方案**：
  - 在 `scrape.sh` 中预下载远程中文网详情页（前20个）
  - 新增 `parse_remotechina_detail()` 函数提取详情页中的"申请职位"按钮链接
  - 将提取的链接作为 `applyUrl` 存储
- **修复后验证**：`applyUrl` 现在指向 zhaopin.com 等招聘网站，详情页按钮显示"申请职位 →"
- **代码位置**：`scrape.sh` 第93-120行（预下载）、第404-450行（解析逻辑）

### 🔧 海外岗位显示"0" Bug（已修复，2026-03-24 15:52）
- **问题**：页面显示"0 海外岗位"，海外远程岗列表无数据
- **根本原因**：`jobs-global.js` 中 `description` 字段包含未转义的换行符和引号，导致 JavaScript 解析失败，`JOBS_GLOBAL` 变量无法定义
- **修复方案**：
  - 改进 `scrape.sh` 中的 `escape_str()` 函数，增加对换行符(\n)、回车符(\r)、制表符(\t)、双引号(")的转义
  - 新增 `escape_list()` 函数处理数组字段
- **修复后验证**：生成的 `jobs-global.js` 语法正确，海外岗位正常显示（316条）
- **代码位置**：`scrape.sh` 第740-760行

### ⚠️ 教训
- 每次脚本生成数据文件后，务必用 `node -c` 检查语法
- HTML 内容字段（description、requirements、benefits）必须完整转义
