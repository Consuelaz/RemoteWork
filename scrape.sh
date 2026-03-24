#!/bin/bash
# 远程工作数据抓取脚本 (纯 curl + Python)
# 设置定时任务: crontab -e
# 0 8 * * * /Users/qisoong/WorkBuddy/20260317141747/scrape.sh

PROJECT_DIR="/Users/qisoong/WorkBuddy/20260317141747"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$PROJECT_DIR/scrape.log"

echo "========================================" >> $LOG_FILE
echo "开始抓取: $DATE" >> $LOG_FILE

cd $PROJECT_DIR

# 代理配置 (仅用于 V2EX)
PROXY="-x http://127.0.0.1:7897"

# ========================================
# 1. 抓取 Remote OK (JSON API) - 直接连接
# ========================================
echo "正在抓取 Remote OK..." >> $LOG_FILE
curl -s -L -A "Mozilla/5.0" "https://remoteok.com/remote-jobs.json" -o /tmp/remoteok.json

if [ -s /tmp/remoteok.json ]; then
    echo "Remote OK 下载完成" >> $LOG_FILE
else
    echo "Remote OK 下载失败" >> $LOG_FILE
fi

# ========================================
# 2. 抓取远程中文网 - 直接连接
# ========================================
echo "正在抓取远程中文网..." >> $LOG_FILE
curl -s -L "https://remote-china.com/jobs" -o /tmp/remote-china.html

if [ -s /tmp/remote-china.html ]; then
    echo "远程中文网 下载完成" >> $LOG_FILE
else
    echo "远程中文网 下载失败" >> $LOG_FILE
fi

# ========================================
# 3. 抓取 V2EX 远程工作板块 (需要代理)
# ========================================
echo "正在抓取 V2EX..." >> $LOG_FILE
curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" $PROXY "https://www.v2ex.com/go/remote" -o /tmp/v2ex.html

if [ -s /tmp/v2ex.html ]; then
    echo "V2EX 下载完成" >> $LOG_FILE
else
    echo "V2EX 下载失败" >> $LOG_FILE
fi

# ========================================
# 3. 用 Python 处理数据
# ========================================
python3 << 'EOF'
import json
import os
from datetime import datetime

DATE = datetime.now().strftime('%Y-%m-%d')

# ========== 处理 Remote OK ==========
remoteok_jobs = []
try:
    with open('/tmp/remoteok.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 跳过第一个元素(元数据)，取50条
    for item in data[1:51]:
        job = {
            "id": f"global-remoteok-{hash(item.get('position', '')) % 1000000}",
            "title": item.get("position", ""),
            "company": item.get("company", "Remote OK"),
            "logo": "🌍",
            "category": "软件工程",
            "tags": item.get("tags", [])[:5],
            "salary": item.get("salary", "面议"),
            "location": "全球远程",
            "date": DATE,
            "isNew": True,
            "isFeatured": False,
            "canRefer": False,
            "source": "https://remoteok.com/remote-dev-jobs",
            "sourceUrl": "https://remoteok.com" + item.get("url", ""),
            "currency": "USD",
            "companyCountry": "海外",
            "description": f"{item.get('company', '')} 招聘 {item.get('position', '')}",
            "requirements": [],
            "benefits": []
        }
        if job["title"]:
            remoteok_jobs.append(job)
    print(f"Remote OK: {len(remoteok_jobs)} jobs")
except Exception as e:
    print(f"Remote OK 解析失败: {e}")

# ========== 处理远程中文网 ==========
from bs4 import BeautifulSoup

remotechina_jobs = []
try:
    with open('/tmp/remote-china.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('a.job-item')[:30]
    
    for i, item in enumerate(items):
        title_elem = item.select_one('.job-title')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        company_elem = item.select_one('.job-team-name')
        company = company_elem.get_text(strip=True) if company_elem else "远程中文网"
        
        salary_elem = item.select_one('.job-description')
        salary = salary_elem.get_text(strip=True)[:50] if salary_elem else "面议"
        
        href = item.get('href', '')
        link = "https://remote-china.com" + href if href else ""
        
        if title and link:
            job = {
                "id": f"cn-remotechina-{i}{hash(title) % 10000}",
                "title": title,
                "company": company,
                "logo": "🌐",
                "category": "远程工作",
                "tags": ["远程"],
                "salary": salary,
                "location": "全国远程",
                "date": DATE,
                "isNew": True,
                "isFeatured": False,
                "canRefer": False,
                "source": "https://remote-china.com/jobs",
                "sourceUrl": link,
                "applyUrl": link,
                "description": "来自远程中文网的远程工作机会",
                "requirements": [],
                "benefits": []
            }
            remotechina_jobs.append(job)
    print(f"远程中文网: {len(remotechina_jobs)} jobs")
except Exception as e:
    print(f"远程中文网 解析失败: {e}")

# ========== 处理 V2EX ==========
v2ex_jobs = []
try:
    with open('/tmp/v2ex.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.cell')[:30]
    
    for i, item in enumerate(items):
        title_elem = item.select_one('span.item_title a') or item.select_one('a.topic-link')
        if not title_elem:
            continue
        
        title = title_elem.get_text(strip=True)
        href = title_elem.get('href', '')
        link = "https://www.v2ex.com" + href if href.startswith('/') else href
        
        if title and link:
            # 尝试从标题提取公司
            import re as re2
            company_match = re2.search(r'【(.+?)】', title)
            company = company_match.group(1) if company_match else "（V2EX用户招聘）"
            
            job = {
                "id": f"cn-v2ex-{i}{hash(title) % 10000}",
                "title": title,
                "company": company,
                "logo": "💻",
                "category": "远程工作",
                "tags": ["远程", "V2EX"],
                "salary": "面议",
                "location": "全国远程",
                "date": DATE,
                "isNew": True,
                "isFeatured": False,
                "canRefer": True,  # V2EX 可内推
                "source": "https://www.v2ex.com/go/remote",
                "sourceUrl": link,
                "description": "来自V2EX远程工作社区的招聘帖子",
                "requirements": [],
                "benefits": []
            }
            v2ex_jobs.append(job)
    print(f"V2EX: {len(v2ex_jobs)} jobs")
except Exception as e:
    print(f"V2EX 解析失败: {e}")

# ========== 处理电鸭 ==========
dianyu_jobs = []
try:
    with open('/tmp/dianyu.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    # 电鸭可能有多种选择器
    items = soup.select('div.post-item') or soup.select('li.topic-item') or soup.select('div.topic-item')
    items = items[:30] if items else []
    
    for i, item in enumerate(items):
        title_elem = item.select_one('h3 a, h4 a, .title a, a.title')
        if not title_elem:
            continue
        
        title = title_elem.get_text(strip=True)
        href = title_elem.get('href', '')
        link = "https://eleduck.com" + href if href.startswith('/') else href
        
        if title and link:
            job = {
                "id": f"cn-dianyu-{i}{hash(title) % 10000}",
                "title": title,
                "company": "（电鸭用户招聘）",
                "logo": "🦆",
                "category": "远程工作",
                "tags": ["远程", "电鸭"],
                "salary": "面议",
                "location": "全国远程",
                "date": DATE,
                "isNew": True,
                "isFeatured": False,
                "canRefer": True,  # 电鸭可内推
                "source": "https://eleduck.com/category/4",
                "sourceUrl": link,
                "description": "来自电鸭社区的远程工作机会",
                "requirements": [],
                "benefits": []
            }
            dianyu_jobs.append(job)
    print(f"电鸭: {len(dianyu_jobs)} jobs")
except Exception as e:
    print(f"电鸭 解析失败: {e}")

# ========== 读取现有数据 ==========
def load_js_array(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        match = re.search(r'const JOBS_\w+ = \[([\s\S]*?)\];', content)
        if not match:
            return []
        array_str = match.group(1).strip()
        if not array_str:
            return []
        # 简单解析
        jobs = []
        obj_pattern = r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        for obj_str_list in re.findall(obj_pattern, array_str):
            obj_str = '{' + obj_str_list + '}'
            job = {}
            field_pattern = r"(\w+):\s*(\[.*?\]|'[^']*'|true|false|\d+)"
            for m in re.finditer(field_pattern, obj_str):
                key = m.group(1)
                val = m.group(2)
                if val == 'true':
                    job[key] = True
                elif val == 'false':
                    job[key] = False
                elif val.startswith('['):
                    job[key] = []
                elif val.startswith("'"):
                    job[key] = val[1:-1]
                else:
                    job[key] = val
            if job.get('id'):
                jobs.append(job)
        return jobs
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return []

existing_cn = load_js_array('jobs-cn.js')
existing_global = load_js_array('jobs-global.js')

print(f"现有数据: CN={len(existing_cn)}, Global={len(existing_global)}")

# ========== 合并数据 ==========
def merge_jobs(old_jobs, new_jobs):
    existing_ids = set(j['id'] for j in old_jobs)
    unique_new = [j for j in new_jobs if j['id'] not in existing_ids]
    # 保留旧的，新的放前面
    merged = unique_new + old_jobs
    # 限制数量
    return merged[:200]

merged_cn = merge_jobs(existing_cn, remotechina_jobs + v2ex_jobs + dianyu_jobs)
merged_global = merge_jobs(existing_global, remoteok_jobs)

print(f"合并后: CN={len(merged_cn)}, Global={len(merged_global)}")

# ========== 写入 JS 文件 ==========
def escape_str(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

def jobs_to_js(jobs, var_name):
    lines = [f"const {var_name} = ["]
    for job in jobs:
        lines.append("  {")
        for i, (key, val) in enumerate(job.items()):
            if isinstance(val, bool):
                lines.append(f"    {key}: {'true' if val else 'false'},")
            elif isinstance(val, list):
                tags = ", ".join([f"'{escape_str(t)}'" for t in val])
                lines.append(f"    {key}: [{tags}],")
            else:
                lines.append(f"    {key}: '{escape_str(val)}',")
        lines.append("  },")
    lines.append("];")
    return "\n".join(lines)

# 写入 CN
header_cn = f"""// ============================================================
// 国内远程工作岗位数据
// 数据来源：远程中文网等
// 最后更新：{DATE}
// ============================================================

"""
with open('jobs-cn.js', 'w', encoding='utf-8') as f:
    f.write(header_cn + jobs_to_js(merged_cn, "JOBS_CN"))

# 写入 Global  
header_global = f"""// ============================================================
// 国外/海外远程工作岗位数据
// 数据来源：Remote OK 等
// 最后更新：{DATE}
// ============================================================

"""
with open('jobs-global.js', 'w', encoding='utf-8') as f:
    f.write(header_global + jobs_to_js(merged_global, "JOBS_GLOBAL"))

print(f"✅ 数据更新完成!")
EOF

echo "数据更新完成: $DATE" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 清理临时文件
rm -f /tmp/remoteok.json /tmp/remote-china.html
