"""Apple Shortcuts Documentation Generator.

A comprehensive tool for analyzing and documenting Apple Shortcuts.
"""

from .shortcut_doc_maker import ShortcutDocMaker
from .shortcut_analyzer import ShortcutAnalyzer
from .doc_generator import DocGenerator

__version__ = "1.0.0"
__all__ = ["ShortcutDocMaker", "ShortcutAnalyzer", "DocGenerator"]