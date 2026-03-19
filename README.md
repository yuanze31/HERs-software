# Build

## html image download

```shell
pyinstaller -F -i yuanze31.ico -n 网页图片下载 --clean --noconfirm --exclude-module tkinter --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module unittest --exclude-module email --exclude-module xml --exclude-module html ./html-image-download/main.py
```

## image-resize

```shell
pyinstaller -F -i yuanze31.ico -n 图片宽度处理 --clean --noconfirm --exclude-module tkinter --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module IPython --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 --exclude-module unittest --exclude-module email --exclude-module http --exclude-module urllib --exclude-module xml --exclude-module html ./image-resize/main.py
```