import pytest

from six_degrees import analyse, reseau
from six_degrees.cli import main


@pytest.fixture
def G():
    return reseau.reseau_demo()


def test_chemin_et_casse(G):
    assert len(analyse.plus_court_chemin(G, "alice", "FRANK")) - 1 == 4
    assert len(analyse.tous_les_plus_courts_chemins(G, "Alice", "Eve")) == 2


def test_personne_inconnue_suggere(G):
    with pytest.raises(analyse.PersonneInconnue, match="Alice"):
        analyse.plus_court_chemin(G, "Alise", "Bob")


def test_non_connexe():
    G = reseau.reseau_demo()
    G.add_edge("X", "Y")
    assert analyse.plus_court_chemin(G, "Alice", "X") is None
    assert not analyse.statistiques(G)["connexe"]


def test_statistiques_demo(G):
    s = analyse.statistiques(G)
    assert (s["personnes"], s["relations"], s["diametre"]) == (10, 12, 4)
    assert analyse.verification_six_degres(G)["proportion"] == 1.0


def test_generateurs_reproductibles():
    a = reseau.generer("petit-monde", 50, graine=3)
    b = reseau.generer("petit-monde", 50, graine=3)
    assert sorted(a.edges) == sorted(b.edges)
    assert reseau.generer("sans-echelle", 30, graine=1).number_of_nodes() == 30
    with pytest.raises(ValueError):
        reseau.generer("inconnu")


def test_communautes_partitionnent(G):
    groupes = analyse.communautes(G)
    assert set().union(*groupes) == set(G.nodes)
    assert sum(map(len, groupes)) == G.number_of_nodes()


def test_suggestions_amis(G):
    assert analyse.suggestions_amis(G, "Bob")[0][0] == "Charlie"
    assert analyse.personnes_a_distance(G, "Alice", 1) == ["Bob", "Charlie", "Jack"]


@pytest.mark.parametrize("ext", [".json", ".csv", ".graphml"])
def test_aller_retour_fichiers(G, tmp_path, ext):
    f = tmp_path / f"r{ext}"
    reseau.sauvegarder(G, f)
    H = reseau.charger(f)
    assert {frozenset(e) for e in H.edges} == {frozenset(e) for e in G.edges}


def test_charger_erreurs(tmp_path):
    with pytest.raises(FileNotFoundError):
        reseau.charger(tmp_path / "absent.json")
    (tmp_path / "x.xyz").write_text("a")
    with pytest.raises(ValueError):
        reseau.charger(tmp_path / "x.xyz")


def test_cli(capsys, tmp_path):
    assert main(["chemin", "Alice", "Frank", "-o", str(tmp_path / "c.png")]) == 0
    assert "4 degré" in capsys.readouterr().out
    assert (tmp_path / "c.png").stat().st_size > 0
    assert main(["chemin", "Alice", "Zzz"]) == 1
    assert main(["-t", "aleatoire", "-n", "40", "--graine", "1", "stats"]) == 0
