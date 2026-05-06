import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QMainWindow, QStatusBar, QTabWidget)

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tabs.image_download_tab import ImageDownloadTab
from tabs.image_resize_tab import ImageResizeTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("yuanze31的工具集")
        self.setGeometry(100, 100, 800, 600)

        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), "yuanze31.ico")
        else:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "yuanze31.ico")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                min-width: 120px;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px 6px 0 0;
                margin-right: 4px;
                background-color: #f0f0f0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #ddd;
                border-bottom: none;
            }
            QTabBar::tab:hover:not(selected) {
                background-color: #e0e0e0;
            }
        """)

        self.download_tab = ImageDownloadTab()
        self.resize_tab = ImageResizeTab()

        self.tab_widget.addTab(self.download_tab, "图片下载")
        self.tab_widget.addTab(self.resize_tab, "图片处理")

        self.setCentralWidget(self.tab_widget)
