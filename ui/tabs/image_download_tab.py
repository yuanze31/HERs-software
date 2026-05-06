import os
import sys

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget)

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.downloader import ImageDownloader


class DownloadWorker(QThread):
    progress_updated = pyqtSignal(int, int, int)
    url_progress_updated = pyqtSignal(int, int)
    finished = pyqtSignal(dict)
    url_finished = pyqtSignal(str, dict)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        downloader = ImageDownloader()
        overall_result = {
                'success': True,
                'total_urls': len(self.urls),
                'success_urls': 0,
                'total_images': 0,
                'success_images': 0,
                'errors': [],
                'url_results': []
                }

        for idx, url in enumerate(self.urls, 1):
            result = downloader.download_images(url, self.on_progress)
            self.url_finished.emit(url, result)
            self.url_progress_updated.emit(idx, len(self.urls))

            if result['success']:
                overall_result['success_urls'] += 1
                overall_result['total_images'] += result['total']
                overall_result['success_images'] += result['success_count']
                if result['errors']:
                    overall_result['errors'].extend(result['errors'])
            else:
                overall_result['success'] = False
                overall_result['errors'].append(f"URL处理失败: {url} - {result['message']}")

        self.finished.emit(overall_result)

    def on_progress(self, current, total, success_count):
        self.progress_updated.emit(current, total, success_count)


class ImageDownloadTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        url_label = QLabel("网页链接（每行一个）：")
        url_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(url_label)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("请输入网页链接，每行一个")
        self.url_input.setStyleSheet("""
            QTextEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                font-family: Consolas, monospace;
            }
            QTextEdit:focus {
                border-color: #4a90d9;
                outline: none;
            }
        """)
        self.url_input.setMinimumHeight(100)
        layout.addWidget(self.url_input)

        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 24px;
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        layout.addWidget(self.download_btn)

        url_progress_layout = QHBoxLayout()
        url_progress_layout.setSpacing(10)

        self.url_progress_bar = QProgressBar()
        self.url_progress_bar.setValue(0)
        self.url_progress_bar.setStyleSheet("""
            QProgressBar {
                height: 24px;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4a90d9;
                border-radius: 4px;
            }
        """)

        self.url_progress_label = QLabel("网页进度: 0/0")
        self.url_progress_label.setStyleSheet("font-size: 12px; color: #666;")

        url_progress_layout.addWidget(self.url_progress_bar)
        url_progress_layout.addWidget(self.url_progress_label)
        layout.addLayout(url_progress_layout)

        image_progress_layout = QHBoxLayout()
        image_progress_layout.setSpacing(10)

        self.image_progress_bar = QProgressBar()
        self.image_progress_bar.setValue(0)
        self.image_progress_bar.setStyleSheet("""
            QProgressBar {
                height: 24px;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #5cb85c;
                border-radius: 4px;
            }
        """)

        self.image_progress_label = QLabel("图片进度: 等待中...")
        self.image_progress_label.setStyleSheet("font-size: 12px; color: #666;")

        image_progress_layout.addWidget(self.image_progress_bar)
        image_progress_layout.addWidget(self.image_progress_label)
        layout.addLayout(image_progress_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.worker = None

    def add_log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_download(self):
        text = self.url_input.toPlainText().strip()
        if not text:
            self.add_log("请输入网页链接")
            return

        urls = [line.strip() for line in text.split('\n') if line.strip()]
        if not urls:
            self.add_log("请输入有效的网页链接")
            return

        self.download_btn.setEnabled(False)
        self.url_progress_bar.setValue(0)
        self.image_progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log(f"发现 {len(urls)} 个网页链接")

        for i, url in enumerate(urls, 1):
            self.add_log(f"{i}. {url}")

        self.worker = DownloadWorker(urls)
        self.worker.progress_updated.connect(self.on_image_progress)
        self.worker.url_progress_updated.connect(self.on_url_progress)
        self.worker.url_finished.connect(self.on_url_finished)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.start()

    def on_url_progress(self, current, total):
        progress = int((current / total) * 100)
        self.url_progress_bar.setValue(progress)
        self.url_progress_label.setText(f"网页进度: {current}/{total}")

    def on_image_progress(self, current, total, success_count):
        progress = int((current / total) * 100)
        self.image_progress_bar.setValue(progress)
        self.image_progress_label.setText(f"图片进度: {current}/{total} (成功: {success_count})")

    def on_url_finished(self, url, result):
        if result['success']:
            self.add_log(f"\n[{url}]")
            self.add_log(f"  发现 {result['total']} 张图片")
            self.add_log(f"  成功下载 {result['success_count']}/{result['total']}")
            self.add_log(f"  保存到: {result['download_dir']}")
        else:
            self.add_log(f"\n[{url}] 失败: {result['message']}")

    def on_download_finished(self, result):
        self.download_btn.setEnabled(True)

        self.add_log("\n=== 下载完成 ===")
        self.add_log(f"处理网页: {result['success_urls']}/{result['total_urls']}")
        self.add_log(f"下载图片: {result['success_images']}/{result['total_images']}")
        self.add_log("---保存位置：桌面/0000图片下载/---")

        if result['errors']:
            self.add_log("\n部分图片下载失败:")
            for error in result['errors'][:10]:
                self.add_log(error)
            if len(result['errors']) > 10:
                self.add_log(f"... 还有 {len(result['errors']) - 10} 个错误")

        self.url_progress_label.setText("网页进度: 完成")
        self.image_progress_label.setText("图片进度: 完成")
