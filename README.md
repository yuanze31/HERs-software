# 图片工具集

包含图片下载和图片处理两个功能的工具集，支持命令行和图形界面两种方式。

## 功能模块

### 1. 网页图片下载
从指定网页提取并下载所有图片，支持多种图片格式。

### 2. 图片宽度处理
批量调整图片宽度，保持宽高比，支持静态图片和动画 GIF/WEBP。

## 目录结构

```
├── html-image-download/    # 命令行版 - 网页图片下载（停止更新）
│   └── main.py
├── image-resize/           # 命令行版 - 图片处理（停止更新）
│   └── main.py
├── ui/                     # GUI版
│   ├── main.py             # 应用入口
│   ├── ui_main.py          # 主窗口
│   ├── tabs/               # Tab组件
│   │   ├── image_download_tab.py
│   │   └── image_resize_tab.py
│   └── utils/              # 工具类
│       ├── downloader.py
│       └── resizer.py
├── yuanze31.ico            # 应用图标
└── README.md
```

## 依赖安装

```shell
# 安装基础依赖
pip install Pillow

# GUI版额外依赖
pip install PyQt6
```

## 运行方式

### 命令行版

```shell
# 网页图片下载
python html-image-download/main.py

# 图片宽度处理
python image-resize/main.py
```

### GUI版

```shell
python ui/main.py
```

## 打包命令

### 命令行版 - 网页图片下载

```shell
pyinstaller -F -i yuanze31.ico -n 网页图片下载 --clean --noconfirm --exclude-module tkinter --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module unittest --exclude-module email --exclude-module xml --exclude-module html ./html-image-download/main.py
```

### 命令行版 - 图片宽度处理

```shell
pyinstaller -F -i yuanze31.ico -n 图片宽度处理 --clean --noconfirm --exclude-module tkinter --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module unittest --exclude-module email --exclude-module http --exclude-module urllib --exclude-module xml --exclude-module html ./image-resize/main.py
```

### GUI版 - 工具集

```shell
pyinstaller -w -i yuanze31.ico -n yuanze31的工具集 --clean --noconfirm --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module IPython --collect-all PyQt6 --collect-all Pillow --add-data "yuanze31.ico:." --add-data "ui/tabs/*.py:tabs" --add-data "ui/utils/*.py:utils" --hidden-import "tabs.image_download_tab" --hidden-import "tabs.image_resize_tab" --hidden-import "utils.downloader" --hidden-import "utils.resizer" ./ui/main.py
```

> **注意**：在 Windows 命令行中使用 `^` 换行，Linux/macOS 使用 `\`。