import pytest
from pathlib import Path
import json
import tempfile
import shutil
from typing import Dict, Any

from shortcuts_doc_generator.shortcut_doc_maker import ShortcutDocMaker
from shortcuts_doc_generator.shortcut_analyzer import ShortcutAnalyzer
from shortcuts_doc_generator.doc_generator import DocGenerator

@pytest.fixture
def sample_shortcut_data() -> Dict[str, Any]:
    """Provide sample shortcut data for testing."""
    return {
        "WFWorkflowActions": [
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.text",
                "WFWorkflowActionParameters": {
                    "UUID": "test-uuid-1",
                    "WFTextActionText": "Hello World"
                }
            },
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
                "WFWorkflowActionParameters": {
                    "UUID": "test-uuid-2"
                }
            }
        ],
        "WFWorkflowClientVersion": "1200",
        "WFWorkflowTypes": ["NCWidget"],
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4282601983,
            "WFWorkflowIconGlyphNumber": 59511
        }
    }

@pytest.fixture
def sample_shortcut_file(tmp_path: Path, sample_shortcut_data: Dict[str, Any]) -> Path:
    """Create a temporary shortcut file for testing."""
    shortcut_file = tmp_path / "test_shortcut.json"
    with open(shortcut_file, 'w') as f:
        json.dump(sample_shortcut_data, f)
    return shortcut_file

@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir

@pytest.fixture
def doc_maker(test_output_dir: Path) -> ShortcutDocMaker:
    """Provide a configured ShortcutDocMaker instance."""
    return ShortcutDocMaker()

@pytest.fixture
def analyzer(doc_maker: ShortcutDocMaker) -> ShortcutAnalyzer:
    """Provide a configured ShortcutAnalyzer instance."""
    return ShortcutAnalyzer(doc_maker)

@pytest.fixture
def doc_generator(doc_maker: ShortcutDocMaker, analyzer: ShortcutAnalyzer, 
                 test_output_dir: Path) -> DocGenerator:
    """Provide a configured DocGenerator instance."""
    return DocGenerator(doc_maker, analyzer)

@pytest.fixture
def complex_shortcut_data() -> Dict[str, Any]:
    """Provide more complex shortcut data for advanced testing."""
    return {
        "WFWorkflowActions": [
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
                "WFWorkflowActionParameters": {
                    "UUID": "menu-uuid-1",
                    "GroupingIdentifier": "menu-group-1",
                    "WFMenuPrompt": "Select an option",
                    "WFMenuItems": ["Option 1", "Option 2", "Option 3"]
                }
            },
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
                "WFWorkflowActionParameters": {
                    "UUID": "condition-uuid-1",
                    "GroupingIdentifier": "condition-group-1",
                    "WFCondition": "Equals",
                    "WFConditionalActionString": "Option 1"
                }
            }
        ],
        "WFWorkflowClientVersion": "1250",
        "WFWorkflowMinimumClientVersion": 1200,
        "WFWorkflowTypes": ["WatchKit", "NCWidget"],
        "WFQuickActionSurfaces": ["WatchKit", "NCWidget"]
    }

@pytest.fixture
def sample_database(test_output_dir: Path) -> Path:
    """Create a sample database file for testing."""
    db_file = test_output_dir / "test_shortcuts_db.json"
    sample_data = {
        "actions_db": {},
        "metadata": {},
        "known_actions": [],
        "uuid_map": {},
        "group_map": {},
        "action_flows": {},
        "parameter_types": {},
        "action_relationships": {},
        "menu_structures": {},
        "action_versions": {}
    }
    with open(db_file, 'w') as f:
        json.dump(sample_data, f)
    return db_file

@pytest.fixture
def cleanup_files(request):
    """Cleanup temporary files after tests."""
    def cleanup():
        # Clean up any temporary files created during tests
        if hasattr(request, "node"):
            test_path = Path(request.node.fspath).parent
            temp_files = test_path.glob("test_*")
            for file in temp_files:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
    
    request.addfinalizer(cleanup)