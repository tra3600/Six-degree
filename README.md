# Six-degree — les six degrés de séparation

Outil en Python pour **générer, analyser et visualiser** des réseaux sociaux et vérifier la théorie des
« six degrés de séparation » : deux personnes quelconques seraient reliées par une chaîne d'au plus six relations.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python -m six_degrees [options de source] <commande>     # ou : python 6degre.py <commande>
```

**Source du réseau** (par défaut : le réseau de démonstration de 10 personnes)

| Option | Effet |
|---|---|
| `-r FICHIER` | charger un réseau `.json`, `.csv`, `.txt` (une relation `a,b` par ligne) ou `.graphml` |
| `-t {demo,petit-monde,aleatoire,sans-echelle}` | générer un réseau (Watts-Strogatz, Erdős-Rényi, Barabási-Albert) |
| `-n N`, `--graine G` | nombre de personnes, graine aléatoire pour des résultats reproductibles |

**Commandes**

| Commande | Rôle |
|---|---|
| `stats` (défaut) | personnes, relations, densité, diamètre, distance moyenne, regroupement, **part des paires à ≤ 6 degrés** |
| `chemin A B [--tous] [-o img.png]` | plus court chemin (ou tous), dessiné en rouge dans l'image |
| `centralite [--top N]` | les plus connectés, meilleurs intermédiaires, plus proches de tous |
| `communautes` | groupes d'amis (modularité) |
| `amis NOM` | suggestions d'amis (amis d'amis, classés par amis communs) |
| `distance NOM D` | personnes à exactement D degrés |
| `distances` | distribution des distances |
| `dessiner [-o img.png] [--communautes] [--histogramme]` | graphe (coloré par communauté) ou histogramme des distances |
| `exporter FICHIER` | enregistrer le réseau (`.json`, `.csv`, `.graphml`) |
| `interactif` | shell : `chemin`, `stats`, `amis`, `ajouter A B`, `retirer A B`, `dessiner`, `sauver`… |

Les noms ignorent la casse et les fautes de frappe sont signalées avec des suggestions.

## Exemples

```bash
python -m six_degrees chemin alice frank --tous -o chemin.png
python -m six_degrees -t petit-monde -n 1000 --graine 1 stats       # la théorie tient-elle ?
python -m six_degrees -t sans-echelle -n 300 dessiner --communautes -o reseau.png
python -m six_degrees -r amis.csv amis Marie
```

Format JSON : `{"personnes": ["A", "B"], "relations": [["A", "B"]]}`.

## Structure

- `six_degrees/reseau.py` : génération, chargement, sauvegarde
- `six_degrees/analyse.py` : chemins, statistiques, centralités, communautés, suggestions
- `six_degrees/visualisation.py` : dessin du graphe et histogramme
- `six_degrees/cli.py` : ligne de commande et mode interactif

Tests : `python -m pytest`
