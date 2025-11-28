import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Fix for macOS + Homebrew: explicitly add Homebrew lib path for cffi/weasyprint
if sys.platform == "darwin":
    # Common Homebrew paths
    homebrew_paths = ["/opt/homebrew/lib", "/usr/local/lib"]
    for path in homebrew_paths:
        if os.path.exists(path):
            # Add to DYLD_FALLBACK_LIBRARY_PATH
            current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{path}:{current_dyld}"
            break

from md2angebot.main import main

if __name__ == "__main__":
    main()

