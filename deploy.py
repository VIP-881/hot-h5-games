#!/usr/bin/env python3
"""
🚀 灵犀游戏大厅 · 轻量级静态游戏部署自动化脚本
========================================================
纯 HTML/CSS/JS 游戏，GitHub Pages + Maton API Gateway 部署。

用法：
  python3 deploy.py sync      # 同步本地游戏到 GitHub（检测差异、上传变更）
  python3 deploy.py sitemap   # 重新生成 sitemap.xml（覆盖全部游戏 URL）
  python3 deploy.py verify    # 验证部署：主页 SEO、链接可达、sitemap 覆盖
  python3 deploy.py all       # 全部流程：sync → sitemap → verify
  python3 deploy.py diff      # 仅比较本地与 GitHub 文件差异（不执行操作）
  python3 deploy.py seo       # 检查主页 SEO/GEO 优化项完备性

依赖：
  - Python 3.6+
  - MATON_API_KEY 环境变量（或硬编码，部署用）
  - 网络访问 GitHub API（通过 Maton Gateway）

作者：灵犀 AI
日期：2026-09-17
"""

import os, sys, json, base64, hashlib, time, urllib.request, urllib.error
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
LOCAL_DIR = "/home/admin/.openclaw/canvas/games/maton-games"

# 游戏优先级分层（用于 sitemap）
GAME_PRIORITY = {
    "index.html": (1.0, "daily"),
    # 热门经典
    "2048.html": (0.9, "weekly"), "mines.html": (0.9, "weekly"),
    "breakout.html": (0.9, "weekly"), "flappy.html": (0.9, "weekly"),
    "sudoku.html": (0.9, "weekly"), "tetris.html": (0.9, "weekly"),
    "snake.html": (0.9, "weekly"), "pacman.html": (0.9, "weekly"),
    "pong.html": (0.9, "weekly"), "sokoban.html": (0.9, "weekly"),
    "bubbleshooter.html": (0.9, "weekly"), "suika.html": (0.9, "weekly"),
    # API 驱动 / 开发者主题
    "rpg.html": (0.9, "weekly"), "monopoly.html": (0.9, "weekly"),
    "code-typer.html": (0.9, "weekly"), "debug-detective.html": (0.9, "weekly"),
    "api-speedrunner.html": (0.9, "weekly"), "regex-challenge.html": (0.9, "weekly"),
    # 牌类/策略
    "blackjack.html": (0.9, "weekly"), "battleship.html": (0.9, "weekly"),
    "othello.html": (0.9, "weekly"), "chess.html": (0.9, "weekly"),
    # 中级游戏
    "dino.html": (0.8, "weekly"), "doodlejump.html": (0.8, "weekly"),
    "asteroids.html": (0.8, "weekly"), "invader.html": (0.8, "weekly"),
    "memory.html": (0.8, "weekly"), "match3.html": (0.8, "weekly"),
    "puzzle.html": (0.8, "weekly"), "jigsaw.html": (0.8, "weekly"),
    "hangman.html": (0.8, "weekly"), "connect4.html": (0.8, "weekly"),
    "battleship.html": (0.8, "weekly"), "word.html": (0.8, "weekly"),
}
DEFAULT_PRIORITY = (0.7, "monthly")

# SEO/GEO 检查项清单
SEO_CHECKS = [
    # (标签选择器, 描述)
    ("og:title", "Open Graph 标题"),
    ("og:description", "Open Graph 描述"),
    ("og:type", "Open Graph 类型"),
    ("og:url", "Open Graph URL"),
    ("og:image", "Open Graph 图片"),
    ("og:locale", "Open Graph 语言区域"),
    ("twitter:card", "Twitter Card 类型"),
    ("twitter:title", "Twitter 标题"),
    ("twitter:description", "Twitter 描述"),
    ("twitter:image", "Twitter 图片"),
    ("canonical", "Canonical URL 规范"),
    ("hreflang", "多语言标注 hreflang"),
    ("geo.region", "Geo 区域"),
    ("geo.placename", "Geo 地名"),
    ("geo.position", "Geo 精确坐标"),
    ("ICBM", "ICBM 坐标（旧式）"),
    ("DC.title", "Dublin Core 标题"),
    ("DC.description", "Dublin Core 描述"),
    ("DC.language", "Dublin Core 语言"),
    ("application/ld+json", "JSON-LD 结构化数据"),
    ("robots", "搜索引擎抓取规则"),
    ("description", "Meta 描述"),
    ("keywords", "Meta 关键词"),
    ("theme-color", "主题色"),
    ("manifest", "PWA Manifest"),
    ("sitemap", "Sitemap 引用"),
]


# ══════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════

def gh_api(method, path, body=None, decode_base64=False):
    """调用 Maton API Gateway → GitHub"""
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
        result = json.loads(resp.read())
        if decode_base64 and "content" in result and result.get("encoding") == "base64":
            result["_decoded"] = base64.b64decode(result["content"]).decode("utf-8")
        return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": e.code, "message": body}


def get_github_files():
    """获取 GitHub 仓库根目录所有文件"""
    result = gh_api("GET", f"/repos/{REPO_PATH}/contents/")
    if "error" in result:
        print(f"❌ 获取 GitHub 文件列表失败: {result}")
        return {}
    return {f["name"]: f for f in result if isinstance(f, dict)}


def get_local_files():
    """获取本地目录所有 HTML 文件"""
    local_path = Path(LOCAL_DIR)
    if not local_path.exists():
        return {}
    return {
        f.name: {"path": str(f), "size": f.stat().st_size, "mtime": f.stat().st_mtime}
        for f in local_path.iterdir() if f.suffix == ".html"
    }


def file_sha_local(path):
    """计算本地文件 SHA"""
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def upload_file(filename, content, sha, message):
    """上传文件到 GitHub（CREATE 或 UPDATE）"""
    body = {
        "message": message,
        "content": base64.b64encode(content.encode() if isinstance(content, str) else content).decode(),
        "branch": "main",
    }
    if sha:
        body["sha"] = sha
    return gh_api("PUT", f"/repos/{REPO_PATH}/contents/{filename}", body=body)


# ══════════════════════════════════════════════════════
# 命令实现
# ══════════════════════════════════════════════════════

def cmd_diff():
    """比较本地与 GitHub 文件差异"""
    print("🔍 比较本地 ↔ GitHub 文件差异\n")
    
    local = get_local_files()
    github = get_github_files()
    
    if not github:
        print("⚠️ GitHub 文件列表为空，请检查网络和认证")
        return
    
    new_files = []
    modified_files = []
    same_files = []
    only_github = []
    
    print(f"{'文件名':<30} {'本地 SHA':<16} {'GitHub SHA':<16} {'状态':<8}")
    print("-" * 72)
    
    for name, info in sorted(local.items()):
        local_sha = file_sha_local(info["path"])
        
        if name in github:
            gh_content = gh_api("GET", f"/repos/{REPO_PATH}/contents/{name}", decode_base64=True)
            if "_decoded" in gh_content:
                gh_sha = hashlib.sha1(gh_content["_decoded"].encode()).hexdigest()
            else:
                gh_sha = "N/A"
            
            if local_sha == gh_sha:
                status = "相同"
                same_files.append(name)
            else:
                status = "⬆ 变更"
                modified_files.append((name, local_sha, gh_sha))
        else:
            status = "🆕 新增"
            new_files.append(name)
            gh_sha = "—"
        
        print(f"{name:<30} {local_sha[:14]:<16} {gh_sha[:14] if gh_sha else '—':<16} {status:<8}")
    
    # 仅 GitHub 有的文件
    only_github = [n for n in github if n.endswith(".html") and n not in local]
    
    print(f"\n📊 统计：")
    print(f"  本地 HTML 文件：{len(local)}")
    print(f"  GitHub HTML 文件：{sum(1 for n in github if n.endswith('.html'))}")
    print(f"  ✅ 相同：{len(same_files)}")
    print(f"  ⬆️ 有变更：{len(modified_files)}")
    print(f"  🆕 仅本地（需上传）：{len(new_files)}")
    print(f"  📦 仅 GitHub（本地无）：{len(only_github)}")
    
    if new_files:
        print(f"\n📂 待上传新文件：{', '.join(new_files)}")
    if modified_files:
        print(f"\n🔄 待更新文件：{', '.join(n for n, _, _ in modified_files)}")


def cmd_sync():
    """同步本地变更到 GitHub"""
    print("🔄 同步本地游戏到 GitHub...\n")
    
    local = get_local_files()
    github = get_github_files()
    
    uploaded = 0
    skipped = 0
    failed = 0
    
    for name, info in sorted(local.items()):
        local_sha = file_sha_local(info["path"])
        
        # 检查是否需要更新
        need_upload = False
        gh_sha = None
        
        if name not in github:
            need_upload = True
            print(f"  🆕 {name} — 新文件", end="")
        else:
            gh_file = gh_api("GET", f"/repos/{REPO_PATH}/contents/{name}", decode_base64=True)
            if "_decoded" in gh_file:
                gh_sha_hash = hashlib.sha1(gh_file["_decoded"].encode()).hexdigest()
                gh_sha = gh_file.get("sha")
                if local_sha != gh_sha_hash:
                    need_upload = True
                    delta = info["size"] - gh_file.get("size", 0)
                    sign = "+" if delta >= 0 else ""
                    verbose_status = f"更新 ({sign}{delta} bytes)"
                    print(f"  ⬆️ {name} — {verbose_status}", end="")
                else:
                    skipped += 1
                    continue
        
        if need_upload:
            with open(info["path"], "rb") as f:
                content = f.read()
            size_kb = len(content) / 1024
            result = upload_file(name, content, gh_sha,
                               f"deploy: 更新 {name} ({size_kb:.1f}KB) via deploy.py")
            if "error" in result:
                print(f" ❌ 失败: {result.get('message', '')}")
                failed += 1
            else:
                print(f" ✅ ({size_kb:.1f}KB)")
                uploaded += 1
    
    print(f"\n📊 同步完成：上传 {uploaded} | 跳过 {skipped} | 失败 {failed}")


def cmd_sitemap():
    """重新生成 sitemap.xml"""
    print("🗺️ 生成 sitemap.xml...")
    
    github = get_github_files()
    html_files = sorted([f for f in github if f.endswith(".html") and f != "index.html"])
    
    # 先在头部加 index.html
    urls = []
    urls.append(("index.html", 1.0, "daily"))
    for fname in html_files:
        priority, freq = GAME_PRIORITY.get(fname, DEFAULT_PRIORITY)
        urls.append((fname, priority, freq))
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    sitemap += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    
    for fname, priority, freq in urls:
        url_name = "" if fname == "index.html" else fname
        sitemap += f"  <url>\n"
        sitemap += f"    <loc>{BASE_URL}/{url_name}</loc>\n"
        sitemap += f"    <changefreq>{freq}</changefreq>\n"
        sitemap += f"    <priority>{priority}</priority>\n"
        sitemap += f"  </url>\n"
    
    sitemap += "</urlset>"
    
    # 获取当前 sitemap SHA
    current = gh_api("GET", f"/repos/{REPO_PATH}/contents/sitemap.xml")
    sha = current.get("sha")
    
    result = upload_file("sitemap.xml", sitemap, sha,
                        f"SEO: 更新 sitemap.xml ({len(urls)} 个 URL)")
    
    if "error" in result:
        print(f"❌ 上传失败: {result.get('message', '')}")
    else:
        print(f"✅ sitemap.xml 已更新 ({len(urls)} 个 URL, {len(sitemap)} 字符)")
        print(f"   URL: {result['content']['html_url']}")


def cmd_verify():
    """验证部署状态"""
    print("🔬 验证部署...\n")
    
    # 1. 主页可访问性
    print("1️⃣ 主页可访问性")
    try:
        req = urllib.request.Request(BASE_URL + "/")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; deploy-bot)")
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode()
        print(f"   ✅ HTTP {resp.getcode()} — {len(html)} 字符")
    except Exception as e:
        print(f"   ❌ 无法访问: {e}")
        return
    
    # 2. SEO/GEO 检查
    print("\n2️⃣ SEO/GEO 标签检查")
    all_ok = True
    for tag, desc in SEO_CHECKS:
        count = html.count(tag)
        if "ld+json" in tag:
            count = html.count('"@type"')
        if count > 0:
            print(f"   ✅ {desc} ({tag})")
        else:
            print(f"   ⚠️ 缺失: {desc} ({tag})")
            all_ok = False
    
    # 3. 游戏链接抽样
    print("\n3️⃣ 游戏链接抽样检查")
    import random
    game_links = []
    for line in html.split("\n"):
        if '.html"' in line and 'href=' in line and 'github.io' not in line:
            import re
            m = re.search(r'href="([^"]+\.html)"', line)
            if m and m.group(1) not in ['manifest.json']:
                game_links.append(m.group(1))
    
    game_links = list(set(game_links))[:10]
    for link in game_links:
        try:
            url = BASE_URL + "/" + link if not link.startswith("http") else link
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0")
            resp = urllib.request.urlopen(req, timeout=5)
            print(f"   ✅ {link} → HTTP {resp.getcode()}")
        except Exception as e:
            print(f"   ❌ {link} → {e}")
    
    # 4. Sitemap 覆盖
    print("\n4️⃣ Sitemap 覆盖检查")
    try:
        req = urllib.request.Request(BASE_URL + "/sitemap.xml")
        req.add_header("User-Agent", "Mozilla/5.0")
        resp = urllib.request.urlopen(req, timeout=5)
        sitemap_content = resp.read().decode()
        url_count = sitemap_content.count("<url>")
        print(f"   ✅ sitemap.xml 可访问 — {url_count} 个 <url>")
    except Exception as e:
        print(f"   ❌ sitemap.xml 不可访问: {e}")
    
    # 5. robots.txt
    print("\n5️⃣ robots.txt 检查")
    try:
        req = urllib.request.Request(BASE_URL + "/robots.txt")
        req.add_header("User-Agent", "Mozilla/5.0")
        resp = urllib.request.urlopen(req, timeout=5)
        robots = resp.read().decode()
        has_sitemap = "Sitemap:" in robots
        has_allow = "Allow:" in robots or "Disallow:" in robots
        print(f"   {'✅' if has_sitemap else '⚠️'} Sitemap 引用{' 存在' if has_sitemap else ' 缺失'}")
        print(f"   {'✅' if has_allow else '⚠️'} 抓取规则{' 存在' if has_allow else ' 缺失'}")
    except Exception as e:
        print(f"   ❌ robots.txt 不可访问: {e}")
    
    # 6. GitHub Pages 状态
    print("\n6️⃣ GitHub Pages 部署状态")
    pages = gh_api("GET", f"/repos/{REPO_PATH}/pages")
    if "error" not in pages:
        print(f"   状态: {pages.get('status', 'N/A')}")
        print(f"   在线地址: {pages.get('html_url', 'N/A')}")
        print(f"   HTTPS: {'已强制' if pages.get('https_enforced') else '未强制'}")
    
    print(f"\n{'✅ 全部验证通过！' if all_ok else '⚠️ 存在优化项，请检查上述 ⚠️ 标记'}")


def cmd_seo():
    """SEO/GEO 优化检查"""
    print("🔍 主页 SEO/GEO 优化完备性检查\n")
    
    try:
        req = urllib.request.Request(BASE_URL + "/")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; seo-bot)")
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode()
    except Exception as e:
        print(f"❌ 无法访问主页: {e}")
        return
    
    score = 0
    max_score = 0
    
    sections = {
        "基础 Meta": ["description", "keywords", "robots", "viewport", "charset", "theme-color", "author"],
        "Open Graph": ["og:title", "og:description", "og:type", "og:url", "og:image", "og:locale"],
        "Twitter Cards": ["twitter:card", "twitter:title", "twitter:description", "twitter:image"],
        "GEO 定位": ["geo.region", "geo.placename", "geo.position", "ICBM"],
        "Dublin Core": ["DC.title", "DC.description", "DC.language"],
        "多语言": ["hreflang"],
        "结构化数据": ['"@type"'],
        "Canonical": ["canonical"],
        "PWA": ["manifest"],
    }
    
    for section, tags in sections.items():
        print(f"\n📂 {section}")
        for tag in tags:
            max_score += 1
            if tag in html:
                count = html.count(tag)
                print(f"   ✅ {tag} ({count} 处)")
                score += 1
            else:
                print(f"   ❌ {tag} 缺失")
    
    pct = (score / max_score * 100) if max_score else 0
    grade = "🏆 A+" if pct >= 95 else "✅ A" if pct >= 85 else "⚠️ B" if pct >= 70 else "❌ C"
    print(f"\n{'─'*50}")
    print(f"  SEO/GEO 评分: {score}/{max_score} ({pct:.0f}%) {grade}")


def cmd_all():
    """完整部署流程"""
    print("=" * 60)
    print("🚀 灵犀游戏大厅 · 完整部署")
    print(f"   时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    steps = [
        ("同步本地文件", cmd_sync),
        ("更新 Sitemap", cmd_sitemap),
        ("验证部署", cmd_verify),
    ]
    
    for i, (name, func) in enumerate(steps, 1):
        print(f"\n{'─'*40}")
        print(f"📌 步骤 {i}/{len(steps)}: {name}")
        print(f"{'─'*40}")
        try:
            func()
        except Exception as e:
            print(f"❌ 步骤失败: {e}")
            return
    
    print(f"\n{'='*60}")
    print("🎉 部署完成！")
    print(f"   🌐 {BASE_URL}/")
    print(f"   📦 https://github.com/{REPO_PATH}")
    print(f"{'='*60}")


# ══════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════

COMMANDS = {
    "diff": cmd_diff,
    "sync": cmd_sync,
    "sitemap": cmd_sitemap,
    "verify": cmd_verify,
    "seo": cmd_seo,
    "all": cmd_all,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print("可用命令：")
        for name, fn in COMMANDS.items():
            print(f"  {name:<10} {fn.__doc__ or ''}")
        sys.exit(1)
    
    COMMANDS[sys.argv[1]]()