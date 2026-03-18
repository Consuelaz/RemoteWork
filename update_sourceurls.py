import re

# 基于实际抓取到的申请URL映射
apply_url_map_cn = {
    "cn-001": "https://eleduck.com/posts/dDfgvD",  # 物流技术运营专员 - 推测为电鸭平台
    "cn-002": "https://www.zhipin.com/job_detail/b188f87a8320fc2703dz2ti1GVdS.html",  # HR主管 - BOSS直聘
    "cn-003": "https://www.zhaopin.com/jobdetail/CCL1475319280J40833117707.htm",  # 插画设计师 - 智联招聘
    "cn-004": "#",  # 商旅客服 - 无直接链接
    "cn-005": "#",  # 新媒体运营 - 无直接链接
    "cn-006": "https://www.zhipin.com/job_detail/2f8614091104659e0nVz29q_GVNV.html",  # GOLANG后端 - BOSS直聘
    "cn-007": "#",  # 广告投放项目经理 - 无直接链接
    "cn-008": "https://www.zhipin.com/job_detail/fa94f3e6ad411ddf0nZ42929F1FX.html",  # 招聘专员 - BOSS直聘
    "cn-009": "#",  # 思辨老师 - 无直接链接
    "cn-010": "#",  # 线上行政客服 - 无直接链接
    "cn-011": "#",  # JAVA高级架构师 - 无直接链接
    "cn-012": "https://www.zhaopin.com/jobdetail/CCL1507259470J40831719411.htm",  # 全栈AI Agent - 智联招聘
    "cn-013": "#",  # GO开发工程师 - 无直接链接
    "cn-014": "https://www.zhaopin.com/jobdetail/CCL1436870760J40757721506.htm",  # 知识产权专员 - 智联招聘
    "cn-015": "https://eleduck.com/posts/dDfgvD",  # 全栈AI Ads Agent - 电鸭平台
    "cn-016": "#",  # .NET全栈兼职 - 无直接链接
    "cn-017": "#",  # Python后端 - 无直接链接
    "cn-018": "#",  # 谷歌SEO专员 - 无直接链接
    "cn-019": "#",  # 前端/后端工程师 - 无直接链接
    "cn-020": "https://eleduck.com/posts/dDfgvD",  # AI产品工程师 - 电鸭平台
    "cn-021": "https://eleduck.com/posts/dDfgvD",  # 前端AI音乐视频 - 电鸭平台
    "cn-022": "https://eleduck.com/posts/dDfgvD",  # 全栈AI驱动兼职 - 电鸭平台
    "cn-023": "https://eleduck.com/posts/dDfgvD",  # 杭州远程全栈 - 电鸭平台
    "cn-024": "https://eleduck.com/posts/dDfgvD",  # Web3运营 - 电鸭平台
}

apply_url_map_global = {
    "global-001": "https://eleduck.com/posts/dDfgvD",  # 海外岗位 - 电鸭平台
    "global-002": "https://eleduck.com/posts/dDfgvD",
    "global-003": "https://eleduck.com/posts/dDfgvD",
    "global-004": "https://eleduck.com/posts/dDfgvD",
    "global-005": "https://eleduck.com/posts/dDfgvD",
    "global-006": "https://eleduck.com/posts/dDfgvD",
    "global-007": "https://eleduck.com/posts/dDfgvD",
    "global-008": "https://eleduck.com/posts/dDfgvD",
    "global-009": "https://eleduck.com/posts/dDfgvD",
    "global-010": "https://eleduck.com/posts/dDfgvD",
    "global-011": "https://eleduck.com/posts/dDfgvD",
    "global-012": "https://remote-china.com/jobs/849",  # remote-china平台
    "global-013": "https://remote-china.com/jobs/872",
    "global-014": "https://remote-china.com/jobs/889",
    "global-015": "https://remote-china.com/jobs/871",
}

def update_apply_urls(filepath, url_map):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    current_id = None
    result = []
    
    for line in lines:
        id_match = re.match(r'^    id: "(cn-\d+|global-\d+)",', line)
        if id_match:
            current_id = id_match.group(1)
            result.append(line)
        elif current_id and 'sourceUrl:' in line:
            if current_id in url_map:
                new_line = re.sub(r'sourceUrl: "[^"]*"', f'sourceUrl: "{url_map[current_id]}"', line)
                result.append(new_line)
            else:
                result.append(line)
        else:
            result.append(line)
    
    new_content = '\n'.join(result)
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"已更新 {filepath}")

update_apply_urls('/Users/qisoong/WorkBuddy/20260317141747/jobs-cn.js', apply_url_map_cn)
update_apply_urls('/Users/qisoong/WorkBuddy/20260317141747/jobs-global.js', apply_url_map_global)
