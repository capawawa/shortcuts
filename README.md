# Shortcuts Documentation Generator

[![Python Tests](https://github.com/capawawa/shortcuts/actions/workflows/python-tests.yml/badge.svg)](https://github.com/capawawa/shortcuts/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful tool for analyzing, documenting, and visualizing Apple Shortcuts workflows. This project helps developers and users understand complex shortcuts by generating detailed documentation, analyzing patterns, and creating visual representations of action flows.

## 🌟 Features

### Documentation Generation

- Comprehensive markdown and HTML documentation
- Parameter usage analysis
- Version compatibility tracking
- Action relationship mapping

### Analysis Tools

- Action flow visualization
- Common pattern detection
- Menu complexity analysis
- Parameter usage statistics
- Version distribution analysis

### Visualization

- Action flow diagrams
- Version distribution charts
- Parameter usage heatmaps
- Menu structure visualization

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/capawawa/shortcuts.git
cd shortcuts

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .
```

## 📖 Usage

### Command Line Interface

```bash
# Generate documentation for a single shortcut
shortcuts-doc generate path/to/shortcut.json

# Analyze multiple shortcuts
shortcuts-doc analyze path/to/shortcuts/directory

# Generate visualizations
shortcuts-doc visualize path/to/shortcut.json

# Export data in different formats
shortcuts-doc export path/to/shortcut.json --format json
```

### Python API

```python
from shortcut_doc_maker import ShortcutDocMaker
from shortcut_analyzer import ShortcutAnalyzer
from doc_generator import DocGenerator

# Process a shortcut
doc_maker = ShortcutDocMaker()
doc_maker.process_shortcut("path/to/shortcut.json")

# Analyze patterns
analyzer = ShortcutAnalyzer(doc_maker)
results = analyzer.analyze_all()

# Generate documentation
generator = DocGenerator(doc_maker)
generator.generate("markdown")
```

## 🔧 Configuration

Configuration can be customized through:

- Command line arguments
- Configuration file (`config.py`)
- Environment variables

### Example Configuration

```python
CONFIG = {
    'output_dir': 'docs/',
    'template_dir': 'templates/',
    'analysis_depth': 3,
    'visualization': {
        'format': 'png',
        'dpi': 300
    }
}
```

## 📊 Output Examples

### Documentation

- Markdown files with action details
- HTML documentation with interactive elements
- JSON/YAML data exports

### Visualizations

- Action flow diagrams (PNG/SVG)
- Statistical charts
- Relationship graphs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Apple Shortcuts community
- Contributors and testers
- Open source libraries used in this project

## 📫 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)
Project Link: [https://github.com/yourusername/shortcuts-doc-generator](https://github.com/yourusername/shortcuts-doc-generator)
