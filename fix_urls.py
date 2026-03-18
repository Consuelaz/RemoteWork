import re

url_map = {
    "cn-001": "https://remote-china.com/jobs/894",
    "cn-002": "https://remote-china.com/jobs/893",
    "cn-003": "https://remote-china.com/jobs/892",
    "cn-004": "https://remote-china.com/jobs/891",
    "cn-005": "https://remote-china.com/jobs/887",
    "cn-006": "https://remote-china.com/jobs/884",
    "cn-007": "https://remote-china.com/jobs/883",
    "cn-008": "https://remote-china.com/jobs/882",
    "cn-009": "https://remote-china.com/jobs/885",
    "cn-010": "https://remote-china.com/jobs/886",
    "cn-011": "https://remote-china.com/jobs/880",
    "cn-012": "https://remote-china.com/jobs/876",
    "cn-013": "https://remote-china.com/jobs/875",
    "cn-014": "https://remote-china.com/jobs/874",
    "cn-015": "https://remote-china.com/jobs/866",
    "cn-016": "https://remote-china.com/jobs/865",
    "cn-017": "https://remote-china.com/jobs/864",
    "cn-018": "https://remote-china.com/jobs/856",
    "cn-019": "https://remote-china.com/jobs/854",
    "cn-020": "https://www.v2ex.com/go/remote",
    "cn-021": "https://www.v2ex.com/go/remote",
    "cn-022": "https://www.v2ex.com/go/remote",
    "cn-023": "https://www.v2ex.com/go/remote",
    "cn-024": "https://www.v2ex.com/go/remote",
}

def fix_source_url(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    current_id = None
    result = []
    
    for line in lines:
        id_match = re.match(r'^    id: "(cn-\d+)",', line)
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
    print(f"已修复 {filepath}")

fix_source_url('/Users/qisoong/WorkBuddy/20260317141747/jobs-cn.js')
