"""Analyses d'un réseau social : chemins, statistiques, centralités, communautés."""

from collections import Counter
from difflib import get_close_matches
from itertools import islice

import networkx as nx


class PersonneInconnue(KeyError):
    """Levée quand un nom ne correspond à aucune personne du réseau."""

    def __str__(self):
        return self.args[0]


def resoudre_nom(G, nom):
    """Retrouve un nœud en ignorant la casse ; propose des suggestions sinon."""
    if nom in G:
        return nom
    par_minuscule = {str(n).lower(): n for n in G.nodes}
    if str(nom).lower() in par_minuscule:
        return par_minuscule[str(nom).lower()]
    proches = get_close_matches(str(nom).lower(), par_minuscule, n=3, cutoff=0.5)
    aide = f" Vouliez-vous dire : {', '.join(str(par_minuscule[p]) for p in proches)} ?" if proches else ""
    raise PersonneInconnue(f"Personne inconnue : {nom!r}.{aide}")


def plus_court_chemin(G, source, cible):
    """Un plus court chemin, ou None si les deux personnes ne sont pas reliées."""
    source, cible = resoudre_nom(G, source), resoudre_nom(G, cible)
    try:
        return nx.shortest_path(G, source, cible)
    except nx.NetworkXNoPath:
        return None


def tous_les_plus_courts_chemins(G, source, cible, limite=10):
    """Jusqu'à `limite` plus courts chemins distincts (liste vide si aucun)."""
    source, cible = resoudre_nom(G, source), resoudre_nom(G, cible)
    try:
        return list(islice(nx.all_shortest_paths(G, source, cible), limite))
    except nx.NetworkXNoPath:
        return []


def distribution_distances(G):
    """Compteur {distance: nombre de paires} sur toutes les paires reliées."""
    compteur = Counter()
    for source, distances in nx.all_pairs_shortest_path_length(G):
        for cible, d in distances.items():
            if d > 0 and str(source) < str(cible):
                compteur[d] += 1
    return dict(sorted(compteur.items()))


def verification_six_degres(G, seuil=6):
    """Part des paires de personnes séparées d'au plus `seuil` relations."""
    n = G.number_of_nodes()
    paires = n * (n - 1) // 2
    if paires == 0:
        return {"paires": 0, "reliees": 0, "dans_le_seuil": 0, "proportion": 0.0, "seuil": seuil}
    dist = distribution_distances(G)
    reliees = sum(dist.values())
    ok = sum(c for d, c in dist.items() if d <= seuil)
    return {"paires": paires, "reliees": reliees, "dans_le_seuil": ok,
            "proportion": ok / paires, "seuil": seuil}


def statistiques(G):
    """Indicateurs globaux du réseau."""
    n = G.number_of_nodes()
    if n == 0:
        raise ValueError("Le réseau est vide")
    composantes = sorted(nx.connected_components(G), key=len, reverse=True)
    plus_grande = G.subgraph(composantes[0])
    degres = [d for _, d in G.degree()]
    stats = {
        "personnes": n,
        "relations": G.number_of_edges(),
        "densite": nx.density(G),
        "degre_moyen": sum(degres) / n,
        "degre_max": max(degres),
        "composantes": len(composantes),
        "connexe": len(composantes) == 1,
        "taille_plus_grande_composante": len(composantes[0]),
        "clustering_moyen": nx.average_clustering(G),
        "transitivite": nx.transitivity(G),
        "distance_moyenne": None,
        "diametre": None,
        "rayon": None,
    }
    if len(plus_grande) > 1:
        stats["distance_moyenne"] = nx.average_shortest_path_length(plus_grande)
        stats["diametre"] = nx.diameter(plus_grande)
        stats["rayon"] = nx.radius(plus_grande)
    return stats


def centralites(G, top=5):
    """Classements (degré, intermédiarité, proximité) : les `top` premiers de chaque."""
    mesures = {
        "degre": nx.degree_centrality(G),
        "intermediarite": nx.betweenness_centrality(G),
        "proximite": nx.closeness_centrality(G),
    }
    return {nom: sorted(vals.items(), key=lambda kv: (-kv[1], str(kv[0])))[:top]
            for nom, vals in mesures.items()}


def communautes(G):
    """Communautés détectées par maximisation de la modularité (plus grandes d'abord)."""
    if G.number_of_edges() == 0:
        return [{n} for n in G.nodes]
    groupes = nx.community.greedy_modularity_communities(G)
    return [set(g) for g in sorted(groupes, key=lambda g: (-len(g), sorted(map(str, g))))]


def suggestions_amis(G, personne, top=5):
    """Amis potentiels : amis d'amis classés par nombre d'amis communs (Adamic-Adar en départage)."""
    personne = resoudre_nom(G, personne)
    voisins = set(G[personne])
    candidats = {}
    for ami in voisins:
        for autre in G[ami]:
            if autre != personne and autre not in voisins:
                candidats.setdefault(autre, set()).add(ami)
    if not candidats:
        return []
    scores = {c: sum(1 / max(nx.degree(G, m), 2) for m in communs) for c, communs in candidats.items()}
    classement = sorted(candidats, key=lambda c: (-len(candidats[c]), -scores[c], str(c)))
    return [(c, sorted(candidats[c], key=str)) for c in classement[:top]]


def personnes_a_distance(G, personne, distance):
    """Personnes situées exactement à `distance` relations de `personne`."""
    personne = resoudre_nom(G, personne)
    longueurs = nx.single_source_shortest_path_length(G, personne, cutoff=distance)
    return sorted((n for n, d in longueurs.items() if d == distance), key=str)


def excentricite(G, personne):
    """Distance maximale de `personne` à toute autre personne de sa composante."""
    personne = resoudre_nom(G, personne)
    return max(nx.single_source_shortest_path_length(G, personne).values())
