# 🎮 热门 H5 游戏合集

**110+ 款免费在线 H5 小游戏** · 手机触屏 + PC 键盘 · 纯 HTML 零依赖 · 即点即玩

🌐 **在线体验**：https://vip-881.github.io/hot-h5-games

---

## 📦 部署流程（完整可复用）

### 一键构建 + 部署

```bash
# 1. 本地构建 index.html + sitemap.xml + robots.txt
python3 build.py

# 2. 构建 + 自动推送到 GitHub（GitHub Pages 自动部署）
export MATON_API_KEY="你的_API_KEY"
python3 build.py --deploy
```

### 三个核心脚本

| 脚本 | 作用 |
|------|------|
| `build.py` | 自动生成 index.html / sitemap.xml / robots.txt，可选推送 GitHub |
| `seo_enhance.py` | 为单个游戏页面批量注入 SEO 元数据 |
| `.github/workflows/deploy.yml` | GitHub Actions 自动部署到 Pages |

### 手动部署步骤

1. **构建**：`python3 build.py` 生成主页 + 站点地图
2. **Git 提交**：`git add . && git commit -m "更新游戏" && git push`
3. **自动部署**：GitHub Pages 检测到 `main` 分支更新后自动发布

---

## 🔍 SEO 优化清单

### 主页（index.html）已包含
- ✅ `<title>` + `<meta description>` + `<meta keywords>`
- ✅ Open Graph（og:title/description/type/url/site_name/locale）
- ✅ Twitter Card（summary_large_image）
- ✅ JSON-LD 结构化数据（CollectionPage + BreadcrumbList + WebSite + SearchAction）
- ✅ 规范链接 `<link rel="canonical">`
- ✅ `robots.txt` + `sitemap.xml`

### GEO 地理定位优化
- ✅ `geo.region` / `geo.placename` / `geo.position` 元标签
- ✅ `content-language` + `http-equiv` 语言声明
- ✅ hreflang 多语言交替链接（zh-CN / zh-Hans / en / x-default）
- ✅ `og:locale` + `og:locale:alternate` 区域声明

### 每个游戏页面
- ✅ 独立 title / description
- ✅ VideoGame JSON-LD 结构化数据
- ✅ OG + Twitter 分享元数据

---

## 🗂️ 目录结构

```
hot-h5-games/
├── index.html          # 主页（SEO/GEO 全优化，含分类筛选）
├── build.py            # 构建脚本
├── seo_enhance.py      # SEO 注入脚本
├── sitemap.xml         # 站点地图
├── robots.txt          # 爬虫规则
├── .github/workflows/  # GitHub Actions 自动部署
└── *.html              # 110+ 个游戏文件
```

---

## 🎮 游戏品类

益智 🧠 · 街机 🕹️ · 体育 ⚽ · 射击 🎯 · 纸牌 🃏 · 音乐 🎵 · 博牌 🎰 · 休闲 🍉 · 跑酷 🏃 · 物理 🔮 · 创作 🎨

---

## 📄 许可证

MIT License · 开源免费 · 🦊 灵犀工作室出品

## ⭐ 支持

给个 Star 支持一下吧！[github.com/VIP-881/hot-h5-games](https://github.com/VIP-881/hot-h5-games)