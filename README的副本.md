# Junes远程 · remotework.asia

> 专注中国远程工作岗位收集平台，聚合国内外优质远程职位，帮你找到在家工作的机会。

🌐 **线上地址**: [remotework.asia](https://remotework.asia)

---

## 项目简介

Junes远程是一个面向中国求职者的远程工作信息聚合平台，收集来自网络的真实远程岗位，涵盖国内和海外机会，同时提供远程公司列表、全球招聘网站导航以及远程工作者社群。

## 页面结构

| 页面 | 文件 | 说明 |
|------|------|------|
| 首页 | `index.html` | 岗位列表，支持关键词搜索和国内/海外切换 |
| 远程公司 | `companies.html` | 100+ Fully Remote 公司列表 |
| 网站聚合 | `aggregate.html` | 全球优质远程工作招聘网站导航 |
| 加入社群 | `community.html` | 微信社群入口，含内推、组队接单等福利 |
| 发布岗位 | `submit.html` | 招聘方岗位提交表单 |
| 公众号 | `gongzhonghao.html` | 微信公众号二维码展示 |
| 小红书 | `xiaohongshu.html` | 小红书账号二维码展示 |

## 技术栈

- **纯静态站点**：HTML + CSS + JavaScript，无需构建工具
- **数据驱动**：岗位数据通过 JS 文件维护（`jobs-cn.js`、`jobs-global.js`、`jobs-mainlist.js`）
- **公司数据**：`companies-data.js`
- **样式**：`style.css` 统一管理，使用 CSS 变量和 Flexbox/Grid 布局
- **字体**：Google Fonts - Inter
- **部署**：Vercel（`vercel.json` 配置）
- **广告**：Google AdSense（Publisher ID: `ca-pub-8403146902177842`）

## 文件说明

```
├── index.html          # 首页 - 岗位列表
├── companies.html      # 远程公司列表
├── aggregate.html      # 远程工作网站聚合导航
├── community.html      # 加入社群页面
├── submit.html         # 发布岗位表单
├── gongzhonghao.html   # 公众号二维码页
├── xiaohongshu.html    # 小红书二维码页
├── style.css           # 全站样式
├── app.js              # 主逻辑：搜索、筛选、弹窗等
├── jobs-mainlist.js    # 岗位数据入口
├── jobs-cn.js          # 国内远程岗位数据
├── jobs-global.js      # 海外远程岗位数据
├── companies-data.js   # 远程公司数据
├── ads.txt             # Google AdSense 授权文件
├── vercel.json         # Vercel 部署配置
├── wechat-qr.png       # 微信小助手二维码
├── con_code.png        # 公众号二维码
└── xhs_code.png        # 小红书二维码
```

## 岗位数据更新

岗位数据存储在 JS 文件中，更新方式：

1. 打开 `jobs-cn.js`（国内）或 `jobs-global.js`（海外）
2. 按照已有格式添加新岗位对象
3. 提交代码后 Vercel 自动部署

## 本地开发

无需安装依赖，直接用浏览器打开 HTML 文件即可，或使用本地静态服务器：

```bash
# 使用 Python
python3 -m http.server 8080

# 使用 Node.js
npx serve .
```

访问 `http://localhost:8080` 查看效果。

## 部署

项目通过 **Vercel + GitHub** 自动部署：

1. 推送代码到 `master` 分支
2. Vercel 检测到变更后自动触发重新部署
3. 约 1 分钟后 [remotework.asia](https://remotework.asia) 更新生效

DNS 由 **Cloudflare** 管理，已配置 Vercel 自定义域名解析。

## 社群

- **微信**：Junes2023（扫码添加后回复「加入社群」）
- **公众号**：扫描 `con_code.png` 关注
- **小红书**：扫描 `xhs_code.png` 关注

社群福利：内推通道直达HR、新岗位优先获取、Upwork/Fiverr 外包项目组队接单。

---

© 2026 Junes远程 · 数据来自公开渠道整理
