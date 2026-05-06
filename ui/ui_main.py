import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tabs.registry import get_all_tabs


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

        self._load_tabs()

        self.setCentralWidget(self.tab_widget)

    def _load_tabs(self):
        tabs_dict = get_all_tabs()
        for tab_name, tab_class in tabs_dict.items():
            try:
                tab_instance = tab_class()
                self.tab_widget.addTab(tab_instance, tab_name)
            except Exception as e:
                print(f"加载Tab失败 {tab_name}: {e}")
