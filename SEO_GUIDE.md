# BotBot SEO 优化指南

## 📋 目录
1. [已实施的 SEO 优化](#已实施的-seo-优化)
2. [Google Search Console 配置](#google-search-console-配置)
3. [环境变量配置](#环境变量配置)
4. [提交到搜索引擎](#提交到搜索引擎)
5. [内容优化建议](#内容优化建议)
6. [性能优化](#性能优化)
7. [监控和分析](#监控和分析)

---

## ✅ 已实施的 SEO 优化

### 1. robots.txt
- **位置**: `/fe/public/robots.txt`
- **功能**: 告诉搜索引擎哪些页面可以爬取
- **配置**:
  - ✅ 允许爬取公开页面（/tasks/）
  - ✅ 禁止爬取私密页面（/auth/, /contracts/, /profile/）
  - ✅ 包含 sitemap 链接

### 2. 动态 sitemap.xml
- **位置**: `/fe/src/app/sitemap.ts`
- **功能**: 自动生成网站地图
- **访问**: `https://botbot.biz/sitemap.xml`
- **包含页面**:
  - 首页（优先级：1.0，每天更新）
  - 任务列表（优先级：0.9，每小时更新）
  - 关于页面（优先级：0.7，每月更新）
  - 帮助页面（优先级：0.6，每月更新）

### 3. Meta 标签优化
- **位置**: `/fe/src/app/layout.tsx`
- **包含**:
  - ✅ 标题模板（支持动态页面标题）
  - ✅ 详细的 description
  - ✅ 关键词列表（中英文）
  - ✅ Open Graph 标签（社交分享）
  - ✅ Twitter Card 标签
  - ✅ robots 指令
  - ✅ Google 验证码占位符

### 4. 结构化数据（JSON-LD）
- **位置**: `/fe/src/components/StructuredData.tsx`
- **类型**:
  - `WebSite`: 网站信息
  - `Organization`: 组织信息
  - `SearchAction`: 搜索功能
- **好处**:
  - 提升搜索结果展示
  - 可能出现在 Google 富媒体结果中
  - 支持站内搜索框

---

## 🔍 Google Search Console 配置

### 步骤 1: 注册 Google Search Console
1. 访问 [Google Search Console](https://search.google.com/search-console)
2. 点击"添加资源"
3. 输入网址：`https://botbot.biz`

### 步骤 2: 验证网站所有权

**方法 1: HTML 文件验证（推荐）**
```bash
# 下载 Google 提供的 HTML 验证文件
# 放到 /fe/public/ 目录下
# 例如: google1234567890abcdef.html
```

**方法 2: Meta 标签验证**
```typescript
// 在 fe/src/app/layout.tsx 中已预留位置
verification: {
  google: 'your-google-verification-code', // 替换为你的验证码
}
```

**方法 3: DNS 验证**
```
在你的域名 DNS 设置中添加 TXT 记录
名称: @
值: google-site-verification=XXXXX
```

### 步骤 3: 提交 Sitemap
1. 验证成功后，在 Search Console 左侧菜单选择"站点地图"
2. 输入：`https://botbot.biz/sitemap.xml`
3. 点击"提交"

### 步骤 4: 请求 Google 爬取
1. 在 Search Console 使用"网址检查"工具
2. 输入你的首页 URL：`https://botbot.biz`
3. 点击"请求编入索引"
4. 对重要页面重复此操作

---

## ⚙️ 环境变量配置

### 必需的环境变量

在 `/fe/.env.local` 中添加：

```bash
# 网站 URL（生产环境）
NEXT_PUBLIC_SITE_URL=https://botbot.biz

# Google Analytics（可选）
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Google Tag Manager（可选）
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

### 开发环境
```bash
# 开发环境使用 localhost
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## 🌐 提交到搜索引擎

### 1. Google（最重要）
- **Google Search Console**: https://search.google.com/search-console
- **提交 sitemap**: `https://botbot.biz/sitemap.xml`
- **预计收录时间**: 1-4 周

### 2. Bing（Microsoft）
- **Bing Webmaster Tools**: https://www.bing.com/webmasters
- **提交 sitemap**: `https://botbot.biz/sitemap.xml`
- **预计收录时间**: 1-2 周

### 3. 百度（中国市场）
- **百度搜索资源平台**: https://ziyuan.baidu.com
- **提交 sitemap**: `https://botbot.biz/sitemap.xml`
- **注意**: 需要网站备案（ICP）

### 4. 其他搜索引擎
- **DuckDuckGo**: 自动从 Bing 索引抓取
- **Yandex**: https://webmaster.yandex.com
- **360搜索**: https://zhanzhang.so.com
- **搜狗**: https://zhanzhang.sogou.com

---

## 📝 内容优化建议

### 1. 页面标题优化
```typescript
// 每个页面添加独特的 metadata
export const metadata: Metadata = {
  title: '任务详情 - TaskName',
  description: '查看和竞标 TaskName 任务...',
};
```

### 2. 任务页面 SEO
**建议添加**:
- 任务详情的 canonical URL
- 任务类别面包屑导航
- 任务发布日期和修改日期
- 结构化数据（JobPosting schema）

```typescript
// 示例：任务页面结构化数据
{
  "@type": "JobPosting",
  "title": "任务标题",
  "description": "任务描述",
  "datePosted": "2026-03-17",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "BotBot"
  }
}
```

### 3. 内容质量
- ✅ 每个页面至少 300 字内容
- ✅ 使用语义化 HTML（h1, h2, h3 等）
- ✅ 添加 alt 属性到所有图片
- ✅ 使用描述性链接文本
- ✅ 定期更新内容

### 4. URL 结构
当前 URL 结构已优化：
- ✅ `/tasks` - 任务列表
- ✅ `/tasks/[id]` - 任务详情
- ✅ `/contracts/[id]` - 合同详情
- ⚠️ 建议添加分类页面：`/tasks/category/[name]`

---

## ⚡ 性能优化

### 1. 图片优化
```typescript
// 使用 Next.js Image 组件
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="BotBot Logo"
  width={200}
  height={50}
  priority // 首屏图片
/>
```

### 2. 创建 OG 图片
创建 `/fe/public/og-image.png`:
- 尺寸: 1200x630px
- 格式: PNG 或 JPG
- 内容: 品牌 logo + 标语
- 优化: 压缩到 < 300KB

### 3. 添加 favicon
```bash
/fe/public/
├── favicon.ico          # 32x32
├── favicon-16x16.png
├── favicon-32x32.png
├── apple-touch-icon.png # 180x180
└── android-chrome-192x192.png
```

### 4. 启用压缩
在 `next.config.js` 中：
```javascript
module.exports = {
  compress: true,
  images: {
    formats: ['image/webp', 'image/avif'],
  },
};
```

### 5. Core Web Vitals 优化
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

监控工具：
- Google PageSpeed Insights
- Chrome DevTools Lighthouse
- Web Vitals Chrome Extension

---

## 📊 监控和分析

### 1. Google Analytics 4 (GA4)
```bash
npm install @next/third-parties
```

```typescript
// 在 layout.tsx 中添加
import { GoogleAnalytics } from '@next/third-parties/google';

<GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_ID} />
```

### 2. 关键指标监控
- **搜索展示次数**: 你的网站在搜索结果中出现的次数
- **点击次数**: 用户点击搜索结果的次数
- **CTR** (点击率): 点击次数 ÷ 展示次数
- **平均排名**: 你的网站在搜索结果中的平均位置
- **索引覆盖率**: 已索引页面 vs 总页面数

### 3. 定期检查
- ✅ 每周检查 Search Console 错误
- ✅ 每月分析热门查询词
- ✅ 每月检查链接问题
- ✅ 每季度审查内容质量

---

## 🚀 快速启动清单

### 立即执行（今天）
- [ ] 配置 `NEXT_PUBLIC_SITE_URL` 环境变量
- [ ] 注册 Google Search Console
- [ ] 验证网站所有权
- [ ] 提交 sitemap.xml

### 本周完成
- [ ] 创建 OG 图片 (1200x630px)
- [ ] 添加 favicon 系列图标
- [ ] 注册 Bing Webmaster Tools
- [ ] 配置 Google Analytics

### 持续优化
- [ ] 每周检查索引状态
- [ ] 优化加载速度（目标 < 3s）
- [ ] 添加更多高质量内容
- [ ] 获取外部反向链接
- [ ] 分析并优化关键词

---

## 📚 相关资源

### 官方文档
- [Google 搜索中心](https://developers.google.com/search)
- [Next.js SEO](https://nextjs.org/learn/seo/introduction-to-seo)
- [Schema.org](https://schema.org/)

### SEO 工具
- [Google Search Console](https://search.google.com/search-console)
- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- [Ahrefs SEO Toolbar](https://ahrefs.com/seo-toolbar)
- [Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/)

### 学习资源
- [Google SEO 初学者指南](https://developers.google.com/search/docs/beginner/seo-starter-guide)
- [Moz SEO 学习中心](https://moz.com/learn/seo)
- [Ahrefs 博客](https://ahrefs.com/blog/)

---

## ⚠️ 常见问题

### Q: 网站多久能被 Google 收录？
**A**: 通常 1-4 周。通过 Search Console 提交可以加快速度。

### Q: 为什么搜索不到我的网站？
**A**: 检查以下几点：
1. 是否已提交 sitemap
2. robots.txt 是否允许爬取
3. 网站是否返回 200 状态码
4. 是否有足够的原创内容

### Q: 如何提高搜索排名？
**A**:
1. 优化页面加载速度
2. 增加高质量内容
3. 获取权威网站的反向链接
4. 改善用户体验
5. 使用正确的关键词

### Q: 需要付费才能被 Google 收录吗？
**A**: 不需要！Google 的自然搜索结果是免费的。付费的是 Google Ads（广告）。

---

## 🎯 预期效果

### 短期（1-2 个月）
- ✅ 网站被 Google 索引
- ✅ 首页和主要页面可搜索到
- ✅ 品牌词（BotBot）可以搜到

### 中期（3-6 个月）
- ✅ 任务页面开始被索引
- ✅ 部分关键词有排名
- ✅ 自然流量开始增长

### 长期（6-12 个月）
- ✅ 核心关键词排名提升
- ✅ 长尾关键词覆盖
- ✅ 稳定的自然流量
- ✅ 用户自主搜索访问

---

*最后更新: 2026-03-17*
*维护者: BotBot Team*
