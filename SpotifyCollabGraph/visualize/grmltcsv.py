import networkx as nx
import csv
import os

# --- Configuration ---
# Replace with the path to your GraphML file
graphml_file_path = "collaboration_graph_from_playlist.graphml"

# The names of the output CSV files
nodes_csv_path = "nodes.csv"
edges_csv_path = "edges.csv"

# --- Script ---
print(f"Loading graph from '{graphml_file_path}'...")

# Check if the file exists before trying to load it
if not os.path.exists(graphml_file_path):
    print(f"Error: The file '{graphml_file_path}' was not found.")
    exit()

# Load the graph from the GraphML file
g = nx.read_graphml(graphml_file_path)

print(f"Graph loaded successfully with {g.number_of_nodes()} nodes and {g.number_of_edges()} edges.")

# --- Write Nodes CSV ---
print(f"Writing nodes to '{nodes_csv_path}'...")
with open(nodes_csv_path, 'w', newline='', encoding='utf-8') as f:
    # Get all unique node attribute keys to use as CSV headers
    node_attrs = set()
    for _, data in g.nodes(data=True):
        node_attrs.update(data.keys())

    fieldnames = ['id'] + sorted(list(node_attrs))
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for node_id, data in g.nodes(data=True):
        row = {'id': node_id, **data}
        writer.writerow(row)

# --- Write Edges CSV ---
print(f"Writing edges to '{edges_csv_path}'...")
with open(edges_csv_path, 'w', newline='', encoding='utf-8') as f:
    # Get all unique edge attribute keys
    edge_attrs = set()
    for _, _, data in g.edges(data=True):
        edge_attrs.update(data.keys())

    fieldnames = ['source', 'target'] + sorted(list(edge_attrs))
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for u, v, data in g.edges(data=True):
        row = {'source': u, 'target': v, **data}
        writer.writerow(row)

print("Conversion complete!")
print(f"Nodes saved to '{nodes_csv_path}' and edges saved to '{edges_csv_path}'.")