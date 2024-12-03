import pytest
from pathlib import Path
import json

from shortcuts_doc_generator.utils import (
    load_json_file,
    save_json_file,
    get_file_list,
    validate_shortcut_version,
    format_action_name,
    ShortcutError
)

def test_load_json_file(tmp_path):
    """Test JSON file loading."""
    test_file = tmp_path / "test.json"
    test_data = {"test": "data"}
    
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    loaded_data = load_json_file(test_file)
    assert loaded_data == test_data

def test_load_invalid_json(tmp_path):
    """Test loading invalid JSON file."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json")
    
    with pytest.raises(ShortcutError):
        load_json_file(invalid_file)

def test_save_json_file(tmp_path):
    """Test JSON file saving."""
    test_file = tmp_path / "save_test.json"
    test_data = {"save": "test"}
    
    save_json_file(test_data, test_file)
    
    with open(test_file) as f:
        saved_data = json.load(f)
    assert saved_data == test_data

def test_get_file_list(tmp_path):
    """Test file list retrieval."""
    # Create test directory structure
    (tmp_path / "test1.json").touch()
    (tmp_path / "test2.json").touch()
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test3.json").touch()
    
    files = list(get_file_list(tmp_path))
    assert len(files) == 3
    assert all(f.suffix == '.json' for f in files)

def test_validate_shortcut_version():
    """Test shortcut version validation."""
    valid_data = {
        "WFWorkflowClientVersion": "1200",
        "WFWorkflowMinimumClientVersion": 1000
    }
    version = validate_shortcut_version(valid_data)
    assert version == "1200"
    
    invalid_data = {}
    with pytest.raises(ShortcutError):
        validate_shortcut_version(invalid_data)

def test_format_action_name():
    """Test action name formatting."""
    test_cases = [
        ("is.workflow.actions.text", "Text"),
        ("is.workflow.actions.showresult", "Show Result"),
        ("is.workflow.actions.choosefrommenu", "Choose from Menu"),
        ("com.apple.shortcuts.GetURLAction", "Get URL")
    ]
    
    for input_name, expected in test_cases:
        assert format_action_name(input_name) == expected

def test_format_invalid_action_name():
    """Test formatting of invalid action names."""
    invalid_names = [None, "", "invalid.format"]
    for name in invalid_names:
        with pytest.raises(ShortcutError):
            format_action_name(name)

def test_recursive_file_search(tmp_path):
    """Test recursive file search functionality."""
    # Create nested directory structure
    level1 = tmp_path / "level1"
    level2 = level1 / "level2"
    level1.mkdir()
    level2.mkdir()
    
    (tmp_path / "root.json").touch()
    (level1 / "test1.json").touch()
    (level2 / "test2.json").touch()
    
    files = list(get_file_list(tmp_path, recursive=True))
    assert len(files) == 3
    
    files = list(get_file_list(tmp_path, recursive=False))
    assert len(files) == 1

def test_file_filtering(tmp_path):
    """Test file filtering by extension."""
    (tmp_path / "test.json").touch()
    (tmp_path / "test.txt").touch()
    (tmp_path / "test.py").touch()
    
    json_files = list(get_file_list(tmp_path))
    assert len(json_files) == 1
    assert json_files[0].suffix == '.json'