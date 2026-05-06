import os
import sys

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QTextEdit, QVBoxLayout)

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tabs.base_tab import BaseTab
from tabs.registry import register_tab
from utils.resizer import ImageResizer


class ResizeWorker(QThread):
    progress_updated = pyqtSignal(int, int, int)
    finished = pyqtSignal(dict)
    file_processed = pyqtSignal(str, bool, str)

    def __init__(self, folder_path, target_width):
        super().__init__()
        self.folder_path = folder_path
        self.target_width = target_width

    def run(self):
        try:
            resizer = ImageResizer()
            result = resizer.process_images(
                    self.folder_path,
                    self.target_width,
                    self.on_progress,
                    self.on_file_processed
                    )
            result['target_width'] = self.target_width
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({
                    'success': False,
                    'message': f"处理过程发生未预期错误: {str(e)}",
                    'total': 0,
                    'processed_count': 0,
                    'output_dir': '',
                    'target_width': self.target_width,
                    'errors': [f"致命错误: {str(e)}"]
                    })

    def on_progress(self, current, total, processed_count):
        self.progress_updated.emit(current, total, processed_count)

    def on_file_processed(self, filename, success, error_msg=None):
        self.file_processed.emit(filename, success, error_msg if error_msg else "")


@register_tab("图片处理")
class ImageResizeTab(BaseTab):
    def __init__(self):
        self.tab_name = "图片处理"
        super().__init__()
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(10)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("请选择图片所在文件夹")
        self.folder_input.setReadOnly(True)
        self.folder_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
        """)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_folder)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_btn)
        layout.addLayout(folder_layout)

        width_layout = QHBoxLayout()
        width_layout.setSpacing(10)

        width_label = QLabel("目标宽度:")
        width_label.setStyleSheet("font-size: 14px;")

        self.width_input = QLineEdit()
        self.width_input.setText("680")
        self.width_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                width: 100px;
            }
            QLineEdit:focus {
                border-color: #4a90d9;
                outline: none;
            }
        """)

        self.process_btn = QPushButton("开始处理")
        self.process_btn.clicked.connect(self.start_process)
        self.process_btn.setStyleSheet("""
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

        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_input)
        width_layout.addStretch()
        width_layout.addWidget(self.process_btn)
        layout.addLayout(width_layout)

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
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

        self.progress_label = QLabel("等待选择文件夹...")
        self.progress_label.setStyleSheet("font-size: 12px; color: #666;")

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

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

    def add_log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder_path:
            self.folder_input.setText(folder_path)

    def start_process(self):
        folder_path = self.folder_input.text().strip()
        if not folder_path or not os.path.isdir(folder_path):
            self.add_log("请选择有效的文件夹")
            return

        try:
            target_width = int(self.width_input.text().strip())
            if target_width <= 0:
                raise ValueError("宽度必须大于0")
        except ValueError:
            self.add_log("请输入有效的宽度数值")
            return

        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("等待选择文件夹...")
        self.log_text.clear()
        self.add_log(f"处理文件夹: {folder_path}")
        self.add_log(f"目标宽度: {target_width}px")

        self.worker = ResizeWorker(folder_path, target_width)
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.file_processed.connect(self.on_file_processed)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()

    def on_progress(self, current, total, processed_count):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"进度: {current}/{total} (成功: {processed_count})")

    def on_file_processed(self, filename, success, error_msg):
        if success:
            self.add_log(f"✓ {filename}")
        else:
            self.add_log(f"✗ {filename}: {error_msg}")

    def on_process_finished(self, result):
        self.process_btn.setEnabled(True)

        if not result['success']:
            self.add_log(f"错误: {result['message']}")
            self.progress_label.setText("处理失败")
            return

        target_width = result.get('target_width', 680)
        self.add_log(f"找到 {result['total']} 个图像文件")
        self.add_log(f"成功处理 {result['processed_count']}/{result['total']} 个文件")
        self.add_log(f"结果已保存到: {result['output_dir']}")
        self.add_log(f"---当前目录下 output_{target_width} 文件夹---")

        if result['errors']:
            self.add_log("\n部分文件处理失败:")
            for error in result['errors'][:10]:
                self.add_log(error)
            if len(result['errors']) > 10:
                self.add_log(f"... 还有 {len(result['errors']) - 10} 个错误")

        self.progress_label.setText("处理完成")
