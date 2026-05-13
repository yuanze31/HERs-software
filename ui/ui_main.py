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
                alignment: left;
            }
            QTabBar::tab {
                min-width: 80px;
                padding: 6px 12px;
                font-size: 13px;
                border-radius: 5px 5px 0 0;
                margin-right: 1px;
                background-color: #e8e8e8;
                color: #666;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #333;
            }
            QTabBar::tab:hover:not(selected) {
                background-color: #d8d8d8;
            }
            QTabWidget::pane {
                border: none;
            }
            QWidget {
                padding: 0;
                margin: 0;
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
