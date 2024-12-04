from typing import Dict, Any, Optional
from pathlib import Path
import json
import markdown
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import yaml

from shortcuts_doc_generator.config import CONFIG, logger
from shortcuts_doc_generator.utils import format_action_name
from shortcuts_doc_generator.shortcut_analyzer import ShortcutAnalyzer

class SetJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle sets."""
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)

class DocGenerator:
    def __init__(self, doc_maker, analyzer=None, output_dir=None):
        """Initialize generator with document maker and optional analyzer."""
        self.doc_maker = doc_maker
        self.analyzer = analyzer or ShortcutAnalyzer(doc_maker)
        self.config = CONFIG
        
        # Set up directories
        self.templates_dir = Path(__file__).parent / 'templates'
        self.output_dir = Path(output_dir) if output_dir else Path(self.config['output']['dir'])
        
        # Create directories
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Define supported template files
        self.template_files = {
            'markdown': 'markdown.md',
            'html': 'html.html',
            'custom': 'custom.md'
        }
        
        # Set up Jinja environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
        
    def _create_default_templates(self):
        """Create default templates if they don't exist."""
        markdown_template = self.templates_dir / 'markdown.md'
        if not markdown_template.exists():
            markdown_template.write_text('''# Apple Shortcuts Documentation
Generated on {{ timestamp }}

## Overview
Total Actions: {{ total_actions }}
Total Variations: {{ total_variations }}

## Actions
{% for action in actions %}
### {{ action.name }}
- Identifier: {{ action.identifier }}
- Parameters: {{ action.parameters|tojson }}
- Examples: {{ action.examples|length }}
{% endfor %}

## Analysis
{{ analysis|tojson(indent=2) }}
''')

        html_template = self.templates_dir / 'html.html'
        if not html_template.exists():
            html_template.write_text('''<!DOCTYPE html>
<html>
<head>
    <title>Apple Shortcuts Documentation</title>
</head>
<body>
    <h1>Apple Shortcuts Documentation</h1>
    <p>Generated on {{ timestamp }}</p>
    
    <h2>Overview</h2>
    <p>Total Actions: {{ total_actions }}</p>
    <p>Total Variations: {{ total_variations }}</p>
    
    <h2>Actions</h2>
    {% for action in actions %}
    <h3>{{ action.name }}</h3>
    <ul>
        <li>Identifier: {{ action.identifier }}</li>
        <li>Parameters: {{ action.parameters|tojson }}</li>
        <li>Examples: {{ action.examples|length }}</li>
    </ul>
    {% endfor %}
    
    <h2>Analysis</h2>
    <pre>{{ analysis|tojson(indent=2) }}</pre>
</body>
</html>
''')
        
    def generate(self, format: str) -> str:
        """Generate documentation in specified format."""
        if format not in self.template_files:
            raise ValueError(f"Unsupported format: {format}")
        
        template_file = self.template_files[format]
        data = self._prepare_template_data()
        
        try:
            template = self.jinja_env.get_template(template_file)
            output = template.render(**data)
            
            output_dir = Path(self.config['output']['dir'])
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"documentation.{format}"
            output_file.write_text(output)
            
            logger.info(f"Generated {format} documentation: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error generating {format} documentation: {e}")
            raise
        
    def _prepare_template_data(self) -> Dict[str, Any]:
        """Prepare data for template rendering."""
        def convert_sets(obj):
            """Convert sets to lists recursively."""
            if isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(i) for i in obj]
            return obj

        # Get analysis results
        analysis = convert_sets(self.analyzer.analyze_all())
        
        # Prepare action data
        actions_data = []
        total_variations = 0
        
        for identifier in sorted(self.doc_maker.known_actions):
            # Convert sets to lists for JSON serialization
            params = sorted(list(self.doc_maker.parameter_types[identifier]))
            versions = sorted(list(self.doc_maker.action_versions[identifier])) if hasattr(self.doc_maker, 'action_versions') else []
            examples = list(self.doc_maker.actions_db[identifier])
            
            action_data = {
                'identifier': identifier,
                'name': format_action_name(identifier),
                'parameters': convert_sets(self.doc_maker.parameter_types[identifier]),
                'examples': convert_sets(self.doc_maker.actions_db[identifier])
            }
            actions_data.append(action_data)
            total_variations += len(action_data['examples'])
        
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
        for format in self.template_files.keys():
            try:
                output_file = self.generate(format)
                results[format] = output_file
                logger.info(f"Generated {format} documentation: {output_file}")
            except Exception as e:
                logger.error(f"Error generating {format} documentation: {e}")
        return results
        
    def _prepare_export_data(self) -> Dict[str, Any]:
        """Prepare data for export."""
        return {
            'actions': [
                {
                    'identifier': action,
                    'name': format_action_name(action),
                    'parameters': list(params)  # Convert sets to lists
                }
                for action, params in self.doc_maker.actions_db.items()
            ],
            'metadata': {
                k: list(v) if isinstance(v, set) else v  # Convert sets to lists
                for k, v in self.doc_maker.metadata.items()
            },
            'analysis': {
                k: list(v) if isinstance(v, set) else v  # Convert sets to lists
                for k, v in self.analyzer.analyze_all().items()
            }
        }

    def export_data(self, format: str) -> str:
        """Export analyzed data in specified format."""
        if format not in ['json', 'yaml']:
            raise ValueError(f"Unsupported export format: {format}")
        
        data = self._prepare_export_data()
        data = self._convert_complex_types(data)  # Convert sets and tuples
        
        output_dir = self.output_dir
        output_file = output_dir / f"shortcuts_data.{format}"
        
        with open(output_file, 'w') as f:
            if format == 'json':
                json.dump(data, f, indent=2, cls=SetJSONEncoder)
            else:  # yaml
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Exported data: {output_file}")
        return str(output_file)

    def _convert_complex_types(self, obj):
        """Recursively convert sets and tuples to lists in nested structures."""
        if isinstance(obj, (set, tuple)):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_complex_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_complex_types(i) for i in obj]
        return obj 