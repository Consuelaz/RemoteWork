import re

# 原始来源URL映射
original_source_cn = {
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

original_source_global = {
    "global-001": "https://www.v2ex.com/go/remote",
    "global-002": "https://www.v2ex.com/go/remote",
    "global-003": "https://www.v2ex.com/go/remote",
    "global-004": "https://www.v2ex.com/go/remote",
    "global-005": "https://www.v2ex.com/go/remote",
    "global-006": "https://www.v2ex.com/go/remote",
    "global-007": "https://www.v2ex.com/go/remote",
    "global-008": "https://www.v2ex.com/go/remote",
    "global-009": "https://www.v2ex.com/go/remote",
    "global-010": "https://www.v2ex.com/go/remote",
    "global-011": "https://www.v2ex.com/go/remote",
    "global-012": "https://remote-china.com/jobs/849",
    "global-013": "https://remote-china.com/jobs/872",
    "global-014": "https://remote-china.com/jobs/889",
    "global-015": "https://remote-china.com/jobs/871",
}

def restore_sources(filepath, source_map):
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
        elif current_id and 'source: "网络"' in line:
            if current_id in source_map:
                # 替换为原始来源URL
                new_line = line.replace('source: "网络"', f'source: "{source_map[current_id]}"')
                result.append(new_line)
            else:
                result.append(line)
        else:
            result.append(line)

    new_content = '\n'.join(result)
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"已恢复 {filepath}")

restore_sources('/Users/qisoong/WorkBuddy/20260317141747/jobs-cn.js', original_source_cn)
restore_sources('/Users/qisoong/WorkBuddy/20260317141747/jobs-global.js', original_source_global)
