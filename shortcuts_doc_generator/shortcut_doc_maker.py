from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from pathlib import Path
import json

from config import CONFIG, logger
from utils import (
    load_json_file, 
    save_json_file, 
    get_file_list, 
    validate_shortcut_version, 
    format_action_name,
    ShortcutError
)

class ShortcutDocMaker:
    def __init__(self):
        """Initialize the documentation maker with empty data structures."""
        # Core data structures
        self.actions_db = defaultdict(list)  # Store action parameters
        self.metadata = defaultdict(set)     # Store metadata
        self.known_actions = set()           # Track unique actions
        self.new_actions = set()             # Track newly discovered actions
        
        # Enhanced tracking
        self.uuid_map = {}                   # Map UUIDs to actions
        self.group_map = defaultdict(list)   # Track action groups
        self.action_flows = defaultdict(list) # Track action sequences
        self.parameter_types = defaultdict(set) # Track parameter data types
        self.action_relationships = defaultdict(set) # Track related actions
        self.menu_structures = defaultdict(dict)    # Track menu hierarchies
        self.action_versions = defaultdict(set)     # Track version information
        
        # Load existing database
        self.load_database()
        
    def load_database(self) -> None:
        """Load existing database if it exists."""
        db_file = Path(CONFIG['database']['file'])
        if db_file.exists():
            try:
                data = load_json_file(db_file)
                self._populate_from_data(data)
                logger.info(f"Loaded {len(self.known_actions)} known actions from database")
            except ShortcutError as e:
                logger.error(f"Error loading database: {e}")
                logger.info("Starting with empty database")
        else:
            logger.info("No existing database found. Starting fresh.")
            
    def _populate_from_data(self, data: Dict[str, Any]) -> None:
        """Populate internal structures from loaded data."""
        self.actions_db = defaultdict(list, data.get('actions_db', {}))
        self.metadata = defaultdict(set, {k: set(v) for k, v in data.get('metadata', {}).items()})
        self.known_actions = set(data.get('known_actions', []))
        self.uuid_map = data.get('uuid_map', {})
        self.group_map = defaultdict(list, data.get('group_map', {}))
        self.action_flows = defaultdict(list, data.get('action_flows', {}))
        self.parameter_types = defaultdict(set, {k: set(v) for k, v in data.get('parameter_types', {}).items()})
        self.action_relationships = defaultdict(set, {k: set(v) for k, v in data.get('action_relationships', {}).items()})
        self.menu_structures = defaultdict(dict, data.get('menu_structures', {}))
        self.action_versions = defaultdict(set, {k: set(v) for k, v in data.get('action_versions', {}).items()})
        
    def save_database(self) -> None:
        """Save current state to database file."""
        save_data = {
            'actions_db': dict(self.actions_db),
            'metadata': {k: list(v) for k, v in self.metadata.items()},
            'known_actions': list(self.known_actions),
            'uuid_map': self.uuid_map,
            'group_map': dict(self.group_map),
            'action_flows': dict(self.action_flows),
            'parameter_types': {k: list(v) for k, v in self.parameter_types.items()},
            'action_relationships': {k: list(v) for k, v in self.action_relationships.items()},
            'menu_structures': dict(self.menu_structures),
            'action_versions': {k: list(v) for k, v in self.action_versions.items()}
        }
        
        db_file = Path(CONFIG['database']['file'])
        save_json_file(save_data, db_file)
        
    def process_input(self, input_path: str) -> Dict[str, Any]:
        """Process either a single file or directory of shortcuts."""
        results = {
            'processed_files': [],
            'new_actions': set(),
            'errors': []
        }
        
        try:
            input_path = Path(input_path)
            if input_path.is_file():
                self._process_single_file(input_path, results)
            elif input_path.is_dir():
                for file_path in get_file_list(input_path):
                    self._process_single_file(file_path, results)
            else:
                results['errors'].append(f"Invalid path: {input_path}")
                
        except Exception as e:
            results['errors'].append(f"Unexpected error: {str(e)}")
            logger.exception("Error processing input")
            
        return results
    
    def _process_single_file(self, file_path: Path, results: Dict[str, Any]) -> None:
        """Process a single shortcut file and update results."""
        try:
            logger.info(f"Processing {file_path}")
            data = load_json_file(file_path)
            
            # Store initial state for comparison
            actions_before = set(self.known_actions)
            
            # Process the shortcut
            self._process_shortcut(data)
            
            # Update results
            results['processed_files'].append(str(file_path))
            new_actions = set(self.known_actions) - actions_before
            results['new_actions'].update(new_actions)
            
            if new_actions:
                logger.info(f"Found {len(new_actions)} new actions")
            
        except ShortcutError as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
            
    def _process_shortcut(self, data: Dict[str, Any]) -> None:
        """Process shortcut data and extract all relevant information."""
        # Extract version information
        version = validate_shortcut_version(data)
        
        # Extract metadata
        self._extract_metadata(data)
        
        # Process actions
        actions = data.get('WFWorkflowActions', [])
        total_actions = len(actions)
        
        for index, action in enumerate(actions):
            self._process_action(action, index, total_actions, version)
            
    def _extract_metadata(self, data: Dict[str, Any]) -> None:
        """Extract and store metadata from shortcut."""
        metadata_keys = [
            'WFWorkflowMinimumClientVersion',
            'WFWorkflowMinimumClientVersionString',
            'WFWorkflowClientVersion',
            'WFWorkflowIcon',
            'WFWorkflowTypes',
            'WFWorkflowOutputContentItemClasses',
            'WFQuickActionSurfaces'
        ]
        
        for key in metadata_keys:
            if key in data:
                value = data[key]
                if isinstance(value, (list, dict)):
                    self.metadata[key].update(json.dumps(value))
                else:
                    self.metadata[key].add(str(value))

    def _process_action(self, action: Dict[str, Any], index: int, total: int, version: Optional[str]) -> None:
        """Process a single action and its parameters."""
        identifier = action.get('WFWorkflowActionIdentifier')
        if not identifier:
            return
            
        # Track new actions
        if identifier not in self.known_actions:
            self.new_actions.add(identifier)
            self.known_actions.add(identifier)
            
        # Store version information
        if version:
            self.action_versions[identifier].add(version)
            
        parameters = action.get('WFWorkflowActionParameters', {})
        
        # Track parameter types
        for param_key, param_value in parameters.items():
            param_type = type(param_value).__name__
            self.parameter_types[identifier].add(f"{param_key}: {param_type}")
            
        # Track UUIDs and GroupingIdentifiers
        uuid = parameters.get('UUID')
        group_id = parameters.get('GroupingIdentifier')
        
        if uuid:
            self.uuid_map[uuid] = identifier
        if group_id:
            self.group_map[group_id].append(identifier)
            
        # Track menu structures
        if identifier == 'is.workflow.actions.choosefrommenu':
            menu_items = parameters.get('WFMenuItems', [])
            menu_prompt = parameters.get('WFMenuPrompt', '')
            self.menu_structures[group_id] = {
                'prompt': menu_prompt,
                'items': menu_items
            }
            
        # Track action flows
        if index < total - 1:
            next_action = action.get('WFWorkflowActionIdentifier')
            if next_action:
                self.action_flows[identifier].append(next_action)
                self.action_relationships[identifier].add(next_action)
                
        # Store unique parameter combinations
        param_str = json.dumps(parameters, sort_keys=True)
        if param_str not in [json.dumps(p, sort_keys=True) for p in self.actions_db[identifier]]:
            self.actions_db[identifier].append(parameters) 