# Image to WebP Converter

将 `images` 文件夹（含子文件夹）中的图片转换为 WebP 格式，输出到 `output` 文件夹。

## 支持的格式

- PNG, JPEG/JPG, GIF, BMP, TIFF, WebP

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 将待转换的图片放入 `images` 文件夹（可包含子文件夹）
2. 运行脚本：

```bash
python convert_to_webp.py
```

3. 转换后的 WebP 文件会保存在 `output` 文件夹中，并保持原有目录结构

## 目录结构

```
image_to_webp/
├── images/          # 输入：待转换的图片
│   ├── photo1.jpg
│   └── subfolder/
│       └── photo2.png
├── output/          # 输出：转换后的 WebP
│   ├── photo1.webp
│   └── subfolder/
│       └── photo2.webp
├── convert_to_webp.py
├── requirements.txt
└── README.md
```

## 推送到 GitHub

1. 在 [GitHub](https://github.com/new) 上创建新仓库（例如 `image_to_webp`）
2. 添加远程并推送：

```bash
git remote add origin https://github.com/你的用户名/image_to_webp.git
git branch -M main
git push -u origin main
```

> `images/` 和 `output/` 已加入 `.gitignore`，不会被上传，可确保私人照片不外泄。
