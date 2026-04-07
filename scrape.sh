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
# 1.1 抓取 Remotive (JSON API) - 海外远程工作
# ========================================
echo "正在抓取 Remotive..." >> $LOG_FILE
curl -s -L -A "Mozilla/5.0" "https://remotive.com/api/remote-jobs" -o /tmp/remotive.json

if [ -s /tmp/remotive.json ]; then
    echo "Remotive 下载完成" >> $LOG_FILE
else
    echo "Remotive 下载失败" >> $LOG_FILE
fi

# ========================================
# 1.2 抓取远程岛 (JSON API) - 华人全球远程工作
# ========================================
echo "正在抓取远程岛..." >> $LOG_FILE
# 获取多页数据
for page in 1 2 3 4 5; do
    curl -s -L -A "Mozilla/5.0" "https://yuanchengdao.com/api/jobs?page=${page}&limit=30" -o /tmp/yuanchengdao_${page}.json
    sleep 1
done

if [ -s /tmp/yuanchengdao_1.json ]; then
    echo "远程岛 下载完成" >> $LOG_FILE
else
    echo "远程岛 下载失败" >> $LOG_FILE
fi

# ========================================
# 1.3 抓取 who-is-hiring (Rebase社区) - JSON API
# ========================================
echo "正在抓取 who-is-hiring (Rebase)..." >> $LOG_FILE
curl -s -L -A "Mozilla/5.0" "https://hire.rebase.network/jobs.normalized.json" -o /tmp/rebase_jobs.json

if [ -s /tmp/rebase_jobs.json ]; then
    echo "who-is-hiring 下载完成" >> $LOG_FILE
else
    echo "who-is-hiring 下载失败" >> $LOG_FILE
fi

# 预下载 Remote OK 详情页（前10个岗位）
echo "正在预下载Remote OK岗位详情..." >> $LOG_FILE
python3 << 'PYEOF'
import json
import os
import subprocess

if not os.path.exists('/tmp/remoteok.json'):
    print("Remote OK JSON不存在")
else:
    with open('/tmp/remoteok.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 下载前50个岗位的详情页（增加数量以获取更丰富的数据）
    for i, item in enumerate(data[1:51]):
        url = item.get("url", "")
        if url and not url.startswith("http"):
            url = "https://remoteok.com" + url
        if url:
            # 用hash作为文件名
            fname = f"/tmp/remoteok_detail_{i}.html"
            cmd = f'curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "{url}" -o "{fname}" --max-time 15'
            os.system(cmd)
            print(f"下载 {i}: {url[:50]}")

# 保存映射（使用idx作为key）
remoteok_url_map = {}
for i, item in enumerate(data[1:51]):
    url = item.get("url", "")
    if url and not url.startswith("http"):
        url = "https://remoteok.com" + url
    if url:
        remoteok_url_map[i] = url

import pickle
with open('/tmp/remoteok_url_map.pkl', 'wb') as f:
    pickle.dump(remoteok_url_map, f)
print(f"已保存 {len(remoteok_url_map)} 个Remote OK URL映射")
PYEOF

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

# 预下载远程中文网详情页（提取申请职位链接）
echo "正在预下载远程中文网岗位详情..." >> $LOG_FILE
python3 << 'PYEOF'
import os
import re

if not os.path.exists('/tmp/remote-china.html'):
    print("远程中文网列表页不存在")
else:
    from bs4 import BeautifulSoup
    with open('/tmp/remote-china.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('a.job-item')[:20]  # 只抓取前20个岗位的详情
    
    apply_url_map = {}
    for i, item in enumerate(items):
        href = item.get('href', '')
        if href:
            # 构建完整的详情页URL
            if href.startswith('/'):
                detail_url = "https://remote-china.com" + href
            else:
                detail_url = href
            
            # 下载详情页
            fname = f"/tmp/remotechina_detail_{i}.html"
            cmd = f'curl -s -L -A "Mozilla/5.0" "{detail_url}" -o "{fname}"'
            os.system(cmd)
            apply_url_map[i] = {'detail_url': detail_url, 'file': fname}
            print(f"下载 {i}: {detail_url}")
    
    # 保存映射
    import json
    with open('/tmp/remotechina_url_map.json', 'w') as f:
        json.dump(apply_url_map, f)
    print(f"已保存 {len(apply_url_map)} 个远程中文网详情页映射")
PYEOF

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

# 预下载前10个V2EX岗位详情页（详细信息）
echo "正在预下载V2EX岗位详情..." >> $LOG_FILE
python3 << 'PYEOF'
import os
import re

# 读取列表页
if not os.path.exists('/tmp/v2ex.html'):
    print("V2EX列表页不存在")
else:
    with open('/tmp/v2ex.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 提取前10个帖子链接
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.cell')[:200]
    
    # 使用列表索引确保文件编号连续，同时保存URL映射
    url_mapping = []
    for i, item in enumerate(items):
        title_elem = item.select_one('span.item_title a') or item.select_one('a.topic-link')
        if not title_elem:
            continue
        href = title_elem.get('href', '')
        if href.startswith('/t/'):
            link = "https://www.v2ex.com" + href
            # curl 详情页，使用连续索引编号
            idx = len(url_mapping)
            # 提取t/编号作为映射键
            url_key = re.search(r'(t/\d+)', href)
            if url_key:
                url_mapping.append((url_key.group(1), idx, link))
            cmd = f'curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" -x http://127.0.0.1:7897 "{link}" -o /tmp/v2ex_detail_{idx}.html'
            os.system(cmd)
            print(f"下载 {idx}: {href}")
    
    # 保存URL映射到文件供Python主逻辑使用
    with open('/tmp/v2ex_url_map.txt', 'w') as f:
        for url_key, idx, link in url_mapping:
            f.write(f"{url_key}|{idx}|{link}\n")
    print(f"已保存 {len(url_mapping)} 个URL映射")
PYEOF

# ========================================
# 3. 用 Python 处理数据
# ========================================
python3 << 'EOF'
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

DATE = datetime.now().strftime('%Y-%m-%d')

# ========== 自动推断分类 ==========
def guess_category_cn(title):
    title = title.lower()
    if any(k in title for k in ['前端', 'frontend', 'vue', 'react', 'css', 'html', 'javascript', 'js']):
        return '前端开发'
    if any(k in title for k in ['后端', 'backend', 'java', 'python', 'go', 'php', 'ruby', 'c++', 'c#', 'node', 'spring', 'django']):
        return '后端开发'
    if any(k in title for k in ['全栈', 'fullstack', 'full stack', 'full-stack']):
        return '全栈开发'
    if any(k in title for k in ['ai', '算法', '机器学习', '深度学习', '大模型', 'llm', 'nlp', '人工智能', 'ml']):
        return 'AI/算法'
    if any(k in title for k in ['区块链', 'blockchain', 'web3', '智能合约', 'solidity', 'defi', 'nft', 'crypto']):
        return '区块链'
    if any(k in title for k in ['运营', '推广', '增长', '社群']):
        return '运营'
    if any(k in title for k in ['产品', 'product', 'pm ', ' pm', '产品经理']):
        return '产品经理'
    if any(k in title for k in ['设计', 'design', 'ui', 'ux', '交互', '视觉']):
        return 'UI/UX设计'
    if any(k in title for k in ['市场', 'marketing', '品牌', '广告', 'seo', 'sem']):
        return '市场营销'
    if any(k in title for k in ['数据', 'data', '分析', 'bi ', 'sql', 'etl', '爬虫']):
        return '数据分析'
    if any(k in title for k in ['移动', 'android', 'ios', 'flutter', 'swift', 'kotlin', '小程序', 'rn', 'react native']):
        return '移动开发'
    if any(k in title for k in ['测试', 'qa', 'test', '质量']):
        return '测试/QA'
    if any(k in title for k in ['运维', 'devops', 'k8s', 'docker', 'linux', 'aws', '云', 'kubernetes']):
        return '运维/DevOps'
    if any(k in title for k in ['客服', '销售', '咨询', '法律', '财务', '会计', '翻译', '写作', '文案']):
        return '其他职位'
    return '远程工作'

def guess_category_global(title):
    title = title.lower()
    if any(k in title for k in ['frontend', 'front-end', 'vue', 'react', 'css', 'html', 'javascript']):
        return '前端开发'
    if any(k in title for k in ['backend', 'back-end', 'java', 'python', 'go', 'php', 'ruby', 'node', 'spring']):
        return '后端开发'
    if any(k in title for k in ['fullstack', 'full stack', 'full-stack']):
        return '全栈开发'
    if any(k in title for k in ['ai', 'ml', 'machine learning', 'data science', 'nlp', 'llm']):
        return 'AI/算法'
    if any(k in title for k in ['data', 'analyst', 'analytics', 'bi ', 'sql']):
        return '数据分析'
    if any(k in title for k in ['product', 'pm ', ' pm']):
        return '产品经理'
    if any(k in title for k in ['design', 'ui', 'ux']):
        return 'UI/UX设计'
    if any(k in title for k in ['marketing', 'seo', 'sem', 'brand', 'growth']):
        return '市场营销'
    if any(k in title for k in ['devops', 'infra', 'cloud', 'aws', 'k8s', 'docker', 'linux']):
        return '运维/DevOps'
    return '软件工程'

# ========== 解析 Remote OK 详情页 ==========
def parse_remoteok_detail(file_path):
    """解析Remote OK详情页，提取详细信息"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        # 尝试多种编码
        html = ''
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    html = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'description': '',
            'requirements': [],
            'benefits': [],
            'company_info': ''
        }
        
        # 提取职位描述 - Remote OK 使用 div.description
        desc_elem = soup.select_one('div.description')
        if desc_elem:
            # 获取完整文本
            full_desc = desc_elem.get_text('\n', strip=True)
            
            # 清理噪音：使用正则表达式更精确地匹配
            import re
            noise_patterns = [
                r'^Apply now$',
                r'^Share this job:$',
                r'^Get a$',
                r'^rok\.co$',
                r'^short link$',
                r'^👍$',
                r'^👎$',
                r'^❤️$',
                r'^📍$',
                r'^💼$',
                r'^Report this job$',
                r'^Save$',
                r'^Hide$',
            ]
            
            lines = full_desc.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                # 跳过匹配噪音模式的行
                if any(re.match(pattern, line) for pattern in noise_patterns):
                    continue
                # 跳过太短的行
                if len(line) < 2:
                    continue
                cleaned_lines.append(line)
            
            # 找到实际内容开始的位置
            content_start = 0
            for i, line in enumerate(cleaned_lines):
                # 找到包含 "is hiring" 或职位标题后的内容
                if 'is hiring' in line.lower():
                    content_start = i + 1
                    break
                # 或者找到 Remote 开头的行（通常是职位标题）
                if line.startswith('Remote ') and i > 0:
                    content_start = i + 1
                    break
            
            # 提取内容
            if content_start < len(cleaned_lines):
                # 从 content_start 开始的所有内容作为描述
                desc_text = '\n'.join(cleaned_lines[content_start:])
                # 清理多余的空白和制表符
                desc_text = re.sub(r'\t+', ' ', desc_text)
                desc_text = re.sub(r'\n\s*\n', '\n\n', desc_text)
                result['description'] = desc_text.strip()[:1500]
                
                # 前几句作为公司介绍
                if content_start < len(cleaned_lines):
                    first_para = cleaned_lines[content_start]
                    if len(first_para) > 20:
                        result['company_info'] = first_para[:400]
            else:
                # 如果找不到标记，使用全部内容（但跳过前2行，通常是公司名+职位名）
                if len(cleaned_lines) > 2:
                    result['description'] = '\n'.join(cleaned_lines[2:])[:1500]
                else:
                    result['description'] = '\n'.join(cleaned_lines)[:1500]
        
        # 从描述中提取要求（寻找关键词后的内容）
        if result['description']:
            desc_lower = result['description'].lower()
            req_keywords = ['requirements:', 'what you need:', 'qualifications:', 'you have:', 
                           'skills required:', 'requirements', 'qualifications', 'what you’ll bring']
            for keyword in req_keywords:
                if keyword in desc_lower:
                    idx = desc_lower.find(keyword)
                    if idx >= 0:
                        # 找到这个部分的开始和结束（到下一个主要标题）
                        req_section = result['description'][idx:idx+1000]
                        # 提取列表项
                        req_lines = []
                        for l in req_section.split('\n'):
                            l = l.strip()
                            if l and len(l) > 10:
                                # 移除列表标记
                                if l.startswith(('- ', '• ', '* ')):
                                    l = l[2:]
                                elif l[0].isdigit() and l[1:3] in ('. ', ') '):
                                    l = l[3:]
                                if len(l) > 10:
                                    req_lines.append(l)
                        if len(req_lines) > 1:
                            result['requirements'] = req_lines[:8]
                        break
        
        # 从描述中提取福利
        if result['description']:
            desc_lower = result['description'].lower()
            benefit_keywords = ['benefits:', 'perks:', 'we offer:', 'compensation:', 
                               'benefits', 'perks', 'what we offer']
            for keyword in benefit_keywords:
                if keyword in desc_lower:
                    idx = desc_lower.find(keyword)
                    if idx >= 0:
                        benefit_section = result['description'][idx:idx+800]
                        benefit_lines = []
                        for l in benefit_section.split('\n'):
                            l = l.strip()
                            if l and len(l) > 5:
                                if l.startswith(('- ', '• ', '* ')):
                                    l = l[2:]
                                elif l[0].isdigit() and l[1:3] in ('. ', ') '):
                                    l = l[3:]
                                if len(l) > 5:
                                    benefit_lines.append(l)
                        if len(benefit_lines) > 1:
                            result['benefits'] = benefit_lines[:6]
                        break
        
        # 如果没有提取到描述，使用标签生成
        if not result['description']:
            tags = soup.select('div.tags a') or soup.select('.tag')
            if tags:
                tag_texts = [t.get_text(strip=True) for t in tags[:8]]
                result['description'] = f"技能标签: {', '.join(tag_texts)}"
        
        return result
    except Exception as e:
        print(f"解析Remote OK详情页失败: {e}")
        return {}

# 加载 Remote OK URL 映射
remoteok_detail_map = {}
try:
    import pickle
    if os.path.exists('/tmp/remoteok_url_map.pkl'):
        with open('/tmp/remoteok_url_map.pkl', 'rb') as f:
            remoteok_detail_map = pickle.load(f)
except:
    pass

# ========== 处理 Remote OK ==========
remoteok_jobs = []
try:
    with open('/tmp/remoteok.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 跳过第一个元素(元数据)，取2000条（海外）
    for idx, item in enumerate(data[1:2001]):
        title = item.get("position", "")
        
        # 获取详情页数据
        detail_info = {}
        if idx in remoteok_detail_map:
            detail_info = parse_remoteok_detail(f'/tmp/remoteok_detail_{idx}.html')
        
        job = {
            "id": f"global-remoteok-{hash(item.get('position', '')) % 1000000}",
            "title": title,
            "company": item.get("company", "Remote OK"),
            "logo": "🌍",
            "category": guess_category_global(title),
            "tags": item.get("tags", [])[:5],
            "salary": item.get("salary", "面议"),
            "location": "全球远程",
            "date": DATE,
            "isNew": True,
            "isFeatured": False,
            "canRefer": False,
            "source": "https://remoteok.com/remote-dev-jobs",
            "sourceUrl": item.get("url", "") if item.get("url", "").startswith("http") else "https://remoteok.com" + item.get("url", ""),
            "currency": "USD",
            "companyCountry": "海外",
            "description": (detail_info.get('description') or f"{item.get('company', '')} 招聘 {item.get('position', '')}")[:500],
            "requirements": detail_info.get('requirements', []),
            "benefits": detail_info.get('benefits', []),
            "company_info": detail_info.get('company_info', '')
        }
        if job["title"]:
            remoteok_jobs.append(job)
    print(f"Remote OK: {len(remoteok_jobs)} jobs")
except Exception as e:
    print(f"Remote OK 解析失败: {e}")

# ========== 处理 Remotive ==========
remotive_jobs = []
try:
    with open('/tmp/remotive.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs_list = data.get('jobs', [])[:2000]
    
    for item in jobs_list:
        title = item.get("title", "")
        company = item.get("company_name", "Remotive")
        
        job = {
            "id": f"global-remotive-{item.get('id', '')}",
            "title": title,
            "company": company,
            "logo": "🌍",
            "category": guess_category_global(title),
            "tags": item.get("tags", [])[:5],
            "salary": item.get("salary", "面议"),
            "location": item.get("candidate_required_location", "全球远程"),
            "date": item.get("publication_date", DATE)[:10],
            "isNew": True,
            "isFeatured": False,
            "canRefer": False,
            "source": "https://remotive.com/remote-jobs",
            "sourceUrl": item.get("url", ""),
            "currency": "USD",
            "companyCountry": "海外",
            "description": item.get("description", "")[:500] if item.get("description") else f"{company} 招聘 {title}",
            "requirements": [],
            "benefits": [item.get("job_type", "")] if item.get("job_type") else []
        }
        if job["title"]:
            remotive_jobs.append(job)
    print(f"Remotive: {len(remotive_jobs)} jobs")
except Exception as e:
    print(f"Remotive 解析失败: {e}")

# ========== 处理远程岛 ==========
yuanchengdao_jobs = []
try:
    import glob
    all_jobs = []
    for fname in glob.glob('/tmp/yuanchengdao_*.json'):
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                data = json.load(f)
                jobs = data.get('jobs', [])
                all_jobs.extend(jobs)
        except Exception as e:
            print(f"解析 {fname} 失败: {e}")
    
    for item in all_jobs[:2000]:
        title = item.get("title", "")
        company = item.get("company_name", "远程岛")
        
        # 处理薪资
        salary_lower = item.get("salary_lower", 0)
        salary_upper = item.get("salary_upper", 0)
        salary_currency = item.get("salary_currency", "CNY")
        salary_pay_cycle = item.get("salary_pay_cycle", "year")
        
        if salary_lower > 0 and salary_upper > 0:
            if salary_pay_cycle == "year":
                salary = f"{salary_lower/10000:.0f}万-{salary_upper/10000:.0f}万/年"
            else:
                salary = f"{salary_lower}-{salary_upper}/月"
        else:
            salary = "面议"
        
        # 处理地点
        location_parts = []
        country = item.get("country_name_cn", "")
        location = item.get("location_name_cn", "")
        if country:
            location_parts.append(country)
        if location and location != country:
            location_parts.append(location)
        location_str = " | ".join(location_parts) if location_parts else "全球远程"
        
        # 解析发布时间
        posted_at = item.get("posted_at", "")
        if posted_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
            except:
                date_str = DATE
        else:
            date_str = DATE
        
        # 解析申请链接
        apply_url = ""
        apply_options = item.get("apply_options", "")
        if apply_options:
            try:
                import ast
                options = ast.literal_eval(apply_options)
                if options and len(options) > 0:
                    apply_url = options[0].get("link", "")
            except:
                pass
        
        # 解析职位亮点
        requirements = []
        benefits = []
        try:
            job_highlights = item.get("job_highlights", "")
            if job_highlights:
                import ast
                highlights = ast.literal_eval(job_highlights)
                for h in highlights:
                    if h.get("title") == "资格":
                        requirements = h.get("items", [])[:8]
                    elif h.get("title") == "福利":
                        benefits = h.get("items", [])[:5]
        except:
            pass
        
        job = {
            "id": f"global-yuanchengdao-{item.get('id', '')}",
            "title": title,
            "company": company,
            "logo": item.get("company_thumbnail", "🌏"),
            "category": guess_category_global(title),
            "tags": ["远程", "华人友好"],
            "salary": salary,
            "location": location_str,
            "date": date_str,
            "isNew": True,
            "isFeatured": False,
            "canRefer": False,
            "source": "https://yuanchengdao.com",
            "sourceUrl": f"https://yuanchengdao.com/job/{item.get('slug', '')}",
            "applyUrl": apply_url if apply_url else f"https://yuanchengdao.com/job/{item.get('slug', '')}",
            "currency": salary_currency,
            "companyCountry": item.get("country_name_cn", "海外"),
            "description": item.get("description", "")[:500] if item.get("description") else f"{company} 招聘 {title}",
            "requirements": requirements,
            "benefits": benefits
        }
        if job["title"]:
            yuanchengdao_jobs.append(job)
    print(f"远程岛: {len(yuanchengdao_jobs)} jobs")
except Exception as e:
    print(f"远程岛 解析失败: {e}")

# ========== 处理 who-is-hiring (Rebase社区) ==========
# 注意：联系方式只写入 money.xlsx，不写入 jobs-cn.js
rebase_jobs = []
rebase_jobs_for_excel = []  # 用于写入 money.xlsx 的完整数据（含联系方式）
try:
    with open('/tmp/rebase_jobs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs_list = data.get('jobs', [])[:500]  # 限制500条
    
    for item in jobs_list:
        title = item.get("title") or ""
        company = item.get("company") or ""
        
        # 跳过非远程岗位（work_mode 可能为 None，需做兜底）
        remote = item.get("remote", False)
        work_mode = item.get("work_mode") or ""
        if not remote and "远程" not in work_mode and "remote" not in work_mode.lower():
            continue
        
        # 处理薪资（salary 可能为 None）
        salary = item.get("salary") or "面议"
        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")
        
        # 处理地点（location 可能为 None）
        location = item.get("location") or "远程"
        
        # 解析发布时间
        created_at = item.get("created_at", "")
        date_str = DATE
        if created_at:
            try:
                from datetime import datetime
                # 尝试解析时间戳或日期字符串
                if isinstance(created_at, (int, float)):
                    dt = datetime.fromtimestamp(created_at)
                    date_str = dt.strftime('%Y-%m-%d')
                else:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d')
            except:
                date_str = DATE
        
        # 安全处理可能为 None 的列表字段
        raw_resp = item.get("responsibilities")
        raw_reqs = item.get("requirements")
        raw_benefits = item.get("benefits")
        raw_contacts = item.get("contact_channels")
        # responsibilities/benefits 期望是列表
        resp_list = raw_resp if isinstance(raw_resp, list) else ([] if raw_resp is None else [str(raw_resp)])
        benefits_list = raw_benefits if isinstance(raw_benefits, list) else ([] if raw_benefits is None else [str(raw_benefits)])
        # requirements：列表或字符串均支持
        if isinstance(raw_reqs, list):
            reqs_list = raw_reqs
        elif raw_reqs is None:
            reqs_list = []
        else:
            reqs_list = [str(raw_reqs)]
        contact_list = raw_contacts if isinstance(raw_contacts, list) else ([] if raw_contacts is None else [str(raw_contacts)])

        # 构建职位对象（用于网站展示，不含联系方式）
        desc_text = item.get("description") or ""
        job = {
            "id": f"cn-rebase-{item.get('id', '')}",
            "title": title,
            "company": company,
            "logo": "🌐",
            "category": guess_category_cn(title),
            "tags": ["远程", "Rebase"],
            "salary": salary,
            "location": location,
            "date": date_str,
            "isNew": True,
            "isFeatured": False,
            "canRefer": False,
            "source": "https://hire.rebase.network",
            "sourceUrl": item.get("url") or "",
            "applyUrl": item.get("url") or "",
            "description": desc_text[:300] if desc_text else f"{company} 招聘 {title}",
            "responsibilities": resp_list,
            "requirements": reqs_list,
            "benefits": benefits_list
        }
        
        # 用于 Excel 的数据（包含联系方式）
        job_for_excel = {
            **job,
            "contact_channels": contact_list,
            "original_data": item  # 保存原始数据以便提取更多信息
        }
        
        if job["title"]:
            rebase_jobs.append(job)
            rebase_jobs_for_excel.append(job_for_excel)
    
    print(f"who-is-hiring: {len(rebase_jobs)} jobs (含联系方式的 {len(rebase_jobs_for_excel)} 条)")
except Exception as e:
    print(f"who-is-hiring 解析失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 处理远程中文网 ==========
from bs4 import BeautifulSoup

# 加载远程中文网详情页映射
remotechina_detail_map = {}
try:
    import json
    if os.path.exists('/tmp/remotechina_url_map.json'):
        with open('/tmp/remotechina_url_map.json', 'r') as f:
            remotechina_detail_map = json.load(f)
except Exception as e:
    print(f"加载远程中文网详情页映射失败: {e}")

def parse_remotechina_detail(file_path):
    """解析远程中文网详情页，提取申请职位链接、岗位描述、职责、要求等"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        # ===== 申请职位链接 =====
        apply_link = ''
        for sel in ['a.btn-primary', 'a[href*="zhaopin"]', 'a[href*="zhipin"]',
                    'a[href*="lagou"]', 'a[href*="eleduck"]', 'a[href*="liepin"]']:
            btn = soup.select_one(sel)
            if btn:
                apply_link = btn.get('href', '')
                break
        if apply_link:
            result['applyUrl'] = apply_link
        
        # ===== 从 .markdown-content 提取岗位描述 =====
        mc = soup.select_one('.markdown-content')
        if mc:
            lines = [l.strip() for l in mc.get_text('\n').split('\n') if l.strip()]
            
            responsibilities = []
            requirements = []
            current_section = None
            desc_lines = []
            
            RESP_KEYWORDS = ['岗位职责', '职位职责', '工作职责', '工作内容', '主要职责']
            REQ_KEYWORDS  = ['技能要求', '任职要求', '岗位要求', '职位要求', '基本要求']
            
            for line in lines:
                if any(kw in line for kw in RESP_KEYWORDS):
                    current_section = 'resp'
                    continue
                elif any(kw in line for kw in REQ_KEYWORDS):
                    current_section = 'req'
                    continue
                elif any(kw in line for kw in ['薪资待遇', '福利待遇', '工作时间', '行业和产品', '岗位名称']):
                    current_section = None
                    continue
                
                if current_section == 'resp' and len(line) > 5:
                    responsibilities.append(line)
                elif current_section == 'req' and len(line) > 5:
                    requirements.append(line)
                else:
                    desc_lines.append(line)
            
            if responsibilities:
                result['responsibilities'] = responsibilities[:20]
            if requirements:
                result['requirements'] = requirements[:15]
            
            # description 用前5行精华内容（跳过"行业和产品"这类 AI 生成的标题行）
            skip_prefixes = ['行业和产品', '岗位名称', '推测常规名称', '薪资待遇', '福利待遇', '工作时间']
            clean_desc = [l for l in desc_lines if not any(l.startswith(p) for p in skip_prefixes)]
            if clean_desc:
                result['description'] = ' | '.join(clean_desc[:5])
        
        return result
    except Exception as e:
        print(f"解析远程中文网详情页失败: {e}")
        return {}

remotechina_jobs = []
try:
    with open('/tmp/remote-china.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('a.job-item')[:2000]
    
    for i, item in enumerate(items):
        title_elem = item.select_one('.job-title')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        company_elem = item.select_one('.job-team-name')
        company = company_elem.get_text(strip=True) if company_elem else ""
        
        salary_elem = item.select_one('.job-description')
        salary = salary_elem.get_text(strip=True)[:50] if salary_elem else "面议"
        
        href = item.get('href', '')
        link = "https://remote-china.com" + href if href else ""
        
        # 从详情页获取申请链接、描述等
        apply_url = link  # 默认使用详情页链接
        detail_info = {}
        if str(i) in remotechina_detail_map:
            detail_file = remotechina_detail_map[str(i)].get('file', '')
            if detail_file:
                detail_info = parse_remotechina_detail(detail_file)
                if detail_info.get('applyUrl'):
                    apply_url = detail_info['applyUrl']
        
        if title and link:
            job = {
                "id": f"cn-remotechina-{i}{hash(title) % 10000}",
                "title": title,
                "company": company,
                "logo": "🌐",
                "category": guess_category_cn(title),
                "tags": ["远程"],
                "salary": salary,
                "location": "全国远程",
                "date": DATE,
                "isNew": True,
                "isFeatured": False,
                "canRefer": False,
                "source": "https://remote-china.com/jobs",
                "sourceUrl": link,
                "applyUrl": apply_url,
                "description": detail_info.get('description', ''),
                "responsibilities": detail_info.get('responsibilities', []),
                "requirements": detail_info.get('requirements', []),
                "benefits": []
            }
            remotechina_jobs.append(job)
    print(f"远程中文网: {len(remotechina_jobs)} jobs")
except Exception as e:
    print(f"远程中文网 解析失败: {e}")

# ========== 解析 V2EX 详情页 ==========
def parse_v2ex_detail(file_path):
    """解析V2EX详情页，提取公司信息、岗位职责、任职要求等"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 优先用帖子正文块，避免抓到回复内容
        content_elem = soup.select_one('.topic_content') or soup.select_one('.markdown_body')
        if not content_elem:
            # 兜底用 #Main 里的帖子块
            main_content = soup.select_one('#Main')
            if not main_content:
                return {}
            content_elem = main_content
        
        full_text = content_elem.get_text('\n', strip=True)
        
        result = {
            'description': '',
            'requirements': [],
            'benefits': [],
            'responsibilities': [],
            'company_info': '',
            'company': '',       # 新增：从正文提取的公司名
            'salary': '面议',
            'work_style': '',
            'contact': ''
        }
        
        # ===== 提取公司名（从正文） =====
        company_patterns = [
            r'【(.{2,20}?)】',                                       # 【公司名】
            r'(?:公司名?|Company)[：:\s]+([^\n\s]{2,20})',           # 公司：xxx
            r'(?:我司|我们公司|所在公司)[是为]?[：:\s]*([^\n，。,]{2,20})',  # 我司是xxx
            r'(?:关于我们|公司介绍|公司简介)[：:\s]*([^\n，。,]{2,25})',
        ]
        for pat in company_patterns:
            m = re.search(pat, full_text)
            if m:
                cname = m.group(1).strip()
                # 过滤无效词
                invalid = {'远程', '全职', '兼职', '招聘', '诚招', '职位', '岗位', '工作', '机会'}
                if cname and len(cname) >= 2 and cname not in invalid:
                    result['company'] = cname
                    break
        
        # ===== 提取薪资信息 =====
        salary_patterns = [
            r'薪资[：:]\s*([^\n，,。]{2,30})',
            r'工资[：:]\s*([^\n，,。]{2,30})',
            r'薪酬[：:]\s*([^\n，,。]{2,30})',
            r'薪水[：:]\s*([^\n，,。]{2,30})',
            r'月薪[：:]\s*([^\n，,。]{2,30})',
            r'(\d+[kK]\s*[-~～]\s*\d+[kK])',
            r'(\d+[kK]\+)',
        ]
        for pattern in salary_patterns:
            salary_match = re.search(pattern, full_text)
            if salary_match:
                result['salary'] = salary_match.group(1).strip()
                break
        
        # ===== 提取公司背景 =====
        company_keywords = ['公司背景', '公司介绍', '关于我们', '公司是', '我们是一家']
        for kw in company_keywords:
            if kw in full_text:
                start = full_text.find(kw)
                end = min(start + 500, len(full_text))
                result['company_info'] = full_text[start:end].split('\n')[0]
                break
        
        # ===== 提取福利待遇 =====
        benefit_keywords = ['福利待遇', '我们提供', '员工福利', '福利有', '可享受', '其他：']
        for kw in benefit_keywords:
            if kw in full_text:
                start = full_text.find(kw)
                next_headers = ['加分项', '任职要求', '岗位要求', '岗位职责']
                end_pos = len(full_text)
                for hdr in next_headers:
                    hdr_pos = full_text.find(hdr, start)
                    if hdr_pos > start:
                        end_pos = min(end_pos, hdr_pos)
                end = min(end_pos, start + 500)
                benefit_text = full_text[start:end]
                lines = [l.strip() for l in benefit_text.split('\n') if l.strip() and len(l) > 3]
                result['benefits'] = [l for l in lines if len(l) > 5][:6]
                break
        
        # ===== 提取岗位职责 =====
        duty_keywords = ['岗位职责', '工作内容', '职位描述', '工作职责', '主要工作']
        for kw in duty_keywords:
            if kw in full_text:
                start = full_text.find(kw)
                next_headers = ['任职要求', '岗位要求', '加分项', '任职资格']
                end_pos = len(full_text)
                for hdr in next_headers:
                    hdr_pos = full_text.find(hdr, start)
                    if hdr_pos > start:
                        end_pos = min(end_pos, hdr_pos)
                end = min(end_pos, start + 800)
                duty_text = full_text[start:end]
                lines = [l.strip() for l in duty_text.split('\n') if l.strip() and len(l) > 5 and not l.startswith('岗位职责')]
                result['responsibilities'] = lines[:8]
                break
        
        # ===== 提取任职要求 =====
        req_keywords = ['任职要求', '岗位要求', '任职资格']
        for kw in req_keywords:
            if kw in full_text:
                start = full_text.find(kw)
                next_headers = ['加分项', '工作方式', '简历投递', '联系方式', '福利']
                end_pos = len(full_text)
                for hdr in next_headers:
                    hdr_pos = full_text.find(hdr, start)
                    if hdr_pos > start:
                        end_pos = min(end_pos, hdr_pos)
                end = min(end_pos, start + 800)
                req_text = full_text[start:end]
                lines = [l.strip() for l in req_text.split('\n') if l.strip() and len(l) > 5 and not l.startswith('任职要求')]
                result['requirements'] = lines[:8]
                break
        
        # ===== 提取工作方式 =====
        if '远程' in full_text or '居家' in full_text or '可坐班' in full_text:
            result['work_style'] = '可远程，可坐班' if '可坐班' in full_text else '远程工作'
        
        # ===== 提取联系方式（邮箱 / 微信 / 其他） =====
        contact_parts = []
        email_matches = re.findall(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', full_text)
        if email_matches:
            contact_parts.append('邮箱: ' + '  /  '.join(email_matches[:2]))
        wx_patterns = [
            r'微信[：:\s]*([A-Za-z0-9_\-\u4e00-\u9fa5]{4,30})',
            r'\bwx[：:\s]+([A-Za-z0-9_\-]{4,30})',
            r'\bwechat[：:\s]+([A-Za-z0-9_\-]{4,30})',
        ]
        for pat in wx_patterns:
            wx_m = re.search(pat, full_text, re.IGNORECASE)
            if wx_m:
                contact_parts.append('微信: ' + wx_m.group(1).strip())
                break
        phone_m = re.search(r'(?:电话|手机|Tel|Phone)[：:\s]*([0-9\-\+\s]{7,15})', full_text, re.IGNORECASE)
        if phone_m:
            contact_parts.append('电话: ' + phone_m.group(1).strip())
        other_patterns = [
            r'(?:telegram|tg)[：:\s]*([A-Za-z0-9_@\-]{4,40})',
        ]
        for pat in other_patterns:
            other_m = re.search(pat, full_text, re.IGNORECASE)
            if other_m:
                val = other_m.group(1).strip()
                if '@' not in val:
                    contact_parts.append('Telegram: ' + val[:60])
                break
        result['contact'] = '\n'.join(contact_parts) if contact_parts else ''

        # ===== 联系方式行过滤器 =====
        def is_contact_line(line):
            line_lower = line.lower()
            if re.search(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', line):
                return True
            if any(k in line_lower for k in ['微信', 'wx:', 'wx：', 'wechat', '电话', '手机',
                                              'tel:', 'tel：', '简历发', '投递至', 'telegram', ' tg ']):
                return True
            return False
        
        # ===== 过滤联系方式行 =====
        result['responsibilities'] = [l for l in result['responsibilities'] if not is_contact_line(l)]
        result['requirements']     = [l for l in result['requirements']     if not is_contact_line(l)]
        
        # ===== 工作职责兜底：若结构化内容为空，取正文全文去联系方式 =====
        if not result['responsibilities'] and not result['requirements']:
            all_lines = [l.strip() for l in full_text.split('\n') if l.strip() and len(l.strip()) > 5]
            # 过滤联系方式行 + 太短的行
            clean_lines = [l for l in all_lines if not is_contact_line(l)]
            # 取前30行作为兜底内容
            result['responsibilities'] = clean_lines[:30]
        
        # ===== 生成 description =====
        if result['company_info'] and len(result['company_info']) > 10:
            result['description'] = result['company_info'][:200]
        elif result['responsibilities']:
            desc_text = ' | '.join(result['responsibilities'][:3])
            if len(desc_text) > 10:
                result['description'] = desc_text
        if result['company_info'] and len(result['company_info']) <= 10:
            result['company_info'] = ''
        
        return result
    except Exception as e:
        print(f"解析详情页失败: {e}")
        return {}

# ========== 构建 URL 到详情文件的映射 ==========
detail_url_map = {}
# 从预下载的映射文件读取
if os.path.exists('/tmp/v2ex_url_map.txt'):
    with open('/tmp/v2ex_url_map.txt', 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                url_key = parts[0]
                idx = int(parts[1])
                detail_url_map[url_key] = f'/tmp/v2ex_detail_{idx}.html'
print(f"已建立 {len(detail_url_map)} 个详情页映射")

# ========== 处理 V2EX ==========
v2ex_jobs = []
try:
    with open('/tmp/v2ex.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.cell')[:200]
    
    today_str = DATE  # YYYY-MM-DD
    skipped_old = 0
    
    for i, item in enumerate(items):
        title_elem = item.select_one('span.item_title a') or item.select_one('a.topic-link')
        if not title_elem:
            continue
        
        title = title_elem.get_text(strip=True)
        href = title_elem.get('href', '')
        link = "https://www.v2ex.com" + href if href.startswith('/') else href
        
        if not title or not link:
            continue
        
        # ===== 过滤：黑名单标题（非招聘内容，如网站上线公告等）=====
        TITLE_BLACKLIST = [
            '一直想做的远程工作集合网站',
            '远程工作网站开放',
            # 可在此继续追加非招聘类标题关键词
        ]
        if any(kw in title for kw in TITLE_BLACKLIST):
            continue
        
        # ===== 过滤：只保留当天发布的帖子 =====
        time_elem = item.select_one('span[title]')
        post_date = ''
        if time_elem:
            time_title = time_elem.get('title', '')  # 形如 "2026-03-27 14:33:01 +08:00"
            if time_title:
                post_date = time_title[:10]  # 取 YYYY-MM-DD
        
        if post_date and post_date != today_str:
            skipped_old += 1
            continue  # 不是今天发的，跳过
        
        # ===== 根据URL查找详情页 =====
        detail_info = {}
        for url_key, detail_file in detail_url_map.items():
            if url_key in link:
                detail_info = parse_v2ex_detail(detail_file)
                break
        
        # ===== 公司名：优先从详情页正文提取，其次标题模式，最后"海外公司" =====
        company = detail_info.get('company', '')
        
        if not company:
            # 标题模式提取
            invalid_companies = {'远程', '全职远程', '远程全职招聘', '远程兼职', '全职远程工作', '远程全职', '招聘'}
            m1 = re.search(r'【(.+?)】', title)
            m2 = re.search(r'^([A-Za-z\u4e00-\u9fa5][A-Za-z0-9\u4e00-\u9fa5]{1,20})\s*(?:招聘|招|聘|：|:)', title)
            m3 = re.search(r'^([A-Za-z\u4e00-\u9fa5][A-Za-z0-9\u4e00-\u9fa5]{2,15})\s*[-–]\s*(?:远程|全职|招聘)', title)
            for m in [m1, m2, m3]:
                if m:
                    cname = re.sub(r'[\[\]（）()（）]', '', m.group(1)).strip()
                    if cname and len(cname) >= 2 and cname not in invalid_companies:
                        company = cname
                        break
        
        if not company:
            company = '海外公司'
        
        job = {
            "id": f"cn-v2ex-{i}{hash(title) % 10000}",
            "title": title,
            "company": company,
            "logo": "💻",
            "category": guess_category_cn(title),
            "tags": ["远程", "V2EX", "社群内推"],
            "salary": detail_info.get('salary', '面议'),
            "location": "全国远程",
            "date": DATE,
            "isNew": True,
            "isFeatured": False,
            "canRefer": True,
            "source": "https://www.v2ex.com/go/remote",
            "sourceUrl": link,
            "description": detail_info.get('description', ''),
            "requirements": detail_info.get('requirements', []),
            "benefits": detail_info.get('benefits', []),
            "responsibilities": detail_info.get('responsibilities', []),
            "company_info": detail_info.get('company_info', ''),
            "work_style": detail_info.get('work_style', ''),
            "contact": detail_info.get('contact', '')
        }
        v2ex_jobs.append(job)
    
    print(f"V2EX: {len(v2ex_jobs)} jobs（跳过非今日帖子: {skipped_old}）")
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
    items = items[:200] if items else []
    
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
                "category": guess_category_cn(title),
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

# ========== 合并去重数据 ==========
def dedup_by_source_url(jobs):
    """按 sourceUrl 去重，保留最新（即列表靠前的）那条"""
    seen = {}
    result = []
    for job in jobs:
        key = job.get('sourceUrl', '') or job.get('id', '')
        if key and key not in seen:
            seen[key] = True
            result.append(job)
    return result

def merge_jobs(old_jobs, new_jobs):
    """合并新旧数据并按 sourceUrl 全局去重，新数据优先（放前面）"""
    merged = new_jobs + old_jobs
    deduped = dedup_by_source_url(merged)
    return deduped

# V2EX 数据放最前面（最新抓取的社群内推岗位）
# 国内上限2000条（包含 who-is-hiring 数据）
merged_cn = merge_jobs(existing_cn, v2ex_jobs + remotechina_jobs + dianyu_jobs + rebase_jobs)[:2000]
# 海外上限2000条（Remote OK + Remotive + 远程岛）
merged_global = merge_jobs(existing_global, remoteok_jobs + remotive_jobs + yuanchengdao_jobs)[:2000]

print(f"合并去重后: CN={len(merged_cn)}, Global={len(merged_global)}")

# ========== 写入 JS 文件 ==========
def escape_str(s):
    """转义字符串中的特殊字符，确保生成合法的 JS 字符串"""
    if s is None:
        return ""
    s = str(s)
    # 顺序很重要：先转义反斜杠，再转义其他字符
    s = s.replace("\\", "\\\\")  # 反斜杠
    s = s.replace("\n", "\\n")   # 换行
    s = s.replace("\r", "\\r")   # 回车
    s = s.replace("\t", "\\t")   # 制表符
    s = s.replace("'", "\\'")    # 单引号
    s = s.replace('"', '\\"')    # 双引号
    return s

def escape_list(arr):
    """转义数组中的每个元素"""
    if not isinstance(arr, list):
        return []
    return [escape_str(item) for item in arr]

def jobs_to_js(jobs, var_name):
    lines = [f"const {var_name} = ["]
    for job in jobs:
        lines.append("  {")
        for i, (key, val) in enumerate(job.items()):
            if isinstance(val, bool):
                lines.append(f"    {key}: {'true' if val else 'false'},")
            elif isinstance(val, list):
                # 使用新的 escape_list 函数处理数组
                items = ", ".join([f"'{escape_str(t)}'" for t in escape_list(val)])
                lines.append(f"    {key}: [{items}],")
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

# ========== 更新 money.xlsx ==========
try:
    from openpyxl import load_workbook
    import re as _re
    
    xlsx_file = 'money.xlsx'
    if os.path.exists(xlsx_file):
        wb = load_workbook(xlsx_file)
        sheet = wb.active
        
        # 数据从第3行开始（第1行标题，第2行表头）
        data_start_row = 3
        
        # 插入空行给新数据
        if v2ex_jobs and sheet.cell(data_start_row, 1).value is not None:
            sheet.insert_rows(data_start_row, len(v2ex_jobs))
        
        def build_job_desc(job):
            """组合工作职责&任职要求，去掉联系方式。若无结构化内容，全文兜底。"""
            def is_contact(line):
                ll = line.lower()
                if _re.search(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', line):
                    return True
                if any(k in ll for k in ['微信', 'wx:', 'wx：', 'wechat', '电话', '手机',
                                         'tel:', 'tel：', '简历发', '投递至', 'telegram', ' tg ']):
                    return True
                return False
            
            parts = []
            raw_resp = job.get('responsibilities') or []
            raw_reqs = job.get('requirements') or []
            # responsibilities/requirements 可能是字符串或列表，统一转成列表
            if isinstance(raw_resp, str):
                raw_resp = [l for l in raw_resp.splitlines() if l.strip()]
            if isinstance(raw_reqs, str):
                raw_reqs = [l for l in raw_reqs.splitlines() if l.strip()]
            resp = [l for l in raw_resp if not is_contact(str(l))]
            reqs = [l for l in raw_reqs if not is_contact(str(l))]
            
            if resp:
                parts.append('岗位职责：\n' + '\n'.join(resp[:8]))
            if reqs:
                parts.append('任职要求：\n' + '\n'.join(reqs[:8]))
            if job.get('company_info') and len(job.get('company_info', '')) > 10:
                parts.append('公司介绍：' + job['company_info'][:200])
            
            return '\n\n'.join(parts) if parts else '详见原帖'
        
        # 写入 V2EX 数据
        for i, job in enumerate(v2ex_jobs):
            row = data_start_row + i
            
            # 公司名已在 V2EX 处理段完成，直接使用
            final_company = job.get('company', '海外公司')
            
            # 工作职责（去掉联系方式，兜底逻辑已在 parse_v2ex_detail 完成）
            job_desc = build_job_desc(job)
            
            # 联系方式 → 内推方式列
            contact_val = job.get('contact', '')
            infer_method = contact_val if contact_val else '星球同学 私Junes内推'
            
            sheet.cell(row, 1).value = final_company           # 公司
            sheet.cell(row, 2).value = '互联网'                 # 行业
            sheet.cell(row, 3).value = job['category']          # 职位类别
            sheet.cell(row, 4).value = job['title']             # 职位名称
            sheet.cell(row, 5).value = 'Remote'                 # 地区
            sheet.cell(row, 6).value = '内推岗'                 # 申请链接
            sheet.cell(row, 7).value = '星球同学 私Junes内推'   # 内推
            sheet.cell(row, 8).value = job.get('date', DATE)    # 日期
            sheet.cell(row, 9).value = job_desc                 # 工作职责（无联系方式）
            sheet.cell(row, 10).value = job.get('salary', '面议')   # 薪资
            sheet.cell(row, 11).value = infer_method            # 内推方式
            sheet.cell(row, 12).value = job.get('sourceUrl', '')    # 来源
        
        # 写入 who-is-hiring 数据（在 V2EX 数据之后）
        rebase_start_row = data_start_row + len(v2ex_jobs)
        if rebase_jobs_for_excel:
            sheet.insert_rows(rebase_start_row, len(rebase_jobs_for_excel))
            
            for i, job in enumerate(rebase_jobs_for_excel):
                row = rebase_start_row + i
                original = job.get('original_data', {})
                
                # 提取联系方式（contact_channels 字段，可能为 None）
                contact_channels = original.get('contact_channels') or []
                if not isinstance(contact_channels, list):
                    contact_channels = [str(contact_channels)]
                contact_str = ', '.join(str(c) for c in contact_channels)
                
                # 构建职位描述
                job_desc = build_job_desc(job)
                
                # 如果没有结构化内容，尝试从原始数据构建
                if job_desc == '详见原帖' and original.get('description'):
                    job_desc = original.get('description', '')[:500]
                
                sheet.cell(row, 1).value = job.get('company', 'Rebase招聘')     # 公司
                sheet.cell(row, 2).value = '互联网'                              # 行业
                sheet.cell(row, 3).value = job['category']                       # 职位类别
                sheet.cell(row, 4).value = job['title']                          # 职位名称
                sheet.cell(row, 5).value = job.get('location', 'Remote')         # 地区
                sheet.cell(row, 6).value = '查看原帖'                            # 申请链接
                sheet.cell(row, 7).value = 'Rebase社区'                          # 内推
                sheet.cell(row, 8).value = job.get('date', DATE)                 # 日期
                sheet.cell(row, 9).value = job_desc                              # 工作职责
                sheet.cell(row, 10).value = job.get('salary', '面议')            # 薪资
                sheet.cell(row, 11).value = contact_str if contact_str else '详见原帖'  # 内推方式（含联系方式）
                sheet.cell(row, 12).value = job.get('sourceUrl', '')             # 来源
        
        wb.save(xlsx_file)
        total_inserted = len(v2ex_jobs) + len(rebase_jobs_for_excel)
        print(f"✅ money.xlsx 已更新，插入 {len(v2ex_jobs)} 条V2EX数据 + {len(rebase_jobs_for_excel)} 条who-is-hiring数据")
except Exception as e:
    print(f"money.xlsx 更新失败: {e}")
EOF

echo "数据更新完成: $DATE" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 清理临时文件（保留详情页文件用于调试）
rm -f /tmp/remoteok.json /tmp/remote-china.html /tmp/v2ex*.html /tmp/v2ex_url_map.txt /tmp/remoteok_url_map.pkl
# rm -f /tmp/remoteok_detail*.html  # 暂时保留详情页文件
