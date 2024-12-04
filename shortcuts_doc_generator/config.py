from pathlib import Path
import logging
from typing import Dict, Any

# Base configuration
CONFIG: Dict[str, Any] = {
    'database': {
        'path': 'data/shortcuts.db',
        'backup_dir': 'data/backups',
        'backup_count': 5
    },
    'output': {
        'dir': 'output',
        'directory': 'output',
        'formats': ['markdown', 'html', 'json', 'yaml']
    },
    'visualization': {
        'dir': 'visualizations',
        'format': 'png',
        'dpi': 300,
        'graph_layout': 'spring',
        'figure_size': (12, 8),
        'node_size': 2000,
        'font_size': 8
    },
    'analysis': {
        'graph_layout': 'spring',
        'min_pattern_length': 2,
        'max_pattern_length': 5
    },
    'logging': {
        'level': logging.INFO,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'shortcut_doc.log'
    }
}

# Ensure output directories exist
for dir_path in [CONFIG['output']['dir'], CONFIG['visualization']['dir'], CONFIG['database']['backup_dir']]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=CONFIG['logging']['level'],
    format=CONFIG['logging']['format'],
    handlers=[
        logging.FileHandler(CONFIG['logging']['file']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Configuration loaded")

def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    return CONFIG

def update_config(new_config: Dict[str, Any]) -> None:
    """Update configuration with new values."""
    global CONFIG
    CONFIG.update(new_config)
    logger.info("Configuration updated") 