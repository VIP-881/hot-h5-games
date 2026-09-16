# H5 Game SEO Enhancement Script
# Adds SEO meta tags (OG, Twitter, JSON-LD) to game HTML files that lack them.
# Run: python3 seo_enhance.py

import glob, os, re

DIR = '/home/admin/.openclaw/canvas/games/hot-games'
BASE_URL = 'https://vip-881.github.io/hot-h5-games'

GAME_INFO = {
    "2048.html": ("2048", "经典数字合并游戏"),
    "snake.html": ("贪吃蛇", "经典霓虹贪吃蛇"),
    "flappy.html": ("Flappy Bird", "点击飞越水管障碍"),
    "match3.html": ("消消乐", "宝石三连消益智"),
    "jump.html": ("跳一跳", "蓄力跳跃刷屏游戏"),
    "breakout.html": ("打砖块", "经典街机弹球"),
    "bubble.html": ("泡泡龙", "瞄准三连消除"),
    "shmup.html": ("飞机大战", "弹幕射击Boss"),
    "fruit.html": ("切水果", "划屏切割避开炸弹"),
    "link.html": ("连连看", "三线连通配对消除"),
    "hoop.html": ("投篮大挑战", "滑动投篮连击"),
    "piano.html": ("别踩白块", "节奏点击黑块"),
    "mole.html": ("打地鼠", "30秒敲地鼠"),
    "puzzle.html": ("滑动拼图", "数字华容道"),
    "racer.html": ("公路飙车", "躲避障碍渐进加速"),
    "suika.html": ("合成大西瓜", "物理碰撞合成消除"),
    "pong.html": ("乒乓球", "AI对战先7球"),
    "memory.html": ("记忆翻牌", "8对emoji配对"),
    "penalty.html": ("点球大战", "5轮点球对决"),
    "mines.html": ("扫雷", "9×9经典扫雷"),
}

def add_seo_tags(filepath, name, desc):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if '<meta property="og:title"' in content:
        return False
    
    seo_block = f'''<meta name="description" content="{name} - {desc}，热门H5小游戏免费在线玩，无需下载即点即玩">
<meta property="og:title" content="{name} - 热门H5游戏">
<meta property="og:description" content="{desc}，热门H5小游戏合集">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE_URL}/{os.path.basename(filepath)}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{name} - 热门H5游戏">
<meta name="twitter:description" content="{desc}，免费在线H5游戏">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"VideoGame","name":"{name}","description":"{desc}","playMode":"SinglePlayer","applicationCategory":"Game","operatingSystem":"Web"}</script>
'''
    idx = content.index('<meta name="viewport"')
    end_idx = content.index('>', idx) + 1
    content = content[:end_idx] + '\n' + seo_block + content[end_idx:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    return True

if __name__ == '__main__':
    count = 0
    for fpath in glob.glob(f'{DIR}/*.html'):
        fname = os.path.basename(fpath)
        if fname == 'index.html': continue
        if fname in GAME_INFO:
            name, desc = GAME_INFO[fname]
            if add_seo_tags(fpath, name, desc):
                count += 1
    print(f'SEO tags added to {count} files')