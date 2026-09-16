# 🚀 灵犀游戏大厅 · 部署与 SEO/GEO 优化手册

> 轻量级静态游戏（纯 HTML/CSS/JS）的完整部署流程 + 搜索引擎/地理定位优化方案
> 适用平台：GitHub Pages（通过 Maton API Gateway 自动化）

---

## 一、技术栈

| 维度 | 方案 |
|------|------|
| 游戏开发 | 纯 HTML + CSS + JavaScript (ES6+) |
| 图形引擎 | Canvas 2D / CSS Grid + DOM |
| 部署平台 | GitHub Pages（静态托管） |
| 自动化 | Python 脚本 + Maton API Gateway |
| 状态持久化 | localStorage（客户端） |
| 音效 | Web Audio API 程序化合成 |

---

## 二、部署流程（完整可复用）

### 前置条件
```bash
export MATON_API_KEY="v2.xxx"   # Maton API Key
```

### 标准部署命令

| 命令 | 功能 | 适用场景 |
|------|------|---------|
| `python3 deploy.py diff` | 比较本地 ↔ GitHub 文件差异 | 部署前检查 |
| `python3 deploy.py sync` | 检测变更 → 上传到 GitHub | 新增/更新游戏 |
| `python3 deploy.py sitemap` | 重新生成 sitemap.xml | 新增游戏后 |
| `python3 deploy.py verify` | 全面验证部署状态 | 部署后确认 |
| `python3 deploy.py seo` | SEO/GEO 评分检查 | 定期优化审查 |
| `python3 deploy.py all` | 一键完整部署 | 标准发布 |

### 子页面 SEO 批量注入

| 命令 | 功能 |
|------|------|
| `python3 inject_seo.py dry-run` | 预览哪些游戏缺 SEO（不改动） |
| `python3 inject_seo.py inject` | 下载→注入→保存到本地 |
| `python3 inject_seo.py upload` | 批量上传注入结果到 GitHub |
| `python3 inject_seo.py report` | 生成 SEO 完备性报告 |

### 完整部署流程（6 步）

```bash
# 1. 开发新游戏（单文件 .html，零外部依赖）
#    放在本地目录 /home/admin/.openclaw/canvas/games/maton-games/

# 2. 检查差异
python3 deploy.py diff

# 3. 同步到 GitHub
python3 deploy.py sync

# 4. 更新 sitemap（覆盖全部游戏）
python3 deploy.py sitemap

# 5. 批量注入子页面 SEO（可选，新游戏需要）
python3 inject_seo.py inject
python3 inject_seo.py upload

# 6. 验证部署
python3 deploy.py verify
```

---

## 三、主页 SEO 优化（28 项全量覆盖）

### 基础 Meta 标签
```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
<title>🎮 灵犀游戏大厅 · 165款免费H5游戏 | ...</title>
<meta name="description" content="165款免费H5小游戏合集...">
<meta name="keywords" content="H5游戏,免费游戏,在线游戏,...">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="theme-color" content="#0a0a1a">
<meta name="author" content="灵犀 AI">
```

### GEO 地理定位优化
```html
<meta name="geo.region" content="CN">            <!-- 区域 -->
<meta name="geo.placename" content="China">      <!-- 地名 -->
<meta name="geo.position" content="35.8617;104.1954">  <!-- 坐标 -->
<meta name="ICBM" content="35.8617, 104.1954">   <!-- 旧式坐标 -->
```

### 多语言区域适配（hreflang）
```html
<link rel="alternate" hreflang="zh-CN" href=".../">
<link rel="alternate" hreflang="zh-Hans" href=".../">
<link rel="alternate" hreflang="zh-Hant" href=".../?lang=zh-Hant">
<link rel="alternate" hreflang="en" href=".../?lang=en">
<link rel="alternate" hreflang="x-default" href=".../">
```

### 结构化数据（JSON-LD）
- **CollectionPage**：主页合集描述 + 165 游戏 ItemList
- **VideoGame** 子实体：每款游戏含 genre/playMode/applicationCategory/URL
- **Person**：作者信息

### 社交分享标签
- Open Graph（Facebook/微信）：title/description/type/url/image/locale/site_name
- Twitter Cards：summary_large_image 类型

### 爬虫友好特性
- **166 个静态 `<a>` 链接**（`<details>` 折叠 footer）
- canonical URL 规范
- sitemap.xml 引用
- Dublin Core 元数据（学术搜索引擎）

---

## 四、子页面 SEO（165 游戏全量覆盖）

每款游戏页面包含：
```html
<title>🎮 [游戏名] - 灵犀游戏大厅 | 免费H5在线小游戏</title>
<meta name="description" content="[游戏描述]...">
<meta name="keywords" content="[游戏名],[英文名],H5游戏,免费游戏,...">
<link rel="canonical" href="https://vip-881.github.io/hot-h5-games/[游戏].html">
<meta property="og:title" content="🎮 [游戏名] - 灵犀游戏大厅">
<meta property="og:description" content="...">
<meta property="og:type" content="website">
<meta property="og:url" content="...">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "[游戏名]",
  "genre": "[类别]",
  "playMode": "SinglePlayer",
  ...
}
</script>
```

---

## 五、区域适配策略

| 策略 | 实现 | 效果 |
|------|------|------|
| **多语言切换** | `?lang=zh-CN` / `?lang=en` 参数 | 中/英双语用户 |
| **hreflang 标注** | 6 组 alternate 标签 | Google 正确识别语言版本 |
| **GEO 元数据** | geo.region/position/ICBM | 本地化搜索排名 |
| **地理中心坐标** | 35.86, 104.20（中国地理中心） | 覆盖全国用户 |
| **内容本地化** | 中文游戏名 + 中文描述 | 中文搜索可见性 |

---

## 六、验证清单

部署后必须确认：

- [ ] 主页 HTTP 200，字号正常
- [ ] 28 项 SEO/GEO 标签齐全
- [ ] 165 个静态游戏链接可被爬虫发现
- [ ] sitemap.xml 覆盖全部游戏 URL
- [ ] robots.txt 正确引用 sitemap
- [ ] 每个游戏子页面 6/6 SEO 评分
- [ ] GitHub Pages 构建成功（status: built）
- [ ] HTTPS 强制启用

运行 `python3 deploy.py verify` 可一键完成以上检查。

---

## 七、维护建议

1. **每新增游戏**：运行 `deploy.py all` + `inject_seo.py upload`
2. **每周**：运行 `deploy.py seo` 检查 SEO 评分
3. **每月**：审查 sitemap 覆盖率，补充 Google Search Console 索引
4. **定期**：检查 og:image 是否可访问（当前指向 CDN，需确保稳定）

---

## 附：目录结构

```
maton-games/
├── *.html              # 165 款游戏文件
├── index.html          # 主页（含 SEO/GEO + 静态链接）
├── sitemap.xml         # 全量 URL 地图
├── robots.txt          # 爬虫规则
├── manifest.json       # PWA 配置
├── deploy.py           # 部署自动化脚本
├── inject_seo.py       # 子页面 SEO 注入工具
└── *.md                # 规划文档
```