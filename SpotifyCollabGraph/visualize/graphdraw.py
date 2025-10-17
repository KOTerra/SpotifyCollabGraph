import graph_tool.all as gt
import matplotlib.cm
import os
import random

# Set a random seed for reproducible layouts
gt.seed_rng(47)

# --- Configuration ---
graphml_file_path = "collaboration_graph_from_playlist.graphml"
edge_property_name = "weight"

# The file to which the visualization will be saved (now PDF)
output_file_name = "visualization.pdf"

# --- Graph Loading and Pre-processing ---
print(f"Loading graph from '{graphml_file_path}'...")
if not os.path.exists(graphml_file_path):
    print(f"Error: The file '{graphml_file_path}' was not found.")
    exit()

g = gt.load_graph(graphml_file_path)
print(f"Graph loaded successfully with {g.num_vertices()} nodes and {g.num_edges()} edges.")

if edge_property_name not in g.ep:
    print(f"Warning: Edge property '{edge_property_name}' not found.")
    print("Creating a default edge property with random values for visualization.")
    ep_weight = g.new_ep("int")
    for e in g.edges():
        ep_weight[e] = random.randint(1, 10)
    g.ep[edge_property_name] = ep_weight
else:
    print(f"Using existing edge property '{edge_property_name}'.")

# --- Interactive Visualization ---
print("Applying visualization style and opening interactive window...")

state = gt.minimize_nested_blockmodel_dl(g,
                                         state_args=dict(recs=[g.ep[edge_property_name]],
                                                         rec_types=["real-exponential"]))

# Get a property map of the total degree for each node
deg = g.degree_property_map("total")

# First draw call: opens the interactive window
state.draw(
    vertex_size=gt.prop_to_size(deg, mi=5, ma=20),
    edge_color=gt.prop_to_size(g.ep[edge_property_name],
                               power=1,
                               log=True),
    ecmap=(matplotlib.cm.inferno, .6),
    eorder=g.ep[edge_property_name],
    edge_pen_width=gt.prop_to_size(g.ep[edge_property_name],
                                   1, 4,
                                   power=1,
                                   log=True),
    edge_gradient=[]);

# CORRECTED LINE: This keeps the interactive window open until you close it.
# It requires the graph object 'g' to work correctly.
gt.interactive_window(g)

print("Interactive window closed. Now exporting image...")

# Second draw call: renders to a file. It uses the exact same parameters
# as the interactive visualization for consistency.
state.draw(output=output_file_name,
           vertex_size=gt.prop_to_size(deg, mi=5, ma=20),
           edge_color=gt.prop_to_size(g.ep[edge_property_name],
                                      power=1,
                                      log=True),
           ecmap=(matplotlib.cm.inferno, .6),
           eorder=g.ep[edge_property_name],
           edge_pen_width=gt.prop_to_size(g.ep[edge_property_name],
                                          1, 4,
                                          power=1,
                                          log=True),
           edge_gradient=[]);

print(f"Visualization saved to '{output_file_name}'.")