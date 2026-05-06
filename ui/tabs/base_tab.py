from PyQt6.QtWidgets import QWidget


class BaseTab(QWidget):
    def __init__(self):
        super().__init__()
        self.tab_name = "未命名"
        self.init_ui()

    def init_ui(self):
        """由子类实现"""
        raise NotImplementedError("子类必须实现 init_ui 方法")

    def get_tab_name(self):
        return self.tab_name

    def on_show(self):
        """Tab显示时调用，可由子类重写"""
        pass

    def on_hide(self):
        """Tab隐藏时调用，可由子类重写"""
        pass
