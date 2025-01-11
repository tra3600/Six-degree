import networkx as nx
import matplotlib.pyplot as plt

def create_social_network():
    """
    Crée un graphe représentant un réseau social.
    """
    G = nx.Graph()
    
    # Ajouter des nœuds (personnes)
    people = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack"]
    for person in people:
        G.add_node(person)
    
    # Ajouter des arêtes (relations)
    relationships = [
        ("Alice", "Bob"), ("Alice", "Charlie"), ("Bob", "David"), ("Charlie", "David"), 
        ("David", "Eve"), ("Eve", "Frank"), ("Frank", "Grace"), ("Grace", "Hank"), 
        ("Hank", "Ivy"), ("Ivy", "Jack"), ("Jack", "Alice"), ("Jack", "Charlie")
    ]
    G.add_edges_from(relationships)
    
    return G

def plot_social_network(G):
    """
    Affiche le graphe du réseau social.
    """
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10)
    plt.title("Réseau Social")
    plt.show()

def find_shortest_path(G, source, target):
    """
    Trouve et affiche le chemin le plus court entre deux personnes dans le réseau social.
    """
    try:
        path = nx.shortest_path(G, source=source, target=target)
        print(f"Le chemin le plus court entre {source} et {target} est : {path}")
        print(f"Nombre de degrés de séparation : {len(path) - 1}")
    except nx.NetworkXNoPath:
        print(f"Aucun chemin trouvé entre {source} et {target}.")

# Création et affichage du réseau social
G = create_social_network()
plot_social_network(G)

# Exemple de recherche de chemin le plus court
find_shortest_path(G, "Alice", "Frank")