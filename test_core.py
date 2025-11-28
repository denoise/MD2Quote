import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md2angebot.core.parser import MarkdownParser
from md2angebot.core.renderer import TemplateRenderer
from md2angebot.core.config import config

def test_pipeline():
    # 1. Parse
    parser = MarkdownParser()
    # Use one of the examples
    example_path = "examples/programming.md"
    if not os.path.exists(example_path):
        print("Example file not found!")
        return

    metadata, html_body = parser.parse_file(example_path)
    print("Metadata parsed:", metadata.keys())
    
    # 2. Render
    renderer = TemplateRenderer()
    # Mock config loading for test if needed, or rely on default/fallback
    # Since we haven't set up the user config dir with real files, config might be empty
    # But we can manually inject the example config for testing
    import yaml
    with open("examples/config.yaml", 'r') as f:
        config.config = yaml.safe_load(f)
        
    context = {
        **metadata,
        "content": html_body
    }
    
    final_html = renderer.render(metadata.get("template", "base"), context)
    print("HTML generated, length:", len(final_html))
    
    # 3. Generate PDF (optional for this quick test as it requires weasyprint deps)
    # from md2angebot.core.pdf import PDFGenerator
    # gen = PDFGenerator()
    # gen.generate(final_html, "test_output.pdf")
    # print("PDF generated")

if __name__ == "__main__":
    test_pipeline()

