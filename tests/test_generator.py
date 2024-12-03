import pytest
from pathlib import Path
import json
import yaml

from shortcuts_doc_generator.doc_generator import DocGenerator

def test_init(doc_generator, test_output_dir):
    """Test generator initialization."""
    assert doc_generator.templates_dir.exists()
    assert doc_generator.output_dir.exists()
    assert doc_generator.jinja_env is not None

def test_default_templates(doc_generator):
    """Test default template creation."""
    assert (doc_generator.templates_dir / 'markdown.md').exists()
    assert (doc_generator.templates_dir / 'html.html').exists()
    
    # Check template content
    md_template = (doc_generator.templates_dir / 'markdown.md').read_text()
    assert '{{ timestamp }}' in md_template
    assert '{{ total_actions }}' in md_template

def test_generate_markdown(doc_generator, sample_shortcut_data, test_output_dir):
    """Test markdown documentation generation."""
    # Process test data
    doc_generator.doc_maker._process_shortcut(sample_shortcut_data)
    
    # Generate documentation
    output_file = doc_generator.generate('markdown')
    assert Path(output_file).exists()
    
    # Check content
    content = Path(output_file).read_text()
    assert '# Apple Shortcuts Documentation' in content
    assert 'Generated on' in content
    assert 'Total Actions:' in content

def test_generate_html(doc_generator, complex_shortcut_data, test_output_dir):
    """Test HTML documentation generation."""
    doc_generator.doc_maker._process_shortcut(complex_shortcut_data)
    
    output_file = doc_generator.generate('html')
    assert Path(output_file).exists()
    
    content = Path(output_file).read_text()
    assert '<!DOCTYPE html>' in content
    assert '<title>Apple Shortcuts Documentation</title>' in content

def test_template_data_preparation(doc_generator, complex_shortcut_data):
    """Test template data preparation."""
    doc_generator.doc_maker._process_shortcut(complex_shortcut_data)
    
    data = doc_generator._prepare_template_data()
    assert 'timestamp' in data
    assert 'total_actions' in data
    assert 'total_variations' in data
    assert 'actions' in data
    assert 'analysis' in data

def test_generate_all_formats(doc_generator, sample_shortcut_data):
    """Test generation of all supported formats."""
    doc_generator.doc_maker._process_shortcut(sample_shortcut_data)
    
    results = doc_generator.generate_all_formats()
    assert 'markdown' in results
    assert 'html' in results
    assert all(Path(file).exists() for file in results.values())

def test_export_data_json(doc_generator, complex_shortcut_data, test_output_dir):
    """Test JSON data export."""
    doc_generator.doc_maker._process_shortcut(complex_shortcut_data)
    
    output_file = doc_generator.export_data('json')
    assert Path(output_file).exists()
    
    # Verify JSON structure
    with open(output_file) as f:
        data = json.load(f)
        assert 'actions' in data
        assert 'metadata' in data
        assert 'analysis' in data

def test_export_data_yaml(doc_generator, complex_shortcut_data, test_output_dir):
    """Test YAML data export."""
    doc_generator.doc_maker._process_shortcut(complex_shortcut_data)
    
    output_file = doc_generator.export_data('yaml')
    assert Path(output_file).exists()
    
    # Verify YAML structure
    with open(output_file) as f:
        data = yaml.safe_load(f)
        assert 'actions' in data
        assert 'metadata' in data
        assert 'analysis' in data

def test_invalid_format(doc_generator):
    """Test handling of invalid format."""
    with pytest.raises(ValueError):
        doc_generator.generate('invalid_format')
    
    with pytest.raises(ValueError):
        doc_generator.export_data('invalid_format')

def test_custom_template(doc_generator, test_output_dir):
    """Test using a custom template."""
    # Create custom template
    custom_template = doc_generator.templates_dir / 'custom.md'
    custom_template.write_text('''# Custom Template
Actions: {{ total_actions }}
{% for action in actions %}
- {{ action.name }}
{% endfor %}
''')
    
    # Generate with custom template
    output_file = doc_generator.generate('custom')
    assert Path(output_file).exists()
    
    content = Path(output_file).read_text()
    assert '# Custom Template' in content
    assert 'Actions:' in content