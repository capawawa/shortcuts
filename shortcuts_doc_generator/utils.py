import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from config import CONFIG, logger

class ShortcutError(Exception):
    """Base exception for shortcut-related errors."""
    pass

class JSONValidationError(ShortcutError):
    """Raised when JSON validation fails."""
    pass

class FileOperationError(ShortcutError):
    """Raised when file operations fail."""
    pass

def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Safely load and validate JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict containing the JSON data
        
    Raises:
        JSONValidationError: If JSON is invalid
        FileOperationError: If file operations fail
    """
    try:
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validate required shortcut fields
        required_fields = ['WFWorkflowActions']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise JSONValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
        return data
        
    except json.JSONDecodeError as e:
        raise JSONValidationError(f"Invalid JSON in {file_path}: {str(e)}")
    except OSError as e:
        raise FileOperationError(f"Error reading {file_path}: {str(e)}")

def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], backup: bool = True) -> None:
    """
    Safely save JSON file with optional backup.
    
    Args:
        data: Data to save
        file_path: Path to save to
        backup: Whether to create backup
    """
    file_path = Path(file_path)
    
    # Create backup if requested
    if backup and file_path.exists():
        create_backup(file_path)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON file: {file_path}")
    except OSError as e:
        raise FileOperationError(f"Error saving {file_path}: {str(e)}")

def create_backup(file_path: Path) -> None:
    """Create a backup of the specified file."""
    backup_dir = Path(CONFIG['database']['backup_dir'])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        # Clean up old backups
        cleanup_old_backups(file_path.stem)
    except OSError as e:
        logger.error(f"Backup failed: {str(e)}")

def cleanup_old_backups(file_stem: str) -> None:
    """Keep only the most recent backups based on config."""
    backup_dir = Path(CONFIG['database']['backup_dir'])
    backup_files = sorted(
        backup_dir.glob(f"{file_stem}_*"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove excess backups
    max_backups = CONFIG['database']['backup_count']
    for old_backup in backup_files[max_backups:]:
        old_backup.unlink()
        logger.info(f"Removed old backup: {old_backup}")

def get_file_list(directory: Union[str, Path], pattern: str = "*.json") -> List[Path]:
    """
    Get list of files matching pattern in directory.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileOperationError(f"Not a directory: {directory}")
        
    return sorted(directory.glob(pattern))

def validate_shortcut_version(data: Dict[str, Any]) -> Optional[str]:
    """
    Extract and validate shortcut version information.
    
    Args:
        data: Shortcut JSON data
        
    Returns:
        Version string if found, None otherwise
    """
    version_keys = [
        'WFWorkflowClientVersion',
        'WFWorkflowMinimumClientVersionString',
        'WFWorkflowMinimumClientVersion'
    ]
    
    for key in version_keys:
        if key in data:
            return str(data[key])
    
    return None

def format_action_name(identifier: str) -> str:
    """
    Format action identifier for display.
    
    Args:
        identifier: Raw action identifier
        
    Returns:
        Formatted action name
    """
    # Remove common prefix
    name = identifier.replace('is.workflow.actions.', '')
    
    # Convert to title case and add spaces
    words = name.split('.')
    return ' '.join(word.title() for word in words) 