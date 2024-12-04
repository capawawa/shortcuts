from typing import Dict, List, Set, Any, Tuple, Optional
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import json
from itertools import combinations
import logging

from shortcuts_doc_generator.config import CONFIG, logger
from shortcuts_doc_generator.utils import format_action_name, ShortcutError

logger = logging.getLogger(__name__)

class ShortcutAnalyzer:
    """Analyzes shortcut data for patterns and statistics."""
    
    def __init__(self, doc_maker):
        """Initialize analyzer with document maker."""
        self.doc_maker = doc_maker
        self.action_graph = nx.DiGraph()
        self.common_patterns = defaultdict(list)
        self.action_frequencies = defaultdict(int)
        self.parameter_frequencies = defaultdict(int)
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run all analyses and return combined results."""
        return {
            'action_flows': self.analyze_action_flows(),
            'common_patterns': self.analyze_common_patterns(),
            'parameter_usage': self.analyze_parameter_usage(),
            'version_distribution': self.analyze_version_distribution(),
            'menu_complexity': self.analyze_menu_complexity()
        }
        
    def analyze_parameter_usage(self) -> Dict[str, Dict[str, int]]:
        """Analyze parameter usage patterns."""
        usage = {}
        
        for action, params in self.doc_maker.parameter_types.items():
            param_stats = defaultdict(int)
            for param in params:
                param_name = param.split(':')[0].strip()
                param_stats[param_name] += 1
            usage[action] = dict(param_stats)
            
        return usage
        
    def analyze_action_flows(self) -> Dict[str, Any]:
        """Analyze action flows and relationships."""
        self._build_action_graph()
        
        # Calculate centrality metrics
        centrality = nx.pagerank(self.action_graph) if self.action_graph.nodes else {}
        
        # Find common sequences
        sequences = []
        for source, targets in self.doc_maker.action_flows.items():
            for target in targets:
                sequences.append(f"{source} -> {target}")
        
        # Sort by frequency
        sequence_counts = Counter(sequences)
        most_common = sequence_counts.most_common(5)
        
        # Find isolated actions
        all_actions = set(self.doc_maker.known_actions)
        connected_actions = set(self.action_graph.nodes())
        isolated = all_actions - connected_actions
        
        return {
            'central_actions': centrality,
            'isolated_actions': isolated,
            'total_flows': len(self.doc_maker.action_flows),
            'flow_patterns': dict(self.doc_maker.action_flows),
            'most_common_sequences': [seq for seq, count in most_common]
        }
        
    def _build_action_graph(self) -> None:
        """Build networkx graph from action flows."""
        self.action_graph.clear()
        
        # Add all known actions as nodes
        for action in self.doc_maker.known_actions:
            self.action_graph.add_node(action)
            
        # Add edges from action flows
        for source, targets in self.doc_maker.action_flows.items():
            for target in targets:
                self.action_graph.add_edge(source, target)
                
    def generate_visualizations(self, output_dir: Optional[Path] = None) -> None:
        """Generate visualizations of action flows."""
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            
            # Use provided directory or default
            if output_dir is None:
                output_dir = Path(CONFIG['visualization']['dir'])
            
            # Ensure directory exists
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build graph before visualization
            self._build_action_graph()
            
            if len(self.action_graph.nodes()) == 0:
                logger.warning("No actions to visualize")
                return
            
            # Generate action flow graph
            plt.figure(figsize=CONFIG['visualization'].get('figure_size', (12, 8)))
            
            # Use layout from config
            layout = CONFIG['visualization'].get('graph_layout', 'spring')
            if layout == 'spring':
                pos = nx.spring_layout(self.action_graph, k=2, iterations=50)
            else:
                pos = nx.kamada_kawai_layout(self.action_graph)
            
            # Draw nodes and edges
            nx.draw(self.action_graph, pos, with_labels=True, 
                   node_color='lightblue', 
                   node_size=CONFIG['visualization'].get('node_size', 2000),
                   font_size=CONFIG['visualization'].get('font_size', 8))
            
            # Save visualization
            output_file = output_dir / 'action_flow.png'
            plt.savefig(str(output_file), bbox_inches='tight', 
                       dpi=CONFIG['visualization'].get('dpi', 300))
            plt.close()
            
            logger.info(f"Generated visualization at {output_file}")
            return str(output_file)
            
        except ImportError:
            logger.warning("Matplotlib or networkx not available. Skipping visualization generation.")
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            raise

    def analyze_common_patterns(self) -> Dict[str, List[str]]:
        """Analyze common action patterns."""
        patterns = defaultdict(list)
        
        # Find common action sequences
        sequence_counts = defaultdict(int)
        for source, targets in self.doc_maker.action_flows.items():
            for target in targets:
                sequence = f"{source} -> {target}"
                sequence_counts[sequence] += 1
                
        # Find common parameter combinations
        param_patterns = defaultdict(int)
        for action, params in self.doc_maker.parameter_types.items():
            param_key = f"{action}: {sorted(params)}"
            param_patterns[param_key] += 1
            
        # Store most common patterns
        patterns['sequences'] = [k for k, v in sorted(sequence_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        patterns['parameters'] = [k for k, v in sorted(param_patterns.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return dict(patterns)

    def analyze_version_distribution(self) -> Dict[str, List[str]]:
        """Analyze action availability across iOS versions."""
        distribution = defaultdict(list)
        
        # Ensure action_versions exists
        if not hasattr(self.doc_maker, 'action_versions'):
            self.doc_maker.action_versions = defaultdict(set)
            
        for action, versions in self.doc_maker.action_versions.items():
            for version in versions:
                distribution[version].append(action)
                
        return dict(distribution)

    def analyze_menu_complexity(self) -> Dict[str, Any]:
        """Analyze complexity of menu structures."""
        menu_stats = {
            'total_menus': len(self.doc_maker.menu_structures),
            'avg_items': 0,
            'max_items': 0,
            'nested_menus': 0
        }
        
        if menu_stats['total_menus'] > 0:
            item_counts = []
            for menu in self.doc_maker.menu_structures.values():
                items = menu.get('items', [])
                item_counts.append(len(items))
                menu_stats['max_items'] = max(menu_stats['max_items'], len(items))
                
                # Check for nested menus
                if any('menu' in str(item).lower() for item in items):
                    menu_stats['nested_menus'] += 1
                    
            menu_stats['avg_items'] = sum(item_counts) / len(item_counts)
            
        return menu_stats

    def find_common_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Find common patterns in action sequences."""
        patterns = defaultdict(list)
        
        # Analyze sequences of different lengths
        for length in range(2, 5):
            sequences = self._get_action_sequences(length)
            freq = Counter(sequences)
            
            # Store most common patterns
            for seq, count in freq.most_common(3):
                patterns[str(length)].append({
                    'actions': list(seq),
                    'frequency': count
                })
                
        return dict(patterns)
        
    def _get_action_sequences(self, length: int) -> List[Tuple[str, ...]]:
        """Get sequences of actions of specified length."""
        sequences = []
        actions = list(self.doc_maker.action_flows.items())
        
        for i in range(len(actions) - length + 1):
            seq = tuple(a[0] for a in actions[i:i+length])
            sequences.append(seq)
            
        return sequences