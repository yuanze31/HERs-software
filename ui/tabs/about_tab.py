import webbrowser

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import Qt

import ENV
from tabs.base_tab import BaseTab
from tabs.registry import register_tab


class CheckUpdateWorker(QThread):
    checked = pyqtSignal(bool, str, str)

    def __init__(self):
        super().__init__()

    def run(self):
        if not ENV.UPDATE_CHECK_URL:
            self.checked.emit(False, "", "未配置检查更新地址")
            return

        try:
            import json
            import urllib.request
            import urllib.error

            req = urllib.request.Request(ENV.UPDATE_CHECK_URL, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
            with urllib.request.urlopen(req, timeout=10) as f:
                content = f.read().decode('utf-8')

            data = json.loads(content)

            latest_version_name = data.get('VERSION_NAME', "")
            latest_version_number = data.get('VERSION_NUMBER', 0)
            latest_download_link = data.get('DOWNLOAD_LINK', "")

            if latest_version_number == 0:
                self.checked.emit(False, "", "检查更新失败: 无法解析版本信息")
            elif latest_version_number > ENV.VERSION_NUMBER:
                self.checked.emit(True, latest_version_name, latest_download_link)
            else:
                self.checked.emit(False, latest_version_name, "当前已是最新版本")

        except json.JSONDecodeError:
            self.checked.emit(False, "", "检查更新失败: 无效的JSON格式")
        except Exception as e:
            self.checked.emit(False, "", f"检查更新失败: {str(e)}")


@register_tab("关于")
class AboutTab(BaseTab):
    def __init__(self):
        self.tab_name = "关于"
        self.latest_download_link = ""
        self.worker = None
        super().__init__()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("yuanze31的工具集")
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #333;
            line-height: 1;
            padding: 0;
            margin: 0;
        """)
        title_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout.addWidget(title_label)

        version_label = QLabel("版本: " + ENV.VERSION_NAME)
        version_label.setStyleSheet("""
            font-size: 14px; 
            color: #666;
            line-height: 1;
            padding: 0;
            margin: 2px 0 0 0;
        """)
        version_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout.addWidget(version_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 10, 0, 0)

        self.check_btn = QPushButton("检查更新")
        self.check_btn.clicked.connect(self.check_update)
        self.check_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        btn_layout.addWidget(self.check_btn)

        self.download_btn = QPushButton("下载更新")
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setEnabled(False)
        self.download_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background-color: #52c41a;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #389e0d;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        btn_layout.addWidget(self.download_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
            line-height: 1;
            padding: 0;
            margin: 6px 0 0 0;
        """)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout.addWidget(self.status_label)

        desc1_label = QLabel("""一个用于图片处理的工具集

• 图片下载: 从网页批量下载图片
• 图片处理: 批量调整图片宽度
""")
        desc1_label.setStyleSheet("""
            font-size: 14px; 
            color: #555;
            line-height: 1.2;
            padding: 0;
            margin: 12px 0 0 0;
        """)
        desc1_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout.addWidget(desc1_label)

        self.github_label = QLabel('<a href="https://github.com/yuanze31/HERs-software">在Github开源</a>')
        self.github_label.setOpenExternalLinks(False)
        self.github_label.setStyleSheet("""
            font-size: 14px; 
            color: #4a90d9;
            line-height: 1.2;
            padding: 0;
            margin: 0 0 0 0;
        """)
        self.github_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.github_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_label.mousePressEvent = self.open_github
        layout.addWidget(self.github_label)

        layout.addStretch()

        self.setLayout(layout)

    def check_update(self):
        if self.worker and self.worker.isRunning():
            return

        self.check_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.status_label.setText("正在检查更新...")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            line-height: 1;
            padding: 0;
            margin: 6px 0 0 0;
        """)
        self.latest_download_link = ""

        self.worker = CheckUpdateWorker()
        self.worker.checked.connect(self.on_update_checked)
        self.worker.start()

    def on_update_checked(self, has_update, version_name, download_link_or_msg):
        self.check_btn.setEnabled(True)

        if has_update:
            self.latest_download_link = download_link_or_msg
            self.download_btn.setEnabled(True)
            self.status_label.setText(f"发现新版本: {version_name}")
            self.status_label.setStyleSheet("""
                font-size: 12px;
                color: #fa8c16;
                line-height: 1;
                padding: 0;
                margin: 6px 0 0 0;
            """)
        else:
            self.download_btn.setEnabled(False)
            self.status_label.setText(download_link_or_msg)
            if "失败" in download_link_or_msg:
                self.status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #f5222d;
                    line-height: 1;
                    padding: 0;
                    margin: 6px 0 0 0;
                """)
            else:
                self.status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #52c41a;
                    line-height: 1;
                    padding: 0;
                    margin: 6px 0 0 0;
                """)

    def download_update(self):
        if self.latest_download_link:
            webbrowser.open(self.latest_download_link)

    def open_github(self, event):
        webbrowser.open("https://github.com/yuanze31/HERs-software")
