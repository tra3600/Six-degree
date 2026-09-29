"""Dessin du réseau et de la distribution des distances."""

import os

import matplotlib

# Sans écran (serveur, CI) ou en écrivant dans un fichier : backend non interactif.
if not os.environ.get("DISPLAY") and os.name != "nt" and os.uname().sysname != "Darwin":
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

from .analyse import communautes, distribution_distances  # noqa: E402

PALETTE = ["#4e79a7", "#f28e2b", "#59a14f", "#b07aa1", "#76b7b2", "#edc948", "#9c755f", "#bab0ac"]
COULEUR_CHEMIN = "#e15759"
SEUIL_ETIQUETTES = 60


def _finir(fichier, dpi=150):
    plt.tight_layout()
    if fichier:
        plt.savefig(fichier, dpi=dpi)
        plt.close()
        return fichier
    if matplotlib.get_backend().lower() == "agg":
        plt.close()
        return None
    plt.show()
    return None


def _positions(G, graine):
    n = G.number_of_nodes()
    if n <= 40:
        try:
            return nx.kamada_kawai_layout(G)
        except ImportError:  # scipy absent : repli sur le layout à ressorts
            pass
    return nx.spring_layout(G, seed=graine, k=1.5 / max(n, 1) ** 0.5)


def dessiner(G, chemin=None, par_communaute=False, fichier=None, graine=42, titre="Réseau social"):
    """Dessine le réseau. `chemin` (liste de nœuds) est mis en évidence en rouge ;
    `par_communaute` colore chaque communauté ; la taille des nœuds reflète le nombre d'amis."""
    n = G.number_of_nodes()
    plt.figure(figsize=(11, 8))
    pos = _positions(G, graine)

    couleurs = {}
    if par_communaute:
        for i, groupe in enumerate(communautes(G)):
            couleurs.update({m: PALETTE[i % len(PALETTE)] for m in groupe})
    noeuds = list(G.nodes)
    fond = [couleurs.get(x, "#a0cbe8") for x in noeuds]
    tailles = [(150 + 60 * G.degree(x)) if n > 25 else (500 + 250 * G.degree(x)) for x in noeuds]
    nx.draw_networkx_edges(G, pos, alpha=0.35, width=1.0)
    nx.draw_networkx_nodes(G, pos, nodelist=noeuds, node_color=fond, node_size=tailles, edgecolors="white")

    if chemin and len(chemin) > 1:
        aretes = list(zip(chemin, chemin[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=aretes, edge_color=COULEUR_CHEMIN, width=3.5)
        nx.draw_networkx_nodes(G, pos, nodelist=chemin, node_color=fond_chemin(chemin, couleurs),
                               node_size=[tailles[noeuds.index(x)] for x in chemin],
                               edgecolors=COULEUR_CHEMIN, linewidths=2.5)
        titre += f" — {chemin[0]} → {chemin[-1]} : {len(chemin) - 1} degré(s)"
    if n <= SEUIL_ETIQUETTES:
        nx.draw_networkx_labels(G, pos, font_size=9 if n > 25 else 10)
    plt.title(titre)
    plt.axis("off")
    return _finir(fichier)


def fond_chemin(chemin, couleurs):
    return [couleurs.get(x, "#ffd8d8") for x in chemin]


def dessiner_distances(G, fichier=None):
    """Histogramme du nombre de paires de personnes à chaque distance."""
    dist = distribution_distances(G)
    if not dist:
        raise ValueError("Aucune paire de personnes reliées à représenter")
    plt.figure(figsize=(8, 5))
    barres = plt.bar(dist.keys(), dist.values(),
                     color=[PALETTE[0] if d <= 6 else COULEUR_CHEMIN for d in dist])
    plt.bar_label(barres)
    plt.axvline(6.5, color="gray", linestyle="--", label="seuil des six degrés")
    plt.xlabel("Degrés de séparation")
    plt.ylabel("Nombre de paires")
    plt.title("Distribution des distances")
    plt.xticks(list(dist))
    plt.legend()
    return _finir(fichier)
