import re

url_map = {
    "gl-001": "https://www.v2ex.com/go/remote",
    "gl-002": "https://www.v2ex.com/go/remote",
    "gl-003": "https://www.v2ex.com/go/remote",
    "gl-004": "https://www.v2ex.com/go/remote",
    "gl-005": "https://www.v2ex.com/go/remote",
    "gl-006": "https://www.v2ex.com/go/remote",
    "gl-007": "https://www.v2ex.com/go/remote",
    "gl-008": "https://www.v2ex.com/go/remote",
    "gl-009": "https://www.v2ex.com/go/remote",
    "gl-010": "https://www.v2ex.com/go/remote",
    "gl-011": "https://www.v2ex.com/go/remote",
    "gl-012": "https://remote-china.com/jobs/849",
    "gl-013": "https://remote-china.com/jobs/872",
    "gl-014": "https://remote-china.com/jobs/889",
    "gl-015": "https://remote-china.com/jobs/871",
}

def fix_source_url(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    current_id = None
    result = []
    
    for line in lines:
        id_match = re.match(r'^    id: "(gl-\d+)",', line)
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

fix_source_url('/Users/qisoong/WorkBuddy/20260317141747/jobs-global.js')
