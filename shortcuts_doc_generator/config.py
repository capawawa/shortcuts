from pathlib import Path
import logging
from typing import Dict, Any

# Base configuration
CONFIG: Dict[str, Any] = {
    'database': {
        'file': 'shortcuts_db.json',
        'backup_dir': 'backups',
        'backup_count': 5  # Keep last 5 backups
    },
    'output': {
        'dir': Path('documentation'),
        'formats': ['markdown', 'html', 'json'],
        'default_format': 'markdown'
    },
    'visualization': {
        'enabled': True,
        'output_format': 'png',
        'dir': Path('visualizations'),
        'style': {
            'node_size': 2000,
            'font_size': 8,
            'figure_size': (15, 10)
        }
    },
    'logging': {
        'level': logging.INFO,
        'file': 'shortcut_doc.log',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    'analysis': {
        'min_pattern_frequency': 2,  # Minimum times a pattern must appear to be recorded
        'max_pattern_length': 5,     # Maximum length of action sequences to analyze
        'graph_layout': 'spring'     # NetworkX layout algorithm
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