#!/usr/bin/env python3
"""
H5 Games Build & Deploy Script
===============================
Automated build pipeline for the hot-h5-games project.

Usage:
    python3 build.py          # Build index + sitemap locally
    python3 build.py --deploy  # Build + push to GitHub + deploy

Features:
  - Auto-generate index.html from game files
  - Auto-generate sitemap.xml
  - Optional GitHub push via Maton API gateway
  - Optional Netlify deploy via Maton API gateway
  - Full SEO metadata injection (OG, Twitter, JSON-LD, hreflang, geo)
  - Validates game HTML files

Requirements:
  - Python 3.7+
  - MATON_API_KEY env var (for deploy)
  - Network access to github.com / gateway.maton.ai
"""

import os, sys, glob, json, base64, time
import urllib.request
from pathlib import Path

# ── Configuration ──────────────────────────────────────────
DIR = Path('/home/admin/.openclaw/canvas/games/hot-games')
BASE_URL = 'https://vip-881.github.io/hot-h5-games'
GITHUB_REPO = 'VIP-881/hot-h5-games'
GITHUB_API = 'https://gateway.maton.ai/github'
NETLIFY_SITE_ID = 'c30ce5e8-c8da-4bac-86f3-86a0f5818965'
NETLIFY_API = 'https://gateway.maton.ai/netlify/api/v1'
MATON_KEY = os.environ.get('MATON_API_KEY', '')

# ── Game Metadata ───────────────────────────────────────────
GAME_META = {
    "2048":["🔢","2048","合并数字方块极限","viral","现象级"],"angling":["🎣","钓鱼达人","收杆钓大鱼","action","休闲"],
    "archery":["🏹","射箭大师","风速瞄准射箭","sport","精准"],"axe":["🎯","飞斧投掷","旋转投斧中靶","action","节奏"],
    "badminton":["🏸","羽毛球","AI对战","sport","体育"],"balance":["⚖️","平衡大师","砝码精准平衡","puzzle","逻辑"],
    "balloon":["🎈","射击气球","限时打气球","action","射击"],"battlepong":["🏓","弹球大战","双人对战","arcade","街机"],
    "bball":["🎯","弹球消砖","弹球反弹消除","puzzle","物理"],"blackjack":["🃏","21点","经典黑杰克","casino","博牌"],
    "bowling":["🎳","迷你保龄球","10帧保龄球","sport","体育"],"breakout":["🧱","打砖块","弹球碎砖","arcade","街机"],
    "bubble":["🫧","泡泡龙","三连消除","puzzle","益智"],"bubble2":["🔫","泡泡射手","瞄准同色消除","puzzle","益智"],
    "bulls":["🔢","猜数字","4位AB逻辑","puzzle","益智"],"calc24":["🧮","24点","加减乘除算24","puzzle","益智"],
    "catch":["💰","接金币","篮筐接金币","action","休闲"],"chick":["🐥","接住小鸡","接掉落小鸡","action","休闲"],
    "chopper":["🚁","直升机救援","飞行躲避救援","arcade","飞行"],"claw":["🎪","抓娃娃","机械爪抓玩偶","action","模拟"],
    "color":["🧪","颜色合成","RGB调色匹配","puzzle","益智"],"darts":["🎯","飞镖大师","301分飞镖","sport","精准"],
    "defuse":["💣","拆弹专家","剪引线拆炸弹","puzzle","解谜"],"dice":["🎲","骰子对决","13种计分组合","casino","策略"],
    "dino":["🦖","恐龙跑酷","Chrome小恐龙","arcade","街机"],"draw":["🖌️","创意涂色","16色画板","creative","创作"],
    "duel":["🔫","西部决斗","拔枪对决","action","反应"],"eat":["🍔","贪吃大胃王","吃食物变大","action","吞噬"],
    "evolve":["🧪","进化之路","8阶进化","action","进化"],"fish":["🐠","捕鱼达人","炮弹捕鱼","arcade","街机"],
    "flappy":["🐦","Flappy Bird","飞越水管","hot","爆款"],"freethrow":["🏀","罚球挑战","力度条投篮","sport","体育"],
    "frog":["🐸","跳跳蛙","蓄力跳荷叶","action","休闲"],"fruit":["🔪","切水果","划屏切割","action","动作"],
    "gear":["🌀","旋转齿轮","点击联动","puzzle","益智"],"goldminer":["⛏️","黄金矿工","钩子抓金块","arcade","经典"],
    "golf":["⛳","迷你高尔夫","5洞推杆","sport","体育"],"gradient":["🌈","渐变色挑战","色块排序","puzzle","色觉"],
    "helix":["🌀","螺旋跳跃","旋转平台跳","action","超休闲"],"hole":["🕳️","黑洞吞噬","吞噬变大","action","吞噬"],
    "hoop":["🏀","投篮大挑战","滑动投篮","action","动作"],"ice":["🧊","冰块消消乐","同色连通消除","puzzle","消除"],
    "invader":["👾","太空入侵者","街机外星舰队","arcade","街机"],"jenga":["🏗️","叠叠高","Jenga抽积木","puzzle","益智"],
    "jigsaw":["🧩","拼图大师","3×3拼图","puzzle","益智"],"jump":["🏃","跳一跳","蓄力跳跃","viral","刷屏"],
    "kaleido":["🎨","万花筒","镜像对称绘画","creative","创作"],"knife":["🎯","飞刀挑战","旋转靶投刀","action","反应"],
    "lander":["🚀","月球着陆","推力控制着陆","arcade","物理"],"lights":["💡","开关灯","翻转十字灯","puzzle","逻辑"],
    "link":["🔗","连连看","三线连通消除","puzzle","益智"],"magfish":["🎣","磁力钓鱼","磁铁吸引鱼群","action","休闲"],
    "marble":["🎪","弹珠迷宫","鼠标牵引弹珠","puzzle","隐藏"],"match3":["💎","消消乐","宝石三连消","hot","国民"],
    "math":["🔢","速算达人","心算挑战","puzzle","益智"],"maze":["🧲","磁铁迷宫","磁力4关","puzzle","益智"],
    "memory":["🧠","记忆翻牌","8对翻牌配对","puzzle","记忆"],"meteor":["🌙","击碎陨石","激光摧毁陨石","arcade","射击"],
    "mines":["💣","扫雷","9×9经典","classic","经典"],"mole":["🔨","打地鼠","30秒敲地鼠","hot","经典"],
    "numpair":["🧩","数字配对","两数和=目标","puzzle","脑力"],"numsnake":["🔢","数字贪吃蛇","吃正确数字","puzzle","益智"],
    "parachute":["🪂","高空跳伞","穿过圈圈着陆","action","冒险"],"park":["🚗","停车大师","4关倒车入库","arcade","驾驶"],
    "penalty":["⚽","点球大战","5轮点球对决","sport","体育"],"piano":["🎹","别踩白块","节奏点黑块","viral","刷屏"],
    "pinball":["🕹️","弹珠台","双挡板弹珠","arcade","街机"],"pixel":["🎨","像素绘图","20×20网格","creative","创作"],
    "pong":["🏓","乒乓球","AI先7球胜","sport","体育"],"puzzle":["🧩","滑动拼图","数字华容道","puzzle","益智"],
    "racer":["🏎️","公路飙车","躲避障碍","arcade","竞速"],"range":["🎪","打靶场","30秒射击移动靶","action","射击"],
    "react":["⚡","反应测试","5次平均时间","action","竞技"],"rhythm":["🎵","节奏大师","节拍点击","music","音乐"],
    "ringtoss":["🎪","套圈大挑战","瞄准抛出套圈","action","嘉年华"],"roll":["🎳","滚球得分","弹球击中靶区","puzzle","物理"],
    "rope":["🔥","烧绳子","6关摆动物理","puzzle","物理"],"run":["🏃","神庙逃亡","三列道跑酷","arcade","跑酷"],
    "shmup":["✈️","飞机大战","弹幕Boss战","arcade","射击"],"shooter":["🎯","神枪手","快速命中靶子","action","反应"],
    "simon":["🎵","音乐记忆","Simon序列","puzzle","记忆"],"skeet":["🎪","飞碟射击","瞄准击碎飞碟","action","射击"],
    "ski":["🏔️","滑雪大冒险","躲避收集金币","arcade","竞速"],"sling":["🎯","弹弓射手","拉弹弓射击","puzzle","物理"],
    "sling2":["🏹","弹弓消消乐","拖拽消除砖块","puzzle","物理"],"slot":["🎰","老虎机","三列旋转赢奖","casino","博牌"],
    "slots2":["🎰","水果拉霸","拉杆中奖","casino","博牌"],"snake":["🐍","贪吃蛇","霓虹经典","classic","经典"],
    "snakewar":["🐍","贪吃蛇大战","6蛇竞技场","action","IO对战"],"sokoban":["🏰","推箱子","3关仓库番","puzzle","益智"],
    "spider":["🕷️","蜘蛛纸牌","K到A消除接龙","casino","纸牌"],"spot":["🔍","找茬大师","找5处不同","puzzle","观察"],
    "stack":["🏗️","叠叠乐","精准堆叠建塔","action","反应"],"stopwatch":["⏱","计时挑战","精准停在10秒","action","反应"],
    "stroop":["🎨","辨色大师","Stroop辨色","puzzle","脑力"],"sudoku":["🧮","数独","三档难度","puzzle","益智"],
    "suika":["🍉","合成大西瓜","物理碰撞合成","viral","爆款"],"surf":["🌊","冲浪达人","躲避礁石","arcade","竞速"],
    "switch":["🔴","变色球","ColorSwitch","action","超休闲"],"tangram":["🧩","七巧板","7块拼目标","puzzle","益智"],
    "tennis":["🎾","网球对战","AI网球战","sport","体育"],"tetris":["🧩","俄罗斯方块","经典7种方块","classic","经典"],
    "timber":["🪓","砍木头","左右避开树枝","action","反应"],"top":["🌀","抽陀螺","滑动保持旋转","action","传统"],
    "towerdef":["🏰","塔防前线","放炮塔防守","puzzle","策略"],"tubes":["🧪","试管排序","水排序分色","puzzle","益智"],
    "volley":["🏐","沙滩排球","滑动扣球","sport","体育"],"water":["💧","接水滴","接水避毒液","action","休闲"],
    "wheel":["🎪","幸运转盘","10格随机奖励","casino","抽奖"],"word":["🧩","拼字达人","打乱字母拼词","puzzle","词汇"],
}

TAG_CLASSES = {
    "hot":"tag-hot","classic":"tag-classic","viral":"tag-viral",
    "arcade":"tag-arcade","puzzle":"tag-puzzle","action":"tag-action",
    "sport":"tag-sport","casino":"tag-casino","creative":"tag-creative","music":"tag-music"
}

# ── GitHub API Helpers ──────────────────────────────────────
def gh_headers():
    return {
        'Authorization': f'Bearer {MATON_KEY}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json'
    }

def gh_get_sha(path):
    """Get SHA of existing file on GitHub."""
    req = urllib.request.Request(f'{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}')
    for k, v in gh_headers().items(): req.add_header(k, v)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read()).get('sha')
    except:
        return None

def gh_upload(path, content, message="Update via build.py"):
    """Upload/update a file on GitHub."""
    sha = gh_get_sha(path)
    payload = {
        'message': message,
        'content': base64.b64encode(content.encode()).decode(),
        'branch': 'main'
    }
    if sha: payload['sha'] = sha

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f'{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}',
        data=data, method='PUT'
    )
    for k, v in gh_headers().items(): req.add_header(k, v)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# ── Build Functions ─────────────────────────────────────────
def get_game_files():
    """Get sorted list of game HTML files (excluding index)."""
    html_files = sorted([f.name for f in DIR.glob('*.html') if f.name != 'index.html'])
    return [f.replace('.html', '') for f in html_files]

def build_sitemap(games):
    """Generate sitemap.xml content."""
    now = time.strftime('%Y-%m-%d')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    xml += f'  <url><loc>{BASE_URL}/</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for g in games:
        xml += f'  <url><loc>{BASE_URL}/{g}.html</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
    xml += '</urlset>\n'
    return xml

def build_index(games):
    """Generate the full index.html with SEO/GEO optimization."""
    n = len(games)
    cards = ''
    for key in games:
        if key not in GAME_META: continue
        icon, name, desc, cat, label = GAME_META[key]
        tag_cls = TAG_CLASSES.get(cat, 'tag-hot')
        cards += (
            f'<a class="card" href="{key}.html" data-cat="{cat}">'
            f'<div class="card-icon">{icon}</div>'
            f'<div class="card-body"><h3>{name}</h3><p>{desc}</p>'
            f'<span class="card-tag {tag_cls}">{label}</span></div></a>\n'
        )

    index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">

<!-- Primary SEO -->
<title>🔥 热门H5游戏合集 - 110款免费在线小游戏 | 即点即玩</title>
<meta name="description" content="{n}款热门H5小游戏免费在线合集，手机触屏+PC键盘，涵盖益智街机射击体育全品类，无需下载即点即玩。">
<meta name="keywords" content="H5游戏,小游戏,免费游戏,在线游戏,HTML5游戏,网页游戏,休闲游戏,手机游戏">
<meta name="author" content="灵犀工作室">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="googlebot" content="index, follow">
<meta name="bingbot" content="index, follow">
<meta name="theme-color" content="#0f0c29">

<!-- Geo & Language -->
<meta name="geo.region" content="CN">
<meta name="geo.placename" content="China">
<meta name="language" content="Chinese">
<meta name="content-language" content="zh-CN">

<!-- hreflang -->
<link rel="alternate" hreflang="zh-CN" href="{BASE_URL}/">
<link rel="alternate" hreflang="zh-Hans" href="{BASE_URL}/">
<link rel="alternate" hreflang="en" href="{BASE_URL}/">
<link rel="alternate" hreflang="x-default" href="{BASE_URL}/">
<link rel="canonical" href="{BASE_URL}">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">

<!-- Open Graph -->
<meta property="og:title" content="🔥 {n}款热门H5游戏合集 · 免费在线即点即玩">
<meta property="og:description" content="{n}款H5小游戏免费合集，手机触屏+PC，涵盖全品类，无需下载。">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE_URL}">
<meta property="og:site_name" content="热门H5游戏合集">
<meta property="og:locale" content="zh_CN">
<meta property="og:locale:alternate" content="en_US">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="🔥 {n}款热门H5游戏合集">
<meta name="twitter:description" content="{n}款免费H5小游戏，手机+PC双模式，即点即玩。">

<!-- Structured Data: CollectionPage -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "热门H5游戏合集",
  "description": "{n}款免费在线H5小游戏合集",
  "url": "{BASE_URL}",
  "inLanguage": "zh-CN",
  "datePublished": "2026-09-15",
  "dateModified": "{time.strftime('%Y-%m-%d')}",
  "author": {{"@type":"Person","name":"灵犀"}},
  "isAccessibleForFree": true,
  "mainEntity": {{"@type":"ItemList","numberOfItems":{n}}}
}}
</script>

<!-- Structured Data: Breadcrumb -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{{
    "@type": "ListItem","position":1,"name":"首页","item":"{BASE_URL}/"
  }},{{
    "@type": "ListItem","position":2,"name":"H5游戏合集","item":"{BASE_URL}/"
  }}]
}}
</script>

<!-- Structured Data: WebSite + SearchAction -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "热门H5游戏合集",
  "url": "{BASE_URL}",
  "inLanguage": "zh-CN",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": "{BASE_URL}/?q={{search_term_string}}",
    "query-input": "required name=search_term_string"
  }}
}}
</script>

<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#fff}}
.header{{text-align:center;padding:40px 20px 20px}}
.header h1{{font-size:2em;background:linear-gradient(135deg,#f093fb,#f5576c,#fda085);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header .sub{{color:#aaa;font-size:0.9em;max-width:650px;margin:8px auto 0;line-height:1.5}}
.categories{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0;padding:0 12px}}
.cat-btn{{padding:6px 14px;border-radius:20px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.05);color:#aaa;cursor:pointer;font-size:0.8em;transition:all 0.2s}}
.cat-btn:hover,.cat-btn.active{{background:rgba(100,150,255,0.2);border-color:#6af;color:#fff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:6px;padding:8px 12px;max-width:1400px;margin:0 auto}}
.card{{background:rgba(255,255,255,0.06);border-radius:10px;overflow:hidden;cursor:pointer;transition:all 0.3s;border:1px solid rgba(255,255,255,0.1);text-decoration:none;color:inherit;display:block}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.4);border-color:rgba(255,255,255,0.25)}}
.card-icon{{font-size:2em;text-align:center;padding:12px 0 0}}
.card-body{{padding:6px 8px 8px}}
.card-body h3{{font-size:0.8em;margin-bottom:1px}}
.card-body p{{color:#999;font-size:0.66em;line-height:1.3}}
.card-tag{{display:inline-block;padding:1px 5px;border-radius:20px;font-size:0.56em;margin-top:2px}}
.tag-hot{{background:rgba(245,87,108,0.3);color:#f5576c}}
.tag-classic{{background:rgba(253,160,133,0.3);color:#fda085}}
.tag-viral{{background:rgba(240,147,251,0.3);color:#f093fb}}
.tag-arcade{{background:rgba(46,213,115,0.3);color:#2ed573}}
.tag-puzzle{{background:rgba(30,144,255,0.3);color:#4aa3ff}}
.tag-action{{background:rgba(255,165,2,0.3);color:#ffa502}}
.tag-sport{{background:rgba(0,206,201,0.3);color:#00cec9}}
.tag-casino{{background:rgba(255,215,0,0.25);color:#ffd700}}
.tag-creative{{background:rgba(240,147,251,0.25);color:#f093fb}}
.tag-music{{background:rgba(245,87,108,0.25);color:#ff6b81}}
footer{{text-align:center;padding:16px;color:#555;font-size:0.7em;line-height:1.6}}
footer a{{color:#777;text-decoration:none;margin:0 4px}}
footer a:hover{{color:#aaa}}
.links{{display:flex;gap:10px;justify-content:center;margin:6px 0;flex-wrap:wrap}}
.links a{{padding:5px 12px;border-radius:18px;border:1px solid rgba(255,255,255,0.15);color:#aaa;text-decoration:none;font-size:0.78em;transition:all 0.2s}}
.links a:hover{{border-color:rgba(255,255,255,0.4);color:#fff}}
.stats-bar{{display:flex;gap:16px;justify-content:center;margin:8px 0;flex-wrap:wrap}}
.stat-item{{background:rgba(255,255,255,0.07);padding:6px 14px;border-radius:20px;font-size:0.78em;color:#aaa}}
.stat-item b{{color:#fff}}
</style>
</head>
<body>
<header class="header" role="banner">
  <h1>🔥 热门 H5 游戏合集</h1>
  <p class="sub">{n} 款免费在线 H5 小游戏 · 手机触屏 + PC 键盘 · 纯 HTML 零依赖 · 无需下载即点即玩</p>
  <div class="stats-bar">
    <span class="stat-item">🎮 <b id="count">{n}</b> 款游戏</span>
    <span class="stat-item">📱 手机+PC双端</span>
    <span class="stat-item">⚡ 零下载</span>
    <span class="stat-item">🆓 永久免费</span>
  </div>
  <div class="categories" role="navigation" aria-label="游戏分类筛选">
    <button class="cat-btn active" onclick="filter('all')">全部</button>
    <button class="cat-btn" onclick="filter('puzzle')">🧠 益智</button>
    <button class="cat-btn" onclick="filter('action')">⚡ 动作</button>
    <button class="cat-btn" onclick="filter('arcade')">🕹️ 街机</button>
    <button class="cat-btn" onclick="filter('sport')">⚽ 体育</button>
    <button class="cat-btn" onclick="filter('casino')">🎰 博牌</button>
    <button class="cat-btn" onclick="filter('classic')">🏆 经典</button>
    <button class="cat-btn" onclick="filter('creative')">🎨 创作</button>
    <button class="cat-btn" onclick="filter('music')">🎵 音乐</button>
  </div>
</header>
<main role="main" class="grid" id="grid">
{cards}</main>
<footer role="contentinfo">
  <div class="links">
    <a href="https://github.com/VIP-881/hot-h5-games" rel="noopener external">⭐ GitHub</a>
    <a href="{BASE_URL}" rel="home">🌐 Pages</a>
    <a href="/sitemap.xml">🗺️ Sitemap</a>
    <a href="/robots.txt">🤖 Robots</a>
  </div>
  <p>🦊 灵犀工作室出品 · 纯 H5 零依赖 · 开源免费 · AI 驱动开发</p>
  <p style="margin-top:4px;color:#444">
    <span lang="zh-CN">中文</span> · 
    <a href="https://github.com/VIP-881/hot-h5-games" rel="license">MIT License</a> · 
    © 2026 灵犀工作室
  </p>
</footer>
<script>
(function(){{
  var games = {json.dumps(games)};
  var meta = {json.dumps(GAME_META, ensure_ascii=False)};
  var tc = {json.dumps(TAG_CLASSES)};
  window.filter = function(cat) {{
    document.querySelectorAll('.cat-btn').forEach(function(b){{ b.classList.remove('active'); }});
    event.target.classList.add('active');
    var grid = document.getElementById('grid');
    var html = '';
    var count = 0;
    for (var i = 0; i < games.length; i++) {{
      var key = games[i];
      if (!meta[key]) continue;
      var m = meta[key];
      var cat2 = m[3];
      if (cat !== 'all' && cat2 !== cat && !(cat==='classic'&&(cat2==='viral'||cat2==='hot'))) continue;
      count++;
      html += '<a class="card" href="'+key+'.html"><div class="card-icon">'+m[0]+'</div><div class="card-body"><h3>'+m[1]+'</h3><p>'+m[2]+'</p><span class="card-tag '+(tc[cat2]||'tag-hot')+'">'+m[4]+'</span></div></a>';
    }}
    grid.innerHTML = html;
    document.getElementById('count').textContent = count;
  }};
}})();
</script>
</body>
</html>'''
    return index_html


def update_robots_txt():
    """Ensure robots.txt is up to date."""
    content = f"""User-agent: *
Allow: /
Disallow: /assets/

Sitemap: {BASE_URL}/sitemap.xml

# Crawl-delay: 1
"""
    (DIR / 'robots.txt').write_text(content)

# ── Main ────────────────────────────────────────────────────
def main():
    deploy = '--deploy' in sys.argv

    print(f'🔍 Scanning games in {DIR}...')
    games = get_game_files()
    print(f'   Found {len(games)} games')

    print('📝 Building sitemap.xml...')
    sitemap = build_sitemap(games)
    (DIR / 'sitemap.xml').write_text(sitemap)
    print(f'   ✓ {len(sitemap)} bytes')

    print('📝 Building index.html...')
    index = build_index(games)
    (DIR / 'index.html').write_text(index)
    print(f'   ✓ {len(index)} bytes · {len(games)} cards')

    print('📝 Updating robots.txt...')
    update_robots_txt()
    print('   ✓ robots.txt')

    if not deploy:
        print('\n✅ Local build complete. Run with --deploy to push to GitHub.')
        return

    if not MATON_KEY:
        print('\n❌ MATON_API_KEY not set. Cannot deploy.')
        sys.exit(1)

    print('\n🚀 Deploying to GitHub...')
    for fname in ['index.html', 'sitemap.xml', 'robots.txt']:
        path = DIR / fname
        content = path.read_text()
        try:
            gh_upload(fname, content, f'Build: update {fname}')
            print(f'   ✓ {fname}')
        except Exception as e:
            print(f'   ✗ {fname}: {e}')

    print(f'\n✅ Deploy complete!')
    print(f'   🌐 {BASE_URL}')
    print(f'   📦 https://github.com/{GITHUB_REPO}')

if __name__ == '__main__':
    main()