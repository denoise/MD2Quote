
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path.cwd() / "src"))

from md2quote.core.renderer import TemplateRenderer
from md2quote.core.config import config

try:
    pass
except Exception as e:
    print(f"Config setup error: {e}")

def test_render():
    print("Initializing Renderer...")
    renderer = TemplateRenderer()
    print(f"Renderer env cache: {renderer.env.cache}")
    
    context = {
        "content": "<h1>Hello</h1>",
        "company": {"name": "Test Co"}
    }
    
    print("Calling render...")
    try:
        renderer.render("base", context)
        print("Render success")
    except AttributeError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_render()
