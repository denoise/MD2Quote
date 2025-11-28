import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from .ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MD2Angebot")
    
    # Check dependencies
    try:
        import weasyprint
    except OSError as e:
        if "libgobject" in str(e) or "dlopen" in str(e):
            error_msg = (
                "Missing system dependencies for PDF generation (WeasyPrint).\n\n"
                "Please run the following command in your terminal:\n"
                "brew install pango glib gobject-introspection\n\n"
                f"Detailed error: {e}"
            )
            # Using a simple dialog because MainWindow might fail to init if it imports pdf stuff immediately
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Missing System Dependencies")
            msg.setInformativeText(error_msg)
            msg.exec()
            sys.exit(1)
        else:
            raise e
            
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
