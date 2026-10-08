import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(gexf_path, output_png):
    # Read the Graph Exchange XML Format file
    G = nx.read_gexf(gexf_path)
    
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    # Extract labels from nodes if they have them, else use ID
    labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
    
    # Draw nodes and labels
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    # Extract edge labels (the temporal relationship type, e.g., 'NEXT', 'CONCURRENT')
    edge_labels = {(u, v): G.edges[u, v].get('label', '') 
                   for u, v in G.edges()}
    
    # Draw edges and edge labels
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, connectionstyle='arc3, rad=0.1')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='red')
    
    plt.title(f"Temporal Knowledge Graph: {gexf_path.split('/')[-1]}")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Graph successfully saved as {output_png}")

if __name__ == "__main__":
    visualize_graph('../input and outputs/r-dfir-1_graph.gexf', 'sample_knowledge_graph.png')
