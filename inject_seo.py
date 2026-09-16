#!/usr/bin/env python3
"""
🎯 灵犀游戏大厅 · 子页面 SEO 注入工具
========================================================
确保所有游戏 HTML 子页面具有一致的 SEO 元数据、结构化数据和社交共享标签。

用法（在 deploy.py 中集成或独立运行）：
  python3 inject_seo.py dry-run    # 预览哪些文件需要注入（不修改）
  python3 inject_seo.py inject     # 批量注入 SEO 到缺失字段的游戏页面
  python3 inject_seo.py report     # 生成 SEO 完备性报告
  python3 inject_seo.py upload     # 批量注入并上传到 GitHub

策略：
- 已有 title/description/og/jsonld 的不重复注入
- 缺失项逐项补全
- 每款游戏生成独一无二的 VideoGame JSON-LD
"""

import os, sys, json, base64, hashlib, re, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════
# 配置
# ══════════════════════════════════════════════════════

MATON_API_KEY = os.environ.get("MATON_API_KEY",
    "v2.xOedfPfv9hou9ht8BXTbk7OKPlRUUvh5WuyJNC8Q3mLrU5dQVGL5rARouO2DNnC-IKG0UGeYm79Cfw1aIjsOw48Fram7uaVouZHiYKGTZzMBg4SuQLJLz4gY")

MATON_BASE = "https://api.maton.ai"
GITHUB_OWNER = "VIP-881"
GITHUB_REPO = "hot-h5-games"
REPO_PATH = f"{GITHUB_OWNER}/{GITHUB_REPO}"
BASE_URL = f"https://{GITHUB_OWNER}.github.io/{GITHUB_REPO}"

# 游戏名称映射（文件名 → 中文名称 + 英文名称 + 描述 + 类别 + 类别标签）
GAME_META = {
    "2048": ("2048 数字合并", "2048 Number Merge", "经典4×4网格滑动合并，挑战2048！", "益智", "Puzzle"),
    "mines": ("扫雷", "Minesweeper", "经典扫雷游戏，标记地雷揭开安全格", "益智", "Puzzle"),
    "breakout": ("打砖块", "Breakout", "经典弹球打砖块，消除全部砖块过关", "动作", "Action"),
    "flappy": ("Flappy Bird", "Flappy Bird", "点击让小鸟飞越管道，挑战最高分", "动作", "Action"),
    "sudoku": ("数独", "Sudoku", "经典9×9数独，从简单到专家难度", "益智", "Puzzle"),
    "sokoban": ("推箱子", "Sokoban", "将箱子推到目标点，经典解谜", "益智", "Puzzle"),
    "tetris": ("俄罗斯方块", "Tetris", "经典俄罗斯方块，Gmail邮件主题版", "街机", "Arcade"),
    "snake": ("贪吃蛇", "Snake", "经典贪吃蛇，吃食物越长越长", "街机", "Arcade"),
    "pacman": ("吃豆人", "Pacman", "经典吃豆人，躲避幽灵吃光豆子", "街机", "Arcade"),
    "pong": ("乒乓球 Pong", "Pong", "经典乒乓对打，双人同屏对战", "街机", "Arcade"),
    "bubbleshooter": ("泡泡龙射击", "Bubble Shooter", "瞄准射击消除同色泡泡", "益智", "Puzzle"),
    "suika": ("合成大西瓜", "Suika Game", "合成水果，越大越好玩", "益智", "Puzzle"),
    "dino": ("恐龙快跑", "Dino Run", "经典Chrome恐龙跑酷", "动作", "Action"),
    "doodlejump": ("涂鸦跳跃", "Doodle Jump", "不断向上跳跃，避开障碍", "动作", "Action"),
    "asteroids": ("小行星", "Asteroids", "驾驶飞船摧毁小行星，经典街机", "街机", "Arcade"),
    "invader": ("太空侵略者", "Space Invaders", "经典纵版射击，消灭外星人", "街机", "Arcade"),
    "memory": ("翻牌记忆", "Memory Match", "翻牌配对，考验记忆力", "益智", "Puzzle"),
    "match3": ("三消宝石", "Match 3", "经典三消游戏，交换宝石连线消除", "益智", "Puzzle"),
    "puzzle": ("拼图", "Jigsaw Puzzle", "拖拽拼图碎片还原完整图片", "益智", "Puzzle"),
    "jigsaw": ("拼图", "Jigsaw Puzzle", "拖拽拼图碎片还原完整图片", "益智", "Puzzle"),
    "hangman": ("猜单词", "Hangman", "经典猜单词游戏，在限定次数内猜对", "益智", "Puzzle"),
    "connect4": ("四子棋", "Connect 4", "经典四子连线棋，横竖斜连四子即胜", "益智", "Puzzle"),
    "battleship": ("海战棋", "Battleship", "经典海战棋，击沉对方全部战舰", "策略", "Strategy"),
    "blackjack": ("21点", "Blackjack", "经典扑克21点，庄闲对决", "博牌", "Casino"),
    "othello": ("黑白棋", "Othello", "经典黑白翻转棋，夹击翻转棋子", "策略", "Strategy"),
    "tictactoe": ("井字棋", "Tic Tac Toe", "经典井字棋，三连一线即胜", "益智", "Puzzle"),
    "rpg": ("任务打怪 RPG", "Task Monster RPG", "Notion任务化身怪物，完成即可升级！", "角色扮演", "RPG"),
    "monopoly": ("GitHub 大富翁", "GitHub Monopoly", "GitHub提交就是骰子点数，买地建房！", "模拟", "Simulation"),
    "code-typer": ("代码打字王", "Code Typer", "真实代码片段，打字速度大比拼", "教育", "Educational"),
    "debug-detective": ("Debug 侦探", "Debug Detective", "寻找代码中的 Bug 并修复", "教育", "Educational"),
    "regex-challenge": ("正则挑战", "Regex Challenge", "用正则表达式破解谜题挑战", "教育", "Educational"),
    "sql-defender": ("SQL 守卫", "SQL Defender", "编写SQL语句抵御注入攻击", "教育", "Educational"),
    "api-speedrunner": ("API 速通", "API Speedrunner", "速度挑战，用最快速度完成任务", "动作", "Action"),
    "merge-conflict": ("合并冲突", "Merge Conflict", "解决Git冲突，拯救代码仓库", "益智", "Puzzle"),
    "pipeline-puzzle": ("流水线解谜", "Pipeline Puzzle", "CI/CD流水线拼图，畅通部署", "益智", "Puzzle"),
    "status-memory": ("状态翻翻乐", "Status Memory", "匹配API状态码的记忆力游戏", "益智", "Puzzle"),
    "http-archer": ("HTTP 弓箭手", "HTTP Archer", "HTTP状态码是弓箭，精准命中", "动作", "Action"),
    "api-clicker": ("API 点击器", "API Clicker", "疯狂点击调用API，赚钱升级！", "放置", "Idle"),
    "api-towerdefense": ("API 塔防", "API Tower Defense", "搭建防御塔，抵御数据洪流", "策略", "Strategy"),
    "api-snake": ("API 贪吃蛇", "API Snake", "经典贪吃蛇，API数据驱动版", "街机", "Arcade"),
    "firebase-arena": ("Firebase 竞技场", "Firebase Arena", "实时数据库PK，数据即战力", "动作", "Action"),
    "netlify-portal": ("Netlify 传送门", "Netlify Portal", "部署站点争夺战，域名即领地", "模拟", "Simulation"),
    "baserow-racer": ("Baserow 赛车", "Baserow Racer", "数据库表格竞速，SQL查询加速", "竞速", "Racing"),
    "commit-racer": ("Commit 竞速赛", "Commit Racer", "Git提交次数决定你的车速！", "竞速", "Racing"),
    "build-battle": ("Build Battle", "Build Battle", "CI/CD构建竞速，谁先通过？", "动作", "Action"),
    "data-miner": ("数据矿工", "Data Miner", "挖掘数据集，发现隐藏价值", "模拟", "Simulation"),
    "territory": ("领土战争", "Territory War", "争夺领地，扩张版图，策略征服", "策略", "Strategy"),
    "cards": ("卡牌对战", "Card Battle", "策略卡牌对战，收集与组合制胜", "卡牌", "Card"),
    "pet": ("电子宠物", "Virtual Pet", "喂养、互动、进化你的虚拟伙伴", "模拟", "Simulation"),
    "achievements": ("成就系统", "Achievement System", "解锁全成就，展示你的游戏实力", "模拟", "Simulation"),
    "star-hunter": ("星际猎手", "Star Hunter", "在代码星空下收集闪亮的星星", "动作", "Action"),
    "guess": ("猜谜挑战", "Guess Challenge", "API驱动的知识谜题，边玩边学", "教育", "Educational"),
}


def get_game_meta(filename):
    """根据文件名获取游戏元数据"""
    name = filename.replace('.html', '')
    if name in GAME_META:
        cn, en, desc, cat_cn, cat_en = GAME_META[name]
        return cn, en, desc, cat_cn, cat_en
    
    # 自动生成：用文件名
    display = name.replace('-', ' ').title()
    return display, display, f"{display} — 免费H5在线小游戏", "其他", "Other"


def gh_api(method, path, body=None):
    """Maton API Gateway → GitHub"""
    url = f"{MATON_BASE}/github{path}"
    headers = {"Authorization": f"Bearer {MATON_API_KEY}"}
    if body:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
    else:
        req = urllib.request.Request(url, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode()}


def build_seo_block(filename):
    """为游戏页面构建 SEO 元数据块"""
    name = filename.replace('.html', '')
    cn_name, en_name, desc, cat_cn, cat_en = get_game_meta(filename)
    url = f"{BASE_URL}/{filename}"
    
    return f'''<title>🎮 {cn_name} - 灵犀游戏大厅 | 免费H5在线小游戏</title>
<meta name="description" content="{desc} 灵犀游戏大厅 {len(GAME_META)}+ 款免费H5游戏合集之一，即点即玩，无需下载。">
<meta name="keywords" content="{cn_name},{en_name},H5游戏,免费游戏,在线游戏,{cat_cn}游戏,灵犀游戏大厅">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="🎮 {cn_name} - 灵犀游戏大厅">
<meta property="og:description" content="{desc} 免费H5在线游戏，即点即玩。">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="灵犀游戏大厅">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="🎮 {cn_name} - 灵犀游戏大厅">
<meta name="twitter:description" content="{desc} 免费H5在线游戏，即点即玩。">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "{cn_name}",
  "alternateName": "{en_name}",
  "description": "{desc}",
  "url": "{url}",
  "playMode": "SinglePlayer",
  "applicationCategory": "GameApplication",
  "genre": "{cat_en}",
  "inLanguage": "zh-CN",
  "isAccessibleForFree": true,
  "isFamilyFriendly": true,
  "publisher": {{"@type": "Person", "name": "灵犀"}},
  "operatingSystem": "Web Browser",
  "datePublished": "2026-05-06",
  "dateModified": "{datetime.now().strftime('%Y-%m-%d')}"
}}
</script>'''


def inject_seo_to_html(content, filename):
    """向 HTML 内容注入 SEO 元数据（智能补全，不覆盖已有）"""
    # 检查各项是否已存在
    has_full_og = 'og:title' in content and 'og:description' in content and 'og:url' in content
    has_full_twitter = 'twitter:card' in content
    has_canonical = 'canonical' in content
    has_jsonld = 'application/ld+json' in content
    has_keywords = 'name="keywords"' in content
    has_desc = 'name="description"' in content
    
    if has_full_og and has_full_twitter and has_canonical and has_jsonld:
        return None  # 已完备，无需修改
    
    # 构建需要注入的标签
    seo_block = build_seo_block(filename)
    
    # 策略：在 <head> 内部、现有 <title> 之前注入，或替换不完整的 SEO
    # 如果已有 <title>，替换它
    if '<title>' in content:
        # 替换整个 <title>...</title>
        content = re.sub(r'<title>.*?</title>', re.search(r'<title>.*?</title>', seo_block).group(0), content, count=1)
    
    # 在 </head> 之前注入缺失的标签
    tags_to_inject = seo_block.split('\n')
    # 去掉 title（已处理）和 script（JSON-LD 特殊处理）
    tags_to_inject = [t for t in tags_to_inject if '<title>' not in t and 'ld+json' not in t]
    tags_to_inject = '\n'.join(tags_to_inject)
    
    if '</head>' in content:
        if not has_canonical:
            content = content.replace('</head>', f'<link rel="canonical" href="{BASE_URL}/{filename}">\n</head>', 1)
        if not has_desc:
            # Inject description after charset/viewport
            desc_line = [t for t in seo_block.split('\n') if 'name="description"' in t][0]
            # Find viewport meta and insert after it
            vp_match = re.search(r'<meta name="viewport"[^>]*>', content)
            if vp_match:
                pos = vp_match.end()
                content = content[:pos] + '\n' + desc_line + content[pos:]
        if not has_full_og:
            og_lines = [t for t in seo_block.split('\n') if 'og:' in t and '<meta property' in t]
            inj = '\n'.join(og_lines)
            if '</head>' in content:
                content = content.replace('</head>', f'<!-- Open Graph -->\n{inj}\n</head>', 1)
        if not has_full_twitter:
            tw_lines = [t for t in seo_block.split('\n') if 'twitter:' in t and '<meta name' in t]
            inj = '\n'.join(tw_lines)
            if '</head>' in content:
                content = content.replace('</head>', f'<!-- Twitter Cards -->\n{inj}\n</head>', 1)
        if not has_jsonld and 'ld+json' in seo_block:
            jsonld_match = re.search(r'<script type="application/ld\+json">.*?</script>', seo_block, re.DOTALL)
            if jsonld_match:
                content = content.replace('</head>', f'<!-- Structured Data -->\n{jsonld_match.group(0)}\n</head>', 1)
    
    # 最后处理：确保 browser-suggested 的 viewport 在 title 之前
    return content


def cmd_dry_run():
    """预览模式：显示哪些文件需要SEO强化"""
    print("🔍 游戏子页面 SEO 分析（dry-run）\n")
    
    all_files = gh_api("GET", f"/repos/{REPO_PATH}/contents/")
    if "error" in all_files:
        print(f"❌ 无法获取文件列表: {all_files.get('message')}")
        return
    
    html_files = [f for f in all_files if f['name'].endswith('.html') and f['name'] != 'index.html']
    
    need_seo = []
    has_full_seo = []
    
    for f in sorted(html_files, key=lambda x: x['name']):
        fname = f['name']
        file_data = gh_api("GET", f"/repos/{REPO_PATH}/contents/{fname}")
        
        if "_decoded" not in file_data:
            file_data["_decoded"] = base64.b64decode(file_data["content"]).decode("utf-8")
        
        content = file_data["_decoded"]
        
        checks = {
            "title": '<title>' in content,
            "description": 'name="description"' in content,
            "canonical": 'canonical' in content,
            "og": 'og:title' in content and 'og:description' in content,
            "twitter": 'twitter:card' in content,
            "jsonld": 'application/ld+json' in content,
        }
        
        score = sum(checks.values())
        
        if score < 6:
            cn, _, _, _, _ = get_game_meta(fname)
            need_seo.append((fname, cn, score, checks))
        else:
            has_full_seo.append(fname)
    
    print(f"✅ 已完备 ({len(has_full_seo)}/{len(html_files)} 游戏)")
    print(f"⚠️ 需强化 ({len(need_seo)}/{len(html_files)} 游戏):\n")
    
    for fname, cn, score, checks in sorted(need_seo, key=lambda x: x[2]):
        missing = [k for k, v in checks.items() if not v]
        print(f"  [{score}/6] {fname:30s} {cn:15s} 缺失: {', '.join(missing)}")
    
    total_score = sum(3 for _, _, s, _ in need_seo for _ in [s]) + len(has_full_seo) * 6
    max_score = len(html_files) * 6
    pct = total_score / max_score * 100 if max_score else 0
    print(f"\n📊 总体评分: {total_score}/{max_score} ({pct:.0f}%)")


def cmd_inject():
    """注入 SEO 到本地文件（需要 GitHub 下载 → 注入 → 保存）"""
    print("💉 批量注入 SEO 元数据...\n")
    
    all_files = gh_api("GET", f"/repos/{REPO_PATH}/contents/")
    if "error" in all_files:
        print(f"❌ 无法获取文件列表: {all_files.get('message')}")
        return
    
    html_files = [f for f in all_files if f['name'].endswith('.html') and f['name'] != 'index.html']
    
    output_dir = "/tmp/seo_games"
    os.makedirs(output_dir, exist_ok=True)
    
    modified = 0
    for i, f in enumerate(html_files):
        fname = f['name']
        file_data = gh_api("GET", f"/repos/{REPO_PATH}/contents/{fname}")
        
        if "_decoded" not in file_data:
            content = base64.b64decode(file_data["content"]).decode("utf-8")
        else:
            content = file_data["_decoded"]
        
        new_content = inject_seo_to_html(content, fname)
        
        if new_content:
            with open(f"{output_dir}/{fname}", 'w', encoding='utf-8') as out:
                out.write(new_content)
            modified += 1
            cn, _, _, _, _ = get_game_meta(fname)
            print(f"  [{i+1}/{len(html_files)}] ✅ {fname:30s} {cn}")
        else:
            # Already complete
            pass
    
    print(f"\n📂 已保存到 {output_dir}/ (共 {modified} 个文件)")
    print(f"   下一步: python3 inject_seo.py upload")


def cmd_upload():
    """上传本地注入 SEO 后的文件到 GitHub"""
    print("📤 上传 SEO 注入结果到 GitHub...\n")
    
    output_dir = "/tmp/seo_games"
    if not os.path.exists(output_dir):
        print("❌ 请先运行 inject 命令生成文件")
        return
    
    html_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.html')])
    
    uploaded = 0
    for fname in html_files:
        with open(f"{output_dir}/{fname}", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get current SHA from GitHub
        file_data = gh_api("GET", f"/repos/{REPO_PATH}/contents/{fname}")
        sha = file_data.get("sha")
        
        if not sha:
            print(f"  ❌ {fname}: 无法获取 SHA")
            continue
        
        result = gh_api("PUT", f"/repos/{REPO_PATH}/contents/{fname}", body={
            "message": f"SEO: 增强游戏页面元数据/OG/Twitter/JSON-LD ({fname})",
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "sha": sha,
            "branch": "main"
        })
        
        if "error" in result:
            print(f"  ❌ {fname}: {result.get('message', '')}")
        else:
            uploaded += 1
            cn, _, _, _, _ = get_game_meta(fname)
            print(f"  [{uploaded}/{len(html_files)}] ✅ {fname:30s} {cn}")
    
    print(f"\n📊 已上传 {uploaded}/{len(html_files)} 个文件")
    print(f"   🌐 稍后访问查看: {BASE_URL}/")


def cmd_report():
    """生成 SEO 完备性报告"""
    print("📊 生成游戏子页面 SEO 完备性报告\n")
    
    all_files = gh_api("GET", f"/repos/{REPO_PATH}/contents/")
    if "error" in all_files:
        print(f"❌ {all_files.get('message')}")
        return
    
    html_files = sorted([f for f in all_files if f['name'].endswith('.html') and f['name'] != 'index.html'],
                       key=lambda x: x['name'])
    
    report_lines = [
        f"# 游戏子页面 SEO 完备性报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"总游戏数: {len(html_files)}",
        "",
        "| # | 文件 | 游戏名 | title | desc | canonical | OG | Twitter | JSON-LD | 评分 |",
        "|---|------|--------|-------|------|-----------|----|---------|--------|------|",
    ]
    
    total_score = 0
    for i, f in enumerate(html_files, 1):
        fname = f['name']
        file_data = gh_api("GET", f"/repos/{REPO_PATH}/contents/{fname}")
        content = base64.b64decode(file_data["content"]).decode("utf-8") if "_decoded" not in file_data else file_data["_decoded"]
        
        cn, _, _, _, _ = get_game_meta(fname)
        
        checks = {
            "title": '✅' if '<title>' in content else '❌',
            "desc": '✅' if 'name="description"' in content else '❌',
            "canonical": '✅' if 'canonical' in content else '❌',
            "og": '✅' if 'og:title' in content and 'og:description' in content else '❌',
            "twitter": '✅' if 'twitter:card' in content else '❌',
            "jsonld": '✅' if 'application/ld+json' in content else '❌',
        }
        
        score = sum(1 for v in checks.values() if v == '✅')
        total_score += score
        
        report_lines.append(
            f"| {i} | {fname} | {cn} | {checks['title']} | {checks['desc']} | {checks['canonical']} | {checks['og']} | {checks['twitter']} | {checks['jsonld']} | {score}/6 |"
        )
    
    max_score = len(html_files) * 6
    pct = total_score / max_score * 100 if max_score else 0
    report_lines.append(f"\n**总分: {total_score}/{max_score} ({pct:.0f}%)**")
    
    report = '\n'.join(report_lines)
    
    output = "/tmp/seo_report.md"
    with open(output, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n📄 报告已保存: {output}")


# ══════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════

COMMANDS = {
    "dry-run": cmd_dry_run,
    "inject": cmd_inject,
    "upload": cmd_upload,
    "report": cmd_report,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        for name, fn in COMMANDS.items():
            print(f"  {name:<10} {fn.__doc__}")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()