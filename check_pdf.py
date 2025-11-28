try:
    from PyQt6.QtPdfWidgets import QPdfView
    print("QPdfView available")
except ImportError as e:
    print(f"QPdfView NOT available: {e}")
