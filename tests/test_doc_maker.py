import pytest
from pathlib import Path
import json
from collections import defaultdict

from shortcuts_doc_generator.shortcut_doc_maker import ShortcutDocMaker
from shortcuts_doc_generator.utils import ShortcutError

def test_init(doc_maker):
    """Test initialization of ShortcutDocMaker."""
    assert isinstance(doc_maker.actions_db, defaultdict)
    assert isinstance(doc_maker.metadata, defaultdict)
    assert isinstance(doc_maker.known_actions, set)
    assert isinstance(doc_maker.new_actions, set)
    assert isinstance(doc_maker.uuid_map, dict)
    assert isinstance(doc_maker.group_map, defaultdict)
    assert isinstance(doc_maker.action_flows, defaultdict)
    assert isinstance(doc_maker.parameter_types, defaultdict)
    assert isinstance(doc_maker.action_relationships, defaultdict)
    assert isinstance(doc_maker.menu_structures, defaultdict)

def test_process_shortcut_file(doc_maker, sample_shortcut_file):
    """Test processing a single shortcut file."""
    doc_maker.process_shortcut_file(sample_shortcut_file)
    
    # Check that file was processed
    assert len(doc_maker.known_actions) > 0
    assert len(doc_maker.metadata) > 0

def test_process_action(doc_maker, complex_shortcut_data):
    """Test processing individual actions."""
    action = complex_shortcut_data['WFWorkflowActions'][0]
    doc_maker._process_action(action, 0, 2)
    
    identifier = action['WFWorkflowActionIdentifier']
    assert identifier in doc_maker.known_actions
    
    # Check UUID mapping
    uuid = action['WFWorkflowActionParameters'].get('UUID')
    if uuid:
        assert doc_maker.uuid_map[uuid] == identifier

def test_action_flow_tracking(doc_maker, sample_shortcut_data):
    """Test tracking of action flows."""
    actions = sample_shortcut_data['WFWorkflowActions']
    if len(actions) >= 2:
        first = actions[0]['WFWorkflowActionIdentifier']
        second = actions[1]['WFWorkflowActionIdentifier']
        
        doc_maker._process_action(actions[0], 0, 2)
        doc_maker._process_action(actions[1], 1, 2)
        
        assert second in doc_maker.action_flows[first]
        assert second in doc_maker.action_relationships[first]

def test_menu_structure_tracking(doc_maker, complex_shortcut_data):
    """Test tracking of menu structures."""
    menu_action = next(
        action for action in complex_shortcut_data['WFWorkflowActions']
        if action['WFWorkflowActionIdentifier'] == 'is.workflow.actions.choosefrommenu'
    )
    doc_maker._process_action(menu_action, 0, 1)
    
    group_id = menu_action['WFWorkflowActionParameters']['GroupingIdentifier']
    assert group_id in doc_maker.menu_structures
    assert 'items' in doc_maker.menu_structures[group_id]
    assert 'prompt' in doc_maker.menu_structures[group_id]

def test_parameter_tracking(doc_maker, sample_shortcut_data):
    """Test parameter tracking."""
    action = sample_shortcut_data['WFWorkflowActions'][0]
    doc_maker._process_action(action, 0, 1)
    
    identifier = action['WFWorkflowActionIdentifier']
    assert len(doc_maker.parameter_types[identifier]) > 0
    assert len(doc_maker.actions_db[identifier]) > 0

def test_error_handling(doc_maker):
    """Test error handling."""
    with pytest.raises(ShortcutError):
        doc_maker._process_action({}, 0, 1)
    
    with pytest.raises(ShortcutError):
        doc_maker.process_shortcut_file(Path('nonexistent.json'))

def test_duplicate_handling(doc_maker, sample_shortcut_data):
    """Test handling of duplicate parameters."""
    action = sample_shortcut_data['WFWorkflowActions'][0]
    
    # Process same action twice
    doc_maker._process_action(action, 0, 1)
    doc_maker._process_action(action, 0, 1)
    
    identifier = action['WFWorkflowActionIdentifier']
    # Should only store unique parameter combinations
    assert len(doc_maker.actions_db[identifier]) == 1