# Image to WebP Converter

将 `images` 文件夹（含子文件夹）中的图片批量转换为 WebP 格式，输出到 `output` 文件夹并保持原有目录结构。

## 特性

- 支持 PNG、JPEG/JPG、GIF、BMP、TIFF（WebP 文件默认跳过，可选复制）
- 保留透明通道（RGBA / LA / 带透明色的调色板图片）
- 动图 GIF 转为动态 WebP，保留每一帧的时长和循环设置
- 按 EXIF 方向自动旋转手机照片
- 可选无损压缩、保留 EXIF / ICC 色彩配置
- 增量转换：输出文件已存在且比源文件新时自动跳过
- 多线程并行转换

## 安装依赖

需要 Python 3.9+。

```bash
pip install -r requirements.txt
```

## 使用方法

1. 将待转换的图片放入 `images` 文件夹（可包含子文件夹）
2. 运行脚本：

```bash
python convert_to_webp.py
```

3. 转换后的 WebP 文件会保存在 `output` 文件夹中

### 命令行参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-i, --input` | 输入文件夹 | `./images` |
| `-o, --output` | 输出文件夹 | `./output` |
| `-q, --quality` | 质量 0-100 | `85` |
| `--lossless` | 无损压缩 | 关闭 |
| `--method` | 压缩速度/体积权衡 0-6，越大越慢、文件越小 | `4` |
| `--keep-metadata` | 保留 EXIF 与 ICC 色彩配置 | 关闭 |
| `--force` | 忽略增量判断，全部重新转换 | 关闭 |
| `--copy-webp` | 将已是 WebP 的文件复制到输出目录 | 关闭 |
| `-j, --jobs` | 并行任务数 | CPU 核心数 |

示例：

```bash
# 指定目录，质量 75
python convert_to_webp.py -i ~/Pictures/raw -o ~/Pictures/webp -q 75

# 无损转换并保留拍摄信息
python convert_to_webp.py --lossless --keep-metadata
```

有任何文件转换失败时，脚本以非零状态码退出，方便在脚本或 CI 中使用。

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
├── tests/           # pytest 测试
├── convert_to_webp.py
├── requirements.txt
└── README.md
```

## 测试

```bash
pip install pytest
pytest -q
```

## 许可证

[MIT](LICENSE)
