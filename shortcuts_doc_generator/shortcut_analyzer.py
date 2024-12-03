from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import json
from itertools import combinations

from config import CONFIG, logger
from utils import format_action_name

class ShortcutAnalyzer:
    def __init__(self, doc_maker):
        """Initialize analyzer with reference to ShortcutDocMaker instance."""
        self.doc_maker = doc_maker
        self.action_graph = nx.DiGraph()
        self.common_patterns = defaultdict(int)
        self.action_frequencies = defaultdict(int)
        self.parameter_frequencies = defaultdict(lambda: defaultdict(int))
        
    def analyze_all(self) -> Dict[str, Any]:
        """Perform all available analyses."""
        return {
            'action_flows': self.analyze_action_flows(),
            'common_patterns': self.find_common_patterns(),
            'parameter_usage': self.analyze_parameter_usage(),
            'version_distribution': self.analyze_version_distribution(),
            'menu_complexity': self.analyze_menu_complexity()
        }
        
    def analyze_action_flows(self) -> Dict[str, Any]:
        """Analyze how actions are connected."""
        # Build action graph
        self.action_graph.clear()
        for source, targets in self.doc_maker.action_flows.items():
            for target in targets:
                self.action_graph.add_edge(source, target)
                
        return {
            'most_common_sequences': self._get_common_sequences(),
            'central_actions': self._get_central_actions(),
            'isolated_actions': self._get_isolated_actions()
        }
        
    def _get_common_sequences(self, min_length: int = 2, max_length: int = 5) -> List[Tuple[List[str], int]]:
        """Find common sequences of actions."""
        sequences = defaultdict(int)
        
        for path in nx.all_simple_paths(self.action_graph, 
                                      min_nodes=min_length,
                                      max_nodes=max_length):
            sequences[tuple(path)] += 1
            
        return sorted(sequences.items(), key=lambda x: x[1], reverse=True)
        
    def _get_central_actions(self) -> List[Tuple[str, float]]:
        """Identify central actions based on PageRank."""
        pagerank = nx.pagerank(self.action_graph)
        return sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        
    def _get_isolated_actions(self) -> Set[str]:
        """Find actions that are never connected to others."""
        return set(self.doc_maker.known_actions) - set(self.action_graph.nodes)
        
    def find_common_patterns(self) -> Dict[str, List[str]]:
        """Identify common patterns in shortcuts."""
        patterns = defaultdict(list)
        min_freq = CONFIG['analysis']['min_pattern_frequency']
        
        # Analyze action combinations
        for group_id, actions in self.doc_maker.group_map.items():
            for i in range(2, min(len(actions) + 1, CONFIG['analysis']['max_pattern_length'] + 1)):
                for combo in combinations(actions, i):
                    pattern_key = '_'.join(combo)
                    self.common_patterns[pattern_key] += 1
                    
        # Filter and organize patterns
        for pattern, freq in self.common_patterns.items():
            if freq >= min_freq:
                actions = pattern.split('_')
                patterns[str(len(actions))].append({
                    'actions': actions,
                    'frequency': freq
                })
                
        return patterns
        
    def analyze_parameter_usage(self) -> Dict[str, Dict[str, int]]:
        """Analyze how parameters are used across actions."""
        usage = {}
        
        for action, params in self.doc_maker.parameter_types.items():
            param_stats = defaultdict(int)
            for param in params:
                param_name = param.split(':')[0].strip()
                param_stats[param_name] += 1
            usage[action] = dict(param_stats)
            
        return usage
        
    def analyze_version_distribution(self) -> Dict[str, List[str]]:
        """Analyze action availability across iOS versions."""
        distribution = defaultdict(list)
        
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
                
            menu_stats['avg_items'] = sum(item_counts) / len(item_counts)
            
        return menu_stats
        
    def generate_visualizations(self) -> None:
        """Generate various visualizations of the data."""
        vis_dir = Path(CONFIG['visualization']['dir'])
        style = CONFIG['visualization']['style']
        
        # Action flow graph
        plt.figure(figsize=style['figure_size'])
        pos = nx.spring_layout(self.action_graph)
        nx.draw(
            self.action_graph, 
            pos,
            with_labels=True,
            node_size=style['node_size'],
            font_size=style['font_size'],
            node_color='lightblue',
            edge_color='gray'
        )
        plt.savefig(vis_dir / 'action_flow.png', bbox_inches='tight')
        plt.close()
        
        # Version distribution
        plt.figure(figsize=style['figure_size'])
        version_dist = self.analyze_version_distribution()
        versions = sorted(version_dist.keys())
        counts = [len(version_dist[v]) for v in versions]
        plt.bar(versions, counts)
        plt.title('Actions by iOS Version')
        plt.xticks(rotation=45)
        plt.savefig(vis_dir / 'version_distribution.png', bbox_inches='tight')
        plt.close()
        
        logger.info("Generated visualizations") 