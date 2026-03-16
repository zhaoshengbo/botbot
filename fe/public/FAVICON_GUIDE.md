# Favicon 生成指南

由于 favicon 需要设计图像，无法通过代码自动生成。请按照以下步骤创建 BotBot 的 favicon 图标集。

## 方法 1：使用在线工具（推荐）

### 1. 准备源图像
创建或准备一个 **512×512px** 或更大的正方形图像：
- 格式：PNG（支持透明背景）
- 内容：BotBot logo 或 🦞 龙虾图标
- 背景：透明或纯色

### 2. 使用 Favicon 生成器

访问以下任一在线工具：

**推荐工具**：
- **RealFaviconGenerator**: https://realfavicongenerator.net/
  - ✅ 自动生成所有尺寸
  - ✅ 提供预览效果
  - ✅ 生成 HTML 代码
  - ✅ 支持多平台适配

- **Favicon.io**: https://favicon.io/
  - ✅ 简单易用
  - ✅ 支持从文字/Emoji/图片生成
  - ✅ 免费无水印

### 3. 生成所需文件

上传你的源图像后，下载生成的文件包，应包含：

```
favicon.ico           # 32×32 (兼容旧浏览器)
favicon-16x16.png     # 16×16
favicon-32x32.png     # 32×32
apple-touch-icon.png  # 180×180 (iOS 主屏图标)
android-chrome-192x192.png  # 192×192 (Android)
android-chrome-512x512.png  # 512×512 (Android)
```

### 4. 放置文件

将生成的所有文件放到 `/fe/public/` 目录：

```bash
cp ~/Downloads/favicon-package/* /path/to/botbot/fe/public/
```

### 5. 更新 HTML（已配置）

Next.js 会自动检测 `public/` 目录下的 favicon 文件，无需额外配置。

如果需要显式声明，在 `/fe/src/app/layout.tsx` 中添加：

```typescript
export const metadata: Metadata = {
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  // ... 其他配置
}
```

---

## 方法 2：使用 Emoji 快速生成

如果暂时没有设计好的 logo，可以快速使用 Emoji 生成：

### 使用 Favicon.io 的 Emoji 生成器

1. 访问：https://favicon.io/emoji-favicons/
2. 搜索"lobster"或"shrimp"
3. 选择 🦞 龙虾 emoji
4. 自定义背景色：
   - 推荐：`#EF4444`（红色，符合 BotBot 主题）
   - 或：`#F97316`（橙色）
5. 点击"Download"
6. 解压并放置到 `/fe/public/`

---

## 方法 3：使用 ImageMagick（命令行）

如果你有源图像且安装了 ImageMagick：

```bash
# 安装 ImageMagick（macOS）
brew install imagemagick

# 准备源图像（512×512px）
SOURCE_IMAGE="logo-512.png"

# 生成各种尺寸
convert $SOURCE_IMAGE -resize 16x16 favicon-16x16.png
convert $SOURCE_IMAGE -resize 32x32 favicon-32x32.png
convert $SOURCE_IMAGE -resize 180x180 apple-touch-icon.png
convert $SOURCE_IMAGE -resize 192x192 android-chrome-192x192.png
convert $SOURCE_IMAGE -resize 512x512 android-chrome-512x512.png

# 生成 .ico 文件（包含多个尺寸）
convert $SOURCE_IMAGE -resize 32x32 \
        $SOURCE_IMAGE -resize 16x16 \
        favicon.ico
```

---

## 验证安装

完成后，在浏览器中访问：

- http://localhost:3000/favicon.ico
- http://localhost:3000/favicon-32x32.png
- http://localhost:3000/apple-touch-icon.png

如果能看到图标，说明安装成功！

---

## 设计建议

### BotBot 品牌色彩
根据 TailwindCSS 配置和现有设计：

- **主色调**：红色系 `#EF4444` (red-500)
- **次要色**：橙色 `#F97316` (orange-500)
- **渐变**：`from-red-500 to-orange-500`

### 图标创意
- 🦞 龙虾形象（符合"龙虾智能体"概念）
- 字母"B"（BotBot 首字母）
- 字母"BB"的组合
- 龙虾 + 机器人元素结合

### 尺寸规范
- **最小清晰度**：16×16px 时图标依然可识别
- **建议复杂度**：简单、扁平化设计
- **背景处理**：透明背景或纯色背景

---

## 临时方案

如果急需上线但还没设计好图标，可以暂时使用文字 favicon：

1. 访问 https://favicon.io/favicon-generator/
2. 输入文字：`B` 或 `BB`
3. 选择字体：Bold
4. 背景色：`#EF4444`
5. 文字色：`#FFFFFF`
6. 下载并部署

---

## 需要帮助？

如果需要专业设计，可以考虑：
- **Fiverr**: https://www.fiverr.com (搜索"favicon design")
- **Upwork**: https://www.upwork.com
- **99designs**: https://99designs.com

预算：$5 - $50 USD

---

*最后更新：2026-03-17*
