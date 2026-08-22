#!/usr/bin/env python3
"""
Community Comic Sources Tracker
Monitors active community repositories and detects new comic sources or version bumps.
"""

import json
import os
import sys
import urllib.request
import time
from datetime import datetime, timezone, timedelta

TRACKED_REPOSITORIES = [
    ('senran-N/venera-configs', 'senran-N (禁漫/Hitomi/拷贝增强)'),
    ('YHQY-Dev/venera-sources', 'YHQY (国内小众源集合)'),
    ('AXmishell/venera-configs', 'AXmishell (漫蛙/GoDa/hipmh)'),
    ('Qing-Novel/venerax-configs', 'Qing-Novel (VeneraX配套源)'),
    ('EricDasha/venera-configs', 'EricDasha (nhentai/manwaba)'),
    ('coldnighten/venera-configs', 'coldnighten (清理停运源)'),
    ('venera-app/venera-configs', '官方原版仓库'),
]

def fetch_json(url, timeout=6):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

def parse_semver(ver):
    try:
        parts = [int(x) for x in ver.split('-')[0].split('.')]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)
    except:
        return (0, 0, 0)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(root_dir, 'index.json')
    
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found")
        sys.exit(1)
        
    with open(index_path, 'r', encoding='utf-8') as f:
        my_sources = {item['key']: item.get('version', '1.0.0') for item in json.load(f)}
        
    print(f"Tracking {len(TRACKED_REPOSITORIES)} community repositories against {len(my_sources)} local sources...\n")
    
    new_sources = []
    version_bumps = []
    
    for repo, desc in TRACKED_REPOSITORIES:
        data = None
        for branch in ['main', 'master']:
            url = f'https://raw.githubusercontent.com/{repo}/{branch}/index.json'
            try:
                data = fetch_json(url)
                if data:
                    break
            except Exception:
                continue
                
        if not data or not isinstance(data, list):
            print(f"  [跳过] {repo}: 无法获取 index.json")
            continue
            
        print(f"  [检查] {repo:28} (包含 {len(data)} 个源)")
        
        for item in data:
            if not isinstance(item, dict):
                continue
            key = item.get('key')
            name = item.get('name', key)
            ver = item.get('version', '1.0.0')
            desc_text = item.get('description', '')
            
            if not key:
                continue
                
            if key not in my_sources:
                new_sources.append({
                    'repo': repo,
                    'name': name,
                    'key': key,
                    'version': ver,
                    'desc': desc_text
                })
            else:
                my_ver = my_sources[key]
                if parse_semver(ver) > parse_semver(my_ver):
                    version_bumps.append({
                        'repo': repo,
                        'name': name,
                        'key': key,
                        'remote_version': ver,
                        'my_version': my_ver
                    })
                    
    # Generate Markdown Report
    has_updates = bool(new_sources or version_bumps)
    date_str = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S (北京时间)')
    
    md = f"## 🔍 社区漫画源更新巡检报告\n\n"
    md += f"**巡检时间**：`{date_str}`\n\n"
    
    if not has_updates:
        md += "🎉 **当前仓库收录的所有漫画源均为全网最新版本，未发现新源或更高版本更新。**\n"
    else:
        if version_bumps:
            md += "### ⬆️ 发现更高版本的源更新\n\n"
            md += "| 漫画源 | Key | 社区最高版本 | 当前仓库版本 | 维护来源仓库 |\n"
            md += "| :--- | :--- | :---: | :---: | :--- |\n"
            for u in version_bumps:
                md += f"| **{u['name']}** | `{u['key']}` | `v{u['remote_version']}` | `v{u['my_version']}` | [`{u['repo']}`](https://github.com/{u['repo']}) |\n"
            md += "\n"
            
        if new_sources:
            md += "### 🌟 发现社区新收录的漫画源\n\n"
            md += "| 漫画源名称 | 标识符 (Key) | 初始版本 | 描述说明 | 来源仓库 |\n"
            md += "| :--- | :--- | :---: | :--- | :--- |\n"
            for s in new_sources:
                md += f"| **{s['name']}** | `{s['key']}` | `v{s['version']}` | {s['desc'] or '-'} | [`{s['repo']}`](https://github.com/{s['repo']}) |\n"
            md += "\n"
            
        md += "---\n*本通知由 GitHub Actions 自动化社区源巡检机器人生成，是否合并更新由维护者自主决定。*\n"
        
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(md)
            
    report_file = '/tmp/community_updates_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(md)
        
    print(f"\nReport generated. Updates found: {has_updates}")
    if has_updates:
        # Write flag for workflow
        with open('/tmp/has_community_updates.txt', 'w') as f:
            f.write('true')
    else:
        with open('/tmp/has_community_updates.txt', 'w') as f:
            f.write('false')

if __name__ == '__main__':
    main()
