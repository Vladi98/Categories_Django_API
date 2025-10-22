#!/usr/bin/env python
"""
Rabbit Hole Analysis Script

This script analyzes category similarity relationships to find:
1. The longest rabbit hole (shortest path between most distant categories)
2. All rabbit islands (connected components in the similarity graph)

Run with: python manage.py shell < rabbit_hole_analysis.py
Or: python rabbit_hole_analysis.py (if configured as standalone)
"""

import os
import django
from collections import defaultdict, deque
from categories_app.models import Category, CategorySimilarity


class SimilarityGraph:
    """Graph representation of category similarities for analysis,"""
    
    def __init__(self):
        self.graph = defaultdict(set)
        self.categories = {}
        
    def build_from_db(self):
        print("Building similarity graph from db...")

        categries = Category.objects.all()
        for cat in categries:
            self.categories[cat.id] = cat
            self.graph[cat.id] = set()
        

        similarities = CategorySimilarity.objects.all().select_related(
            'category_a', 'category_b'
        )
        
        for sim in similarities:
            #Add bidirectional edges
            self.graph[sim.category_a.id].add(sim.category_b.id)
            self.graph[sim.category_b.id].add(sim.category_a.id)
        
        print(f"Graph built: {len(self.categories)} categories, "
              f"{similarities.count()} similarity pairs")
        return self
     
     
    def bfs_shortest_path(self, start_id, end_id):
        """Find shortest path between two categories using BFS."""
        if start_id == end_id:
            return [start_id]
        
        visited = {start_id}
        queue = deque([(start_id, [start_id])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.graph[current]:
                if neighbor == end_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # PAth does not exist!
    
    def find_all_islands(self):
        """Find all connected components (rabbit islands) in the graph."""
        visited = set()
        islands = []
        
        for cat_id in self.categories:
            if cat_id not in visited:
                # BFS to find all connected categories
                island = set()
                queue = deque([cat_id])
                island.add(cat_id)
                visited.add(cat_id)
                
                while queue:
                    current = queue.popleft()
                    
                    for neighbor in self.graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            island.add(neighbor)
                            queue.append(neighbor)
                
                islands.append(island)
        
        return islands
    
    def find_longest_rabbit_hole(self):
        """
        Find the longest path between any two cats
        """
        islands = self.find_all_islands()
        longest_path = []
        longest_length = 0
        
        for island in islands:
            if len(island) < 2:
                continue

            island_list = list(island)

            # brute force approach -  fine for our scale (could be optimized with BFS)
            for i, start in enumerate(island_list):
                distances = {start: 0}
                queue = deque([start])
                parent = {start: None}
                
                while queue:
                    current = queue.popleft()
                    
                    for neighbor in self.graph[current]:
                        if neighbor not in distances and neighbor in island:
                            distances[neighbor] = distances[current] + 1
                            parent[neighbor] = current
                            queue.append(neighbor)
                # Find the farthest node
                if distances:
                    farthest = max(distances, key=distances.get)
                    max_dist = distances[farthest]
                    if max_dist > longest_length:
                        #recreate path
                        path = []
                        current = farthest
                        while current is not None:
                            path.append(current)
                            current = parent[current]
                        path.reverse()
                        
                        longest_path = path
                        longest_length = max_dist

        return longest_path, longest_length


def format_category_path(graph, path):
    """Format a category path for display."""
    if not path:
        return "No path"
    
    names = [graph.categories[cat_id].name for cat_id in path]
    return " → ".join(names)

def main():
    """Main analysis function."""
    print("=" * 80)
    print("CATEGORY SIMILARITY ANALYSIS - RABBIT HOLES AND ISLANDS")
    print("=" * 80)
    print()
    
    # Build graph
    graph = SimilarityGraph().build_from_db()
    print()
    
    if not graph.categories:
        print("No categories found in database.")
        return
    
    # Locaterabbit islands
    print("=" * 80)
    print("RABBIT ISLANDS (Connected Components)")
    print("=" * 80)
    
    islands = graph.find_all_islands()
    islands.sort(key=len, reverse=True)
    
    print(f"\nFound {len(islands)} rabbit islands\n")
    
    for i, island in enumerate(islands, 1):
        print(f"Island {i}: {len(island)} categories")
        
        # Sort categories by name for consistent output
        island_categories = sorted(
            [graph.categories[cat_id] for cat_id in island],
            key=lambda c: c.name
        )
        
        # Display categories (place a  limit to 20 per island for readability)
        if len(island_categories) <= 20:
            for cat in island_categories:
                print(f"  - {cat.name} (ID: {cat.id})")
        else:
            for cat in island_categories[:10]:
                print(f"  - {cat.name} (ID: {cat.id})")
            print(f"  ... and {len(island_categories) - 10} more categories")
        
        print()
    
    #Find longest rabbit hole
    print("=" * 80)
    print("LONGEST RABBIT HOLE (Diameter of Similarity Graph)")
    print("=" * 80)
    print()
    
    longest_path, longest_length = graph.find_longest_rabbit_hole()
    
    if longest_path:
        print(f"Length: {longest_length} hops")
        print(f"Path: {format_category_path(graph, longest_path)}")
        print()
        print("Detailed path:")
        for i, cat_id in enumerate(longest_path):
            cat = graph.categories[cat_id]
            print(f"  {i + 1}. {cat.name} (ID: {cat.id})")
    else:
        print("No rabbit holes found (no similar categories exist).")
    
    print()
    
    # Additional stas
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print()
    print(f"Total categoies: {len(graph.categories)}")
    print(f"Total similarity relationships: {CategorySimilarity.objects.count()}")
    print(f"Cats with similarities: {sum(1 for edges in graph.graph.values() if edges)}")
    print(f"Isolated cats: {sum(1 for edges in graph.graph.values() if not edges)}")
    print(f"Average conections per category: {sum(len(edges) for edges in graph.graph.values()) / len(graph.categories):.2f}")
    
    # Find most connected cats
    most_connected = sorted(
        graph.categories.keys(),
        key=lambda cat_id: len(graph.graph[cat_id]),
        reverse=True
    )[:5]
    
    print("\nMost connected categories:")
    for cat_id in most_connected:
        cat = graph.categories[cat_id]
        connections = len(graph.graph[cat_id])
        if connections > 0:
            print(f"  - {cat.name}: {connections} connections")
    
    print()
    print("=" * 80)
    print("Analysis complete!!!")
    print("=" * 80)

