"""Création, chargement et sauvegarde de réseaux sociaux (graphes non orientés)."""

import csv
import json
from pathlib import Path

import networkx as nx

PRENOMS_DEMO = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack"]
RELATIONS_DEMO = [
    ("Alice", "Bob"), ("Alice", "Charlie"), ("Bob", "David"), ("Charlie", "David"),
    ("David", "Eve"), ("Eve", "Frank"), ("Frank", "Grace"), ("Grace", "Hank"),
    ("Hank", "Ivy"), ("Ivy", "Jack"), ("Jack", "Alice"), ("Jack", "Charlie"),
]

TYPES_RESEAU = ("demo", "petit-monde", "aleatoire", "sans-echelle")


def reseau_demo():
    """Le petit réseau de dix personnes de l'exemple d'origine."""
    G = nx.Graph()
    G.add_nodes_from(PRENOMS_DEMO)
    G.add_edges_from(RELATIONS_DEMO)
    return G


def _nommer(G):
    """Renomme les nœuds entiers en 'P1', 'P2', ..."""
    return nx.relabel_nodes(G, {i: f"P{i + 1}" for i in G.nodes})


def reseau_petit_monde(n=100, k=4, p=0.1, graine=None):
    """Modèle de Watts-Strogatz : fort regroupement + raccourcis aléatoires."""
    if n <= k:
        raise ValueError("n doit être strictement supérieur à k")
    return _nommer(nx.connected_watts_strogatz_graph(n, k, p, tries=200, seed=graine))


def reseau_aleatoire(n=100, p=0.05, graine=None):
    """Modèle d'Erdős-Rényi (peut être non connexe si p est faible)."""
    return _nommer(nx.gnp_random_graph(n, p, seed=graine))


def reseau_sans_echelle(n=100, m=2, graine=None):
    """Modèle de Barabási-Albert : quelques « hubs » très connectés."""
    if n <= m:
        raise ValueError("n doit être strictement supérieur à m")
    return _nommer(nx.barabasi_albert_graph(n, m, seed=graine))


def generer(type_reseau="demo", n=100, graine=None):
    """Point d'entrée unique pour construire un réseau par son nom de modèle."""
    if type_reseau == "demo":
        return reseau_demo()
    if type_reseau == "petit-monde":
        return reseau_petit_monde(n, graine=graine)
    if type_reseau == "aleatoire":
        return reseau_aleatoire(n, graine=graine)
    if type_reseau == "sans-echelle":
        return reseau_sans_echelle(n, graine=graine)
    raise ValueError(f"Type de réseau inconnu : {type_reseau!r} (choix : {', '.join(TYPES_RESEAU)})")


def charger(chemin):
    """Charge un réseau depuis .json, .csv/.txt (une relation « a,b » par ligne) ou .graphml."""
    chemin = Path(chemin)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")
    ext = chemin.suffix.lower()
    G = nx.Graph()
    if ext == ".json":
        data = json.loads(chemin.read_text(encoding="utf-8"))
        if "nodes" in data:  # format node-link de networkx
            return nx.node_link_graph(data, edges="links" if "links" in data else "edges")
        G.add_nodes_from(data.get("personnes", []))
        G.add_edges_from(tuple(r) for r in data.get("relations", []))
    elif ext in (".csv", ".txt"):
        with chemin.open(encoding="utf-8", newline="") as f:
            dialecte = csv.excel if ext == ".csv" else csv.excel_tab
            for ligne in csv.reader(f, dialecte):
                cases = [c.strip() for c in ligne if c.strip()]
                if len(cases) == 1 and " " in cases[0] and ext == ".txt":
                    cases = cases[0].split()
                if len(cases) >= 2 and not cases[0].startswith("#"):
                    G.add_edge(cases[0], cases[1])
                elif len(cases) == 1 and not cases[0].startswith("#"):
                    G.add_node(cases[0])
    elif ext == ".graphml":
        return nx.read_graphml(chemin)
    else:
        raise ValueError(f"Format non pris en charge : {ext} (json, csv, txt, graphml)")
    if G.number_of_nodes() == 0:
        raise ValueError(f"Aucune donnée exploitable dans {chemin}")
    return G


def sauvegarder(G, chemin):
    """Enregistre le réseau selon l'extension : .json, .csv ou .graphml."""
    chemin = Path(chemin)
    ext = chemin.suffix.lower()
    if ext == ".json":
        data = {"personnes": sorted(map(str, G.nodes)),
                "relations": [[str(a), str(b)] for a, b in G.edges]}
        chemin.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif ext == ".csv":
        with chemin.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerows(G.edges)
            w.writerows([n] for n in nx.isolates(G))
    elif ext == ".graphml":
        nx.write_graphml(G, chemin)
    else:
        raise ValueError(f"Format non pris en charge : {ext} (json, csv, graphml)")
