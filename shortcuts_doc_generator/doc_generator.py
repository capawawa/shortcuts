from typing import Dict, Any, Optional
from pathlib import Path
import json
import markdown
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import yaml

from config import CONFIG, logger
from utils import format_action_name

class DocGenerator:
    def __init__(self, doc_maker, analyzer):
        """Initialize with references to DocMaker and Analyzer instances."""
        self.doc_maker = doc_maker
        self.analyzer = analyzer
        self.templates_dir = Path('templates')
        self.output_dir = Path(CONFIG['output']['dir'])
        
        # Ensure template directory exists
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
        
    def _create_default_templates(self):
        """Create default templates if they don't exist."""
        default_templates = {
            'markdown.md': '''# Apple Shortcuts Documentation
Generated on {{ timestamp }}

## Overview
Total Actions: {{ total_actions }}
Total Parameter Variations: {{ total_variations }}

## Actions
{% for action in actions %}
### {{ action.name }}
**Identifier**: `{{ action.identifier }}`
**Versions**: {{ action.versions|join(', ') }}

#### Parameters:
{% for param in action.parameters %}
- {{ param }}
{% endfor %}

{% if action.examples %}
#### Examples:
```json
{{ action.examples }}
```
{% endif %}
{% endfor %}
''',
            'html.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Apple Shortcuts Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .action { margin-bottom: 30px; }
        .parameters { margin-left: 20px; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Apple Shortcuts Documentation</h1>
    <p>Generated on {{ timestamp }}</p>
    
    <h2>Overview</h2>
    <p>Total Actions: {{ total_actions }}</p>
    <p>Total Parameter Variations: {{ total_variations }}</p>
    
    <h2>Actions</h2>
    {% for action in actions %}
    <div class="action">
        <h3>{{ action.name }}</h3>
        <p><strong>Identifier:</strong> <code>{{ action.identifier }}</code></p>
        <p><strong>Versions:</strong> {{ action.versions|join(', ') }}</p>
        
        <h4>Parameters:</h4>
        <ul class="parameters">
        {% for param in action.parameters %}
            <li>{{ param }}</li>
        {% endfor %}
        </ul>
        
        {% if action.examples %}
        <h4>Examples:</h4>
        <pre><code>{{ action.examples }}</code></pre>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
'''
        }
        
        for filename, content in default_templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content)
                logger.info(f"Created default template: {filename}")
                
    def generate(self, format: str = 'markdown', output_file: Optional[str] = None) -> str:
        """Generate documentation in specified format."""
        if format not in CONFIG['output']['formats']:
            raise ValueError(f"Unsupported format: {format}")
            
        # Prepare data for templates
        template_data = self._prepare_template_data()
        
        # Get appropriate template
        template = self.jinja_env.get_template(f'{format}.{format}')
        
        # Generate content
        content = template.render(**template_data)
        
        # Determine output file
        if output_file is None:
            output_file = self.output_dir / f'shortcuts_documentation.{format}'
        else:
            output_file = Path(output_file)
            
        # Save content
        output_file.write_text(content)
        logger.info(f"Generated documentation: {output_file}")
        
        return str(output_file)
        
    def _prepare_template_data(self) -> Dict[str, Any]:
        """Prepare data for template rendering."""
        actions_data = []
        total_variations = 0
        
        for identifier in sorted(self.doc_maker.known_actions):
            action_data = {
                'identifier': identifier,
                'name': format_action_name(identifier),
                'versions': sorted(self.doc_maker.action_versions[identifier]),
                'parameters': sorted(self.doc_maker.parameter_types[identifier]),
                'examples': json.dumps(self.doc_maker.actions_db[identifier], indent=2)
                if self.doc_maker.actions_db[identifier] else None
            }
            actions_data.append(action_data)
            total_variations += len(self.doc_maker.actions_db[identifier])
            
        # Get analysis results
        analysis = self.analyzer.analyze_all()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_actions': len(self.doc_maker.known_actions),
            'total_variations': total_variations,
            'actions': actions_data,
            'analysis': analysis
        }
        
    def generate_all_formats(self) -> Dict[str, str]:
        """Generate documentation in all supported formats."""
        results = {}
        for format in CONFIG['output']['formats']:
            try:
                output_file = self.generate(format)
                results[format] = output_file
            except Exception as e:
                logger.error(f"Error generating {format} documentation: {e}")
                results[format] = str(e)
        return results
        
    def export_data(self, format: str = 'json') -> str:
        """Export raw data in specified format."""
        data = {
            'actions': self.doc_maker.actions_db,
            'metadata': self.doc_maker.metadata,
            'analysis': self.analyzer.analyze_all()
        }
        
        output_file = self.output_dir / f'shortcuts_data.{format}'
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'yaml':
            with open(output_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        logger.info(f"Exported data: {output_file}")
        return str(output_file) 