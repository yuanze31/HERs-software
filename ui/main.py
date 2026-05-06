import sys
import os
import atexit
import shutil
import tempfile

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui_main import MainWindow


def cleanup_temp_files():
    if getattr(sys, 'frozen', False):
        import glob
        temp_dir = tempfile.gettempdir()
        mei_dirs = glob.glob(os.path.join(temp_dir, '_MEI*'))
        
        for mei_dir in mei_dirs:
            try:
                if os.path.isdir(mei_dir):
                    shutil.rmtree(mei_dir, ignore_errors=True)
            except Exception:
                pass


def main():
    atexit.register(cleanup_temp_files)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()