import sys
import os
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow


def main():
    # Redundant safeguard: Inject Chromium flag into argv if missing
    if sys.platform == "darwin":
        arg = "--disable-features=UseSkiaGraphite"
        if arg not in sys.argv:
            sys.argv.append(arg)

    app = QApplication(sys.argv)
    app.setApplicationName("MD2Angebot")
            
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
