"""Template directory for documentation generation."""

from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent

# Ensure template directory exists
TEMPLATE_DIR.mkdir(exist_ok=True) 