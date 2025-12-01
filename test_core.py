import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from md2quote.core.parser import MarkdownParser
from md2quote.core.renderer import TemplateRenderer
from md2quote.core.config import config

def test_pipeline():
    parser = MarkdownParser()
    example_path = "examples/programming.md"
    if not os.path.exists(example_path):
        print("Example file not found!")
        return

    metadata, html_body = parser.parse_file(example_path)
    print("Metadata parsed:", metadata.keys())
    
    renderer = TemplateRenderer()
    import yaml
    with open("examples/config.yaml", 'r') as f:
        config.config = yaml.safe_load(f)
        
    print("Testing Logo Path Resolution:")
    code_logo = config.resolve_path('assets/images/logo_code.svg')
    print(f"Code Logo: {code_logo}")
    
    if not code_logo:
        print("ERROR: Code logo not resolved!")
        
    context = {
        **metadata,
        "content": html_body
    }
    
    final_html = renderer.render(metadata.get("template", "base"), context)
    print("HTML generated, length:", len(final_html))

if __name__ == "__main__":
    test_pipeline()
