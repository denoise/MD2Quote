import sys
import os
from pathlib import Path

if sys.platform == "darwin":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-features=UseSkiaGraphite"

sys.path.insert(0, str(Path(__file__).parent / "src"))

if sys.platform == "darwin":
    homebrew_paths = ["/opt/homebrew/lib", "/usr/local/lib"]
    for path in homebrew_paths:
        if os.path.exists(path):
            current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{path}:{current_dyld}"
            break

from md2angebot.main import main

if __name__ == "__main__":
    main()

