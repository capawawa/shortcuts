from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Set
import json
import logging

from .utils import ShortcutError, load_json_file, validate_shortcut_version

logger = logging.getLogger(__name__)

class ShortcutDocMaker:
    """Processes Apple Shortcuts files and generates documentation."""
    
    def __init__(self):
        """Initialize the document maker."""
        self.actions_db = defaultdict(set)  # Action identifier -> parameter set
        self.metadata = defaultdict(set)  # Metadata key -> value set
        self.known_actions = set()  # All encountered actions
        self.new_actions = set()  # Actions not previously documented
        self.uuid_map = {}  # UUID -> action identifier mapping
        self.group_map = defaultdict(list)  # Group ID -> action list
        self.action_flows = defaultdict(list)  # Action -> next actions
        self.parameter_types = defaultdict(set)  # Parameter -> type mapping
        self.action_relationships = defaultdict(set)  # Action -> related actions
        self.menu_structures = defaultdict(dict)  # Menu ID -> structure
        self.action_versions = defaultdict(set)  # Action -> versions mapping
        self.last_processed_action = None  # Track last action for flows

    def process_shortcut_file(self, file_path: Path) -> None:
        """Process a single shortcut file."""
        try:
            logger.info(f"Processing {file_path}")
            data = load_json_file(file_path)
            self._process_shortcut(data)
        except ShortcutError as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            logger.error(error_msg)
            raise

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

    def _process_action(self, action: Dict[str, Any], index: int, total: int, version: str = None) -> None:
        """Process a single action and update action flows."""
        identifier = action.get('WFWorkflowActionIdentifier')
        if not identifier:
            raise ShortcutError("Missing action identifier")
        
        # Add to known actions
        self.known_actions.add(identifier)
        
        # Track version information
        if version:
            self.action_versions[identifier].add(version)
        
        # Process parameters
        parameters = action.get('WFWorkflowActionParameters', {})
        
        # Create a unique parameter signature
        param_signature = []
        for param_name, param_value in sorted(parameters.items()):
            # Store parameter type
            self.parameter_types[identifier].add(f"{param_name}: {type(param_value).__name__}")
            
            # Convert value to string representation
            if isinstance(param_value, (dict, list)):
                value_str = json.dumps(param_value, sort_keys=True)
            else:
                value_str = str(param_value)
            
            param_signature.append(f"{param_name}: {value_str}")
        
        # Store unique parameter combination
        if param_signature:  # Only store if there are parameters
            self.actions_db[identifier].add(tuple(param_signature))  # Use tuple for hashability
        
        # Handle UUID mapping - store all UUIDs, including menu UUIDs
        uuid = parameters.get('UUID')
        if uuid:
            self.uuid_map[uuid] = identifier
        
        # Handle menu-specific UUIDs
        if identifier == 'is.workflow.actions.choosefrommenu':
            menu_uuid = parameters.get('GroupingIdentifier')
            if menu_uuid:
                self.uuid_map[f"menu-{menu_uuid}"] = identifier
        
        # Track action flows
        if index > 0 and self.last_processed_action:
            self.action_flows[self.last_processed_action].append(identifier)
            self.action_relationships[self.last_processed_action].add(identifier)
        
        self.last_processed_action = identifier
        
        # Handle menu structures
        if identifier == 'is.workflow.actions.choosefrommenu':
            self._process_menu_action(parameters)

    def _process_parameters(self, identifier: str, parameters: Dict[str, Any]) -> None:
        """Process parameters for a given action."""
        # Store parameter names and types
        for param_name, param_value in parameters.items():
            param_type = type(param_value).__name__
            self.parameter_types[param_name].add(param_type)
            
            # For complex types, store nested structure
            if isinstance(param_value, (dict, list)):
                param_str = json.dumps(param_value, sort_keys=True)
                self.actions_db[identifier].add(f"{param_name}: {param_str}")
            else:
                self.actions_db[identifier].add(f"{param_name}: {param_type}")
                
        # Handle UUID mappings
        uuid = parameters.get('UUID')
        if uuid:
            self.uuid_map[uuid] = identifier
            
        # Handle grouping
        group_id = parameters.get('GroupingIdentifier')
        if group_id:
            self.group_map[group_id].append(identifier)

    def _process_menu_action(self, parameters: Dict[str, Any]) -> None:
        """Process menu action parameters."""
        group_id = parameters.get('GroupingIdentifier')
        if group_id:
            self.menu_structures[group_id] = {
                'items': parameters.get('WFMenuItems', []),
                'prompt': parameters.get('WFMenuPrompt', ''),
                'default': parameters.get('WFMenuDefaultItem', '')
            }