import pytest
from pathlib import Path
import json
from collections import defaultdict
import networkx as nx

from shortcuts_doc_generator.shortcut_analyzer import ShortcutAnalyzer

def test_init(analyzer):
    """Test analyzer initialization."""
    assert isinstance(analyzer.action_graph, nx.DiGraph)
    assert isinstance(analyzer.common_patterns, defaultdict)
    assert isinstance(analyzer.action_frequencies, defaultdict)
    assert isinstance(analyzer.parameter_frequencies, defaultdict)

def test_analyze_action_flows(analyzer, complex_shortcut_data):
    """Test action flow analysis."""
    # Process test data first
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    
    flows = analyzer.analyze_action_flows()
    assert 'most_common_sequences' in flows
    assert 'central_actions' in flows
    assert 'isolated_actions' in flows
    
    # Check graph construction
    assert len(analyzer.action_graph.nodes) > 0
    assert len(analyzer.action_graph.edges) > 0

def test_common_patterns(analyzer, complex_shortcut_data):
    """Test pattern detection."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    patterns = analyzer.find_common_patterns()
    
    # Verify pattern structure
    for length, pattern_list in patterns.items():
        assert isinstance(int(length), int)
        for pattern in pattern_list:
            assert 'actions' in pattern
            assert 'frequency' in pattern
            assert isinstance(pattern['frequency'], int)

def test_parameter_usage(analyzer, sample_shortcut_data):
    """Test parameter usage analysis."""
    analyzer.doc_maker._process_shortcut(sample_shortcut_data)
    usage = analyzer.analyze_parameter_usage()
    
    # Check first action's parameters
    first_action = sample_shortcut_data['WFWorkflowActions'][0]['WFWorkflowActionIdentifier']
    assert first_action in usage
    assert isinstance(usage[first_action], dict)
    assert len(usage[first_action]) > 0

def test_version_distribution(analyzer, complex_shortcut_data):
    """Test version distribution analysis."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    distribution = analyzer.analyze_version_distribution()
    
    # Check version data
    assert len(distribution) > 0
    for version, actions in distribution.items():
        assert isinstance(actions, list)
        assert all(isinstance(action, str) for action in actions)

def test_menu_complexity(analyzer, complex_shortcut_data):
    """Test menu complexity analysis."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    complexity = analyzer.analyze_menu_complexity()
    
    assert 'total_menus' in complexity
    assert 'avg_items' in complexity
    assert 'max_items' in complexity
    assert 'nested_menus' in complexity

def test_central_actions(analyzer, complex_shortcut_data):
    """Test identification of central actions."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    flows = analyzer.analyze_action_flows()
    central = dict(flows['central_actions'])
    
    # Check PageRank scores
    assert len(central) > 0
    assert all(isinstance(score, float) for score in central.values())
    assert all(0 <= score <= 1 for score in central.values())

def test_isolated_actions(analyzer, sample_shortcut_data):
    """Test identification of isolated actions."""
    analyzer.doc_maker._process_shortcut(sample_shortcut_data)
    flows = analyzer.analyze_action_flows()
    isolated = flows['isolated_actions']
    
    # Verify isolated actions
    assert isinstance(isolated, set)
    for action in isolated:
        assert action not in analyzer.action_graph.nodes

def test_analyze_all(analyzer, complex_shortcut_data):
    """Test comprehensive analysis."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    results = analyzer.analyze_all()
    
    assert 'action_flows' in results
    assert 'common_patterns' in results
    assert 'parameter_usage' in results
    assert 'version_distribution' in results
    assert 'menu_complexity' in results

def test_visualization_generation(analyzer, complex_shortcut_data, test_output_dir):
    """Test visualization generation."""
    analyzer.doc_maker._process_shortcut(complex_shortcut_data)
    
    # Configure visualization directory
    vis_dir = test_output_dir / 'visualizations'
    vis_dir.mkdir(exist_ok=True)
    
    # Generate visualizations
    analyzer.generate_visualizations()
    
    # Check for generated files
    assert (vis_dir / 'action_flow.png').exists()
    assert (vis_dir / 'version_distribution.png').exists()