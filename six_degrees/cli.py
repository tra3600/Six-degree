"""Interface en ligne de commande : `python -m six_degrees <commande>`."""

import argparse
import cmd
import sys

from . import __version__, analyse, reseau, visualisation


def _fmt(x, chiffres=3):
    return "—" if x is None else (f"{x:.{chiffres}f}" if isinstance(x, float) else str(x))


def afficher_chemin(G, source, cible, tous=False):
    if tous:
        chemins = analyse.tous_les_plus_courts_chemins(G, source, cible)
    else:
        c = analyse.plus_court_chemin(G, source, cible)
        chemins = [c] if c else []
    source, cible = analyse.resoudre_nom(G, source), analyse.resoudre_nom(G, cible)
    if not chemins:
        print(f"Aucun chemin entre {source} et {cible} (composantes différentes).")
        return None
    print(f"{source} → {cible} : {len(chemins[0]) - 1} degré(s) de séparation")
    for c in chemins:
        print("  " + " → ".join(map(str, c)))
    return chemins[0]


def afficher_stats(G):
    s = analyse.statistiques(G)
    lignes = [
        ("Personnes", s["personnes"]), ("Relations", s["relations"]),
        ("Degré moyen (amis/personne)", _fmt(s["degre_moyen"], 2)), ("Degré max", s["degre_max"]),
        ("Densité", _fmt(s["densite"])), ("Réseau connexe", "oui" if s["connexe"] else "non"),
        ("Composantes", s["composantes"]), ("Plus grande composante", s["taille_plus_grande_composante"]),
        ("Distance moyenne", _fmt(s["distance_moyenne"], 2)), ("Diamètre", _fmt(s["diametre"])),
        ("Rayon", _fmt(s["rayon"])), ("Regroupement moyen", _fmt(s["clustering_moyen"])),
        ("Transitivité", _fmt(s["transitivite"])),
    ]
    for nom, val in lignes:
        print(f"  {nom:<30} {val}")
    v = analyse.verification_six_degres(G)
    print(f"\n  Six degrés : {v['dans_le_seuil']}/{v['paires']} paires ({v['proportion']:.1%}) "
          f"sont séparées d'au plus {v['seuil']} relations.")


def afficher_centralites(G, top=5):
    noms = {"degre": "Les plus connectés (degré)", "intermediarite": "Les meilleurs intermédiaires",
            "proximite": "Les plus proches de tous (proximité)"}
    for cle, classement in analyse.centralites(G, top).items():
        print(f"{noms[cle]} :")
        for i, (p, v) in enumerate(classement, 1):
            print(f"  {i}. {p:<12} {v:.3f}")


def afficher_communautes(G):
    for i, g in enumerate(analyse.communautes(G), 1):
        print(f"Communauté {i} ({len(g)}) : {', '.join(sorted(map(str, g)))}")


def afficher_amis(G, personne, top=5):
    sug = analyse.suggestions_amis(G, personne, top)
    personne = analyse.resoudre_nom(G, personne)
    if not sug:
        print(f"Aucune suggestion pour {personne}.")
    for p, communs in sug:
        print(f"  {p:<12} via {', '.join(map(str, communs))} ({len(communs)} ami(s) en commun)")


def afficher_distances(G):
    for d, c in analyse.distribution_distances(G).items():
        print(f"  {d} degré(s) : {c:>6} paires  {'█' * min(c, 50)}")


class Interactif(cmd.Cmd):
    intro = "Six degrés de séparation — tapez 'help' pour la liste des commandes, 'quit' pour sortir."
    prompt = "six> "

    def __init__(self, G):
        super().__init__()
        self.G = G

    def _garde(self, fn, *a):
        try:
            return fn(*a)
        except (analyse.PersonneInconnue, ValueError, FileNotFoundError) as e:
            print(f"Erreur : {e}")

    def _args(self, ligne, n, usage):
        parts = ligne.split()
        if len(parts) != n:
            print(f"Usage : {usage}")
            return None
        return parts

    def do_chemin(self, ligne):
        "chemin A B : plus court chemin entre deux personnes"
        if (a := self._args(ligne, 2, "chemin A B")):
            self._garde(afficher_chemin, self.G, *a, True)

    def do_stats(self, _):
        "stats : statistiques globales"
        self._garde(afficher_stats, self.G)

    def do_centralite(self, _):
        "centralite : personnes les plus importantes"
        afficher_centralites(self.G)

    def do_communautes(self, _):
        "communautes : groupes d'amis détectés"
        afficher_communautes(self.G)

    def do_amis(self, ligne):
        "amis NOM : suggestions d'amis (amis d'amis)"
        if (a := self._args(ligne, 1, "amis NOM")):
            self._garde(afficher_amis, self.G, a[0])

    def do_distances(self, _):
        "distances : distribution des distances"
        afficher_distances(self.G)

    def do_ajouter(self, ligne):
        "ajouter A B : crée une relation (et les personnes au besoin)"
        if (a := self._args(ligne, 2, "ajouter A B")):
            self.G.add_edge(*a)
            print(f"Relation {a[0]} — {a[1]} ajoutée.")

    def do_retirer(self, ligne):
        "retirer A B : supprime une relation"
        if (a := self._args(ligne, 2, "retirer A B")):
            if self.G.has_edge(*a):
                self.G.remove_edge(*a)
                print("Relation supprimée.")
            else:
                print("Cette relation n'existe pas.")

    def do_personnes(self, _):
        "personnes : liste des personnes"
        print(", ".join(sorted(map(str, self.G.nodes))))

    def do_dessiner(self, ligne):
        "dessiner [A B] [fichier.png] : affiche ou enregistre le graphe (chemin A→B en rouge)"
        parts = ligne.split()
        fichier = parts.pop() if parts and parts[-1].lower().endswith((".png", ".svg", ".pdf")) else None
        chemin = None
        if len(parts) == 2:
            chemin = self._garde(analyse.plus_court_chemin, self.G, *parts)
        self._garde(visualisation.dessiner, self.G, chemin, False, fichier)
        if fichier:
            print(f"Image enregistrée : {fichier}")

    def do_sauver(self, ligne):
        "sauver FICHIER : enregistre le réseau (.json, .csv, .graphml)"
        if (a := self._args(ligne, 1, "sauver FICHIER")):
            self._garde(reseau.sauvegarder, self.G, a[0])
            print("Réseau enregistré.")

    def do_quit(self, _):
        "quit : quitter"
        return True

    do_exit = do_quit
    do_EOF = do_quit

    def emptyline(self):
        pass


def construire_parseur():
    p = argparse.ArgumentParser(prog="six_degrees", description="Explorer les six degrés de séparation.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    src = p.add_argument_group("source du réseau")
    src.add_argument("-r", "--reseau", metavar="FICHIER", help="charger un réseau (.json, .csv, .txt, .graphml)")
    src.add_argument("-t", "--type", choices=reseau.TYPES_RESEAU, default="demo",
                      help="ou générer un réseau (défaut : demo)")
    src.add_argument("-n", "--taille", type=int, default=100, help="nombre de personnes générées (défaut : 100)")
    src.add_argument("--graine", type=int, help="graine aléatoire (résultats reproductibles)")
    sub = p.add_subparsers(dest="commande")
    c = sub.add_parser("chemin", help="plus court chemin entre deux personnes")
    c.add_argument("source"); c.add_argument("cible")
    c.add_argument("--tous", action="store_true", help="afficher tous les plus courts chemins")
    c.add_argument("-o", "--sortie", help="dessiner le chemin dans une image")
    sub.add_parser("stats", help="statistiques et vérification des six degrés")
    s = sub.add_parser("centralite", help="personnes les plus influentes"); s.add_argument("--top", type=int, default=5)
    sub.add_parser("communautes", help="détecter les groupes d'amis")
    s = sub.add_parser("amis", help="suggestions d'amis"); s.add_argument("personne"); s.add_argument("--top", type=int, default=5)
    s = sub.add_parser("distance", help="personnes à exactement D degrés"); s.add_argument("personne"); s.add_argument("d", type=int)
    sub.add_parser("distances", help="distribution des distances")
    s = sub.add_parser("dessiner", help="afficher ou enregistrer le graphe")
    s.add_argument("-o", "--sortie"); s.add_argument("--communautes", action="store_true")
    s.add_argument("--histogramme", action="store_true", help="tracer la distribution des distances")
    s = sub.add_parser("exporter", help="enregistrer le réseau (.json, .csv, .graphml)"); s.add_argument("fichier")
    sub.add_parser("interactif", help="mode interactif")
    return p


def executer(args):
    G = reseau.charger(args.reseau) if args.reseau else reseau.generer(args.type, args.taille, args.graine)
    cmd_ = args.commande or "stats"
    if cmd_ == "chemin":
        chemin = afficher_chemin(G, args.source, args.cible, args.tous)
        if args.sortie and chemin:
            visualisation.dessiner(G, chemin, fichier=args.sortie)
            print(f"Image enregistrée : {args.sortie}")
    elif cmd_ == "stats":
        afficher_stats(G)
    elif cmd_ == "centralite":
        afficher_centralites(G, args.top)
    elif cmd_ == "communautes":
        afficher_communautes(G)
    elif cmd_ == "amis":
        afficher_amis(G, args.personne, args.top)
    elif cmd_ == "distance":
        gens = analyse.personnes_a_distance(G, args.personne, args.d)
        print(f"{len(gens)} personne(s) à {args.d} degré(s) : {', '.join(map(str, gens))}")
    elif cmd_ == "distances":
        afficher_distances(G)
    elif cmd_ == "dessiner":
        if args.histogramme:
            visualisation.dessiner_distances(G, args.sortie)
        else:
            visualisation.dessiner(G, par_communaute=args.communautes, fichier=args.sortie)
        if args.sortie:
            print(f"Image enregistrée : {args.sortie}")
    elif cmd_ == "exporter":
        reseau.sauvegarder(G, args.fichier)
        print(f"Réseau enregistré : {args.fichier}")
    elif cmd_ == "interactif":
        Interactif(G).cmdloop()


def main(argv=None):
    args = construire_parseur().parse_args(argv)
    try:
        executer(args)
    except (analyse.PersonneInconnue, ValueError, FileNotFoundError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
