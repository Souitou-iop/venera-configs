#!/usr/bin/env python3
"""
Venera Comic Sources Automated Health Check Script
Tests endpoint connectivity and basic responsiveness for all sources listed in index.json.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import time

def check_source(source):
    key = source.get('key')
    name = source.get('name')
    file_name = source.get('fileName')
    version = source.get('version', '1.0.0')
    
    # Domain / API definitions for health check
    targets = {
        'copy_manga': ('https://api.copy2000.online/api/v3/system/network2?platform=3', 'GET', {'User-Agent': 'COPY/3.0.9', 'source': 'copyApp'}),
        'Komiic': ('https://komiic.com/api/query', 'POST', {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://komiic.com/', 'Content-Type': 'application/json'}, json.dumps({'operationName': 'allCategory', 'variables': {}, 'query': 'query allCategory { allCategory { id name } }'}).encode('utf-8')),
        'baozi': ('https://baozimhcn.com/', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'picacg': ('https://picaapi.picacomic.com/categories', 'GET', {'User-Agent': 'okhttp/3.8.1', 'api-key': 'C69BAF41DA5ABD1FFEDC6D2FEA56B'}),
        'jm': ('https://rup4a04-c02.tos-cn-hongkong.bytepluses.com/newsvr-2025.txt', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'ehentai': ('https://api.e-hentai.org/api.php', 'POST', {'Content-Type': 'application/json'}, json.dumps({'method': 'gdata', 'gidlist': [[3380000, 'a1b2c3d4e5']]}).encode('utf-8')),
        'manhuaren': ('https://www.manhuaren.com/', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'ikmmh': ('https://www.ikamn.com/', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'nhentai': ('https://nhentai.net/', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'zaimanhua': ('https://api.zaimanhua.com/api/v3/system/network2?platform=3', 'GET', {'User-Agent': 'COPY/3.0.9'}),
        'wnacg': ('https://www.wnacg.com/', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'comick': ('https://api.comick.fun/top', 'GET', {'User-Agent': 'Mozilla/5.0'}),
        'manga_dex': ('https://api.mangadex.org/manga?limit=1', 'GET', {'User-Agent': 'Mozilla/5.0'}),
    }
    
    target_info = targets.get(key)
    if not target_info:
        return {'key': key, 'name': name, 'version': version, 'status': '⚪ 未配置探测', 'code': '-', 'latency': '-'}
    
    url = target_info[0]
    method = target_info[1]
    headers = target_info[2]
    data = target_info[3] if len(target_info) > 3 else None
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            latency = int((time.time() - start_time) * 1000)
            if resp.status in [200, 201, 206]:
                return {'key': key, 'name': name, 'version': version, 'status': '🟢 正常 (Healthy)', 'code': resp.status, 'latency': f'{latency}ms'}
            else:
                return {'key': key, 'name': name, 'version': version, 'status': '🟡 响应异常', 'code': resp.status, 'latency': f'{latency}ms'}
    except urllib.error.HTTPError as e:
        latency = int((time.time() - start_time) * 1000)
        if e.code in [401, 403, 210]:
            return {'key': key, 'name': name, 'version': version, 'status': '🟡 需鉴权/CF保护', 'code': e.code, 'latency': f'{latency}ms'}
        return {'key': key, 'name': name, 'version': version, 'status': '🔴 异常', 'code': e.code, 'latency': f'{latency}ms'}
    except Exception as e:
        return {'key': key, 'name': name, 'version': version, 'status': '🔴 连接失败', 'code': 'ERR', 'latency': '-'}

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(root_dir, 'index.json')
    
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found")
        sys.exit(1)
        
    with open(index_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
        
    print(f"Starting Health Check for {len(sources)} comic sources...\n")
    results = []
    
    for s in sources:
        res = check_source(s)
        results.append(res)
        print(f"  [{res['status']}] {res['name']:15} ({res['key']}) -> Code: {res['code']}, Latency: {res['latency']}")
        time.sleep(0.1)
        
    # Generate summary markdown table
    md = "# 🩺 漫画源实时健康探活报告 (Source Health Report)\n\n"
    md += f"最后检测时间：`{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}`\n\n"
    md += "| 漫画源 | Key | 脚本版本 | 运行状态 | HTTP状态码 | 响应延迟 |\n"
    md += "| :--- | :--- | :---: | :---: | :---: | :---: |\n"
    
    for r in results:
        md += f"| **{r['name']}** | `{r['key']}` | `{r['version']}` | {r['status']} | `{r['code']}` | `{r['latency']}` |\n"
        
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(md)
            
    print("\nHealth check finished successfully.")

if __name__ == '__main__':
    main()
