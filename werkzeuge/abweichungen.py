"""Abweichungsanalyse (zu zweit): Wo sollte man anders spielen als in der neutralen Lage (Spielbeginn)?

1. Für jeden Spielstand und jede Entscheidungssituation wird die beste Entscheidung mit der Entscheidung
   verglichen, die in der neutralen Lage (Hälfte 1, Mitte 13, 0:0) richtig wäre ("Basis").
   Wirkung = Häufigkeit der Situation pro Spiel x Gewinn (weniger Verlustwahrscheinlichkeit).
2. Für die wirkungsvollsten Situationen lernt ein kleiner Entscheidungsbaum aus allen Spielständen,
   WANN man abweichen sollte (Bedingung auf Mitte, Deckel, Phase).

python werkzeuge/abweichungen.py --spiele 20000
Schreibt ergebnisse/abweichungen.csv und ergebnisse/abweichungen.md.
"""

import argparse
import csv
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.analyse import (NEUTRAL_FOLGER, NEUTRAL_STARTER, Lage, aktion_text, ende_text,  # noqa: E402
                              folger_tabellen, starter_tabellen, vergleiche_zug, wuerfel_text)
from schocken.engine import spiele_spiel  # noqa: E402
from schocken.loeser import GESAMT, NH, W, wahl  # noqa: E402
from schocken.optimal import Optimal2, lade_loesung2  # noqa: E402

ERGEBNISSE = Path(__file__).resolve().parent.parent / "ergebnisse"

PHASEN = ["Hälfte 1", "Hälfte 2 (Gegner verlor H1)", "Finale", "Hälfte 2 (ich verlor H1)"]
MERKMALE = ["Mitte", "meine Deckel", "Gegner-Deckel", "Vorsprung", "Phase"]


def phase(lage: Lage) -> int:
    if lage.haelfte == "Hälfte 1":
        return 0
    if lage.haelfte == "Finale":
        return 2
    return 3 if lage.h1_verlierer == "ich" else 1


def merkmale(lage: Lage):
    return [lage.mitte, lage.ich, lage.gegner, lage.gegner - lage.ich, phase(lage)]


# --------------------------------------------------------------------------- Wie oft kommt welcher Spielstand vor?


class Zaehler:
    def __init__(self):
        self.c = Counter()

    def _zaehle(self, h):
        # Wer Hälfte 1 verloren hat, zählt nur in Hälfte 2 (im Finale ist es egal)
        l1 = h.haelften_verlierer[0] if h.name == "Hälfte 2" else None
        d = h.deckel
        for ich in (0, 1):
            lage = Lage(h.name, None if l1 is None else ("ich" if l1 == ich else "gegner"),
                        h.mitte, d[ich], d[1 - ich], "ich" if h.starter == ich else "gegner")
            self.c[lage] += 1

    def haelfte_start(self, h):
        self._zaehle(h)

    def runde(self, h, r):
        if max(h.deckel.values()) < GESAMT:
            self._zaehle(h)

    def haelfte_ende(self, h, v):
        pass


def _besuche(args):
    seed, n = args
    s = lade_loesung2()
    z = Zaehler()
    rng = random.Random(seed)
    a, b = Optimal2(s), Optimal2(s)
    for i in range(n):
        spiele_spiel([a, b], rng, log=z, starter=i % 2)
    return z.c


def besuche(spiele):
    with Pool(4) as pool:
        teile = pool.map(_besuche, [(k, spiele // 4) for k in range(4)])
    gesamt = Counter()
    for t in teile:
        gesamt.update(t)
    n = 4 * (spiele // 4)
    return {lage: c / (2 * n) for lage, c in gesamt.items()}  # Besuche pro Spiel und Spieler


# --------------------------------------------------------------------------- Tabellen mit Cache


class Rechner:
    def __init__(self, s):
        self.s = s
        self.starter = {}
        self.enden = {}
        self.basis_folger = {}
        self.basis_starter = starter_tabellen(s, NEUTRAL_STARTER)

    def starter_tab(self, lage):
        return starter_tabellen(self.s, lage, self.starter)

    def gegner_enden(self, lage):
        """Verteilung der Zug-Enden des optimal startenden Gegners."""
        if lage not in self.enden:
            t = self.starter_tab(lage)
            _, To, Tv, _ = vergleiche_zug(t.V, t.EV, t.Uo, t.Uv, t.V, t.EV, t.Uo, t.Uv, 3, True, False)
            e = {("o", w, k): To[w, k] for w in range(W) for k in range(1, 4) if To[w, k] > 1e-9}
            e.update({("v", h, k): Tv[h, k] for h in range(NH) for k in range(1, 4) if Tv[h, k] > 1e-9})
            self.enden[lage] = e
        return self.enden[lage]

    def basis_folger_tab(self, ende):
        if ende not in self.basis_folger:
            self.basis_folger[ende] = folger_tabellen(self.s, NEUTRAL_FOLGER, ende)
        return self.basis_folger[ende]


def vergleich(t, b):
    return vergleiche_zug(t.V, t.EV, t.Uo, t.Uv, b.V, b.EV, b.Uo, b.Uv, t.grenze, t.darf, t.vm)


# --------------------------------------------------------------------------- 1. Abweichungen einsammeln


def zeilen(lage, rolle, ende, gewicht, rec):
    for k, d, m, s, p, gewinn, jo, vo, jb, vb in rec:
        k, d, m, s, jo, jb = int(k), int(d), int(m), int(s), int(jo), int(jb)
        yield {
            "haelfte": PHASEN[phase(lage)], "mitte": lage.mitte, "ich": lage.ich, "gegner": lage.gegner,
            "rolle": rolle, "gegner_ergebnis": ende_text(ende) if ende else "",
            "wurf": k, "wuerfel": wuerfel_text(d) if k else "", "neu": m if k else 3,
            "basis": aktion_text(d, m, s, jb, bool(vb)), "besser": aktion_text(d, m, s, jo, bool(vo)),
            "p_situation": gewicht * p, "gewinn": gewinn, "wirkung": gewicht * p * gewinn,
            "_situation": (rolle, ende, k, d, m, s),
        }


def sammle(r: Rechner, besuch):
    for lage, gewicht in sorted(besuch.items(), key=lambda x: -x[1]):
        if lage.start == "ich":
            rec, _, _, _ = vergleich(r.starter_tab(lage), r.basis_starter)
            yield from zeilen(lage, "Startspieler", None, gewicht, rec)
            continue
        for ende, p_ende in r.gegner_enden(lage).items():
            f = folger_tabellen(r.s, lage, ende)
            rec, _, _, _ = vergleich(f, r.basis_folger_tab(ende))
            yield from zeilen(lage, "Folgespieler", ende, gewicht * p_ende, rec)


# --------------------------------------------------------------------------- 2. Regeln lernen


def situationsdaten(r: Rechner, besuch, situation):
    """Für eine Situation: über alle Spielstände, in denen sie vorkommt, die beste Entscheidung."""
    rolle, ende, k, d, m, s = situation
    X, y, gew = [], [], []
    for lage, g in besuch.items():
        if (lage.start == "ich") != (rolle == "Startspieler"):
            continue
        if rolle == "Startspieler":
            t, faktor = r.starter_tab(lage), g
        else:
            p_ende = r.gegner_enden(lage).get(ende, 0.0)
            if p_ende == 0.0:
                continue
            t, faktor = folger_tabellen(r.s, lage, ende), g * p_ende
        if k == 0:
            w = faktor
            aktion = aktion_text(0, 3, 0, -2, bool(t.Uv[0, 1] > t.EV[1, 0] + 1e-12))
        else:
            _, _, _, erreicht = vergleich(t, t)
            w = faktor * erreicht[k, d, m, s]
            j, v = wahl(t.V, t.EV, *t.args, k, d, m, s)
            aktion = aktion_text(d, m, s, j, v)
        if w > 0:
            X.append(merkmale(lage))
            y.append(aktion)
            gew.append(w)
    return np.array(X), np.array(y), np.array(gew)


def _bedingung(grenzen):
    teile = []
    for f, (lo, hi) in sorted(grenzen.items()):
        if MERKMALE[f] == "Phase":
            erlaubt = [PHASEN[i] for i in range(4) if lo < i <= hi]
            if len(erlaubt) < 4:
                teile.append(" oder ".join(erlaubt))
            continue
        name = MERKMALE[f]
        a = int(np.floor(lo)) + 1 if lo > -1e9 else None
        b = int(np.floor(hi)) if hi < 1e9 else None
        if name == "Mitte" and b == 0:
            teile.append("Mitte leer")
        elif name == "Mitte" and a == 1 and b is None:
            teile.append("Mitte nicht leer")
        elif a is not None and b is not None:
            teile.append(f"{name} {a}" if a == b else f"{name} {a} bis {b}")
        elif a is not None:
            teile.append(f"{name} ≥ {a}")
        elif b is not None:
            teile.append(f"{name} ≤ {b}")
    return ", ".join(teile) or "immer"


def lerne_regel(X, y, gew, tiefe=3):
    baum = DecisionTreeClassifier(max_depth=tiefe, min_weight_fraction_leaf=0.02, random_state=0)
    baum.fit(X, y, sample_weight=gew)
    genauigkeit = baum.score(X, y, sample_weight=gew)
    t = baum.tree_
    blaetter = []

    def gehe(knoten, grenzen):
        if t.children_left[knoten] == -1:
            werte = t.value[knoten][0]
            blaetter.append((grenzen, baum.classes_[int(np.argmax(werte))], werte.max() / werte.sum(),
                             t.weighted_n_node_samples[knoten] / t.weighted_n_node_samples[0]))
            return
        f, thr = t.feature[knoten], t.threshold[knoten]
        lo, hi = grenzen.get(f, (-1e10, 1e10))
        gehe(t.children_left[knoten], {**grenzen, f: (lo, min(hi, thr))})
        gehe(t.children_right[knoten], {**grenzen, f: (max(lo, thr), hi)})

    gehe(0, {})
    return blaetter, genauigkeit


# --------------------------------------------------------------------------- Bericht


def typ(aktion):
    if aktion == "fertig":
        return "aufhören"
    if "beginnen" in aktion:
        return aktion
    return "weiter verdeckt" if "VERDECKT" in aktion else "weiter offen"


def situation_text(situation):
    rolle, ende, k, d, m, s = situation
    wo = f"nach Wurf {k}: **{wuerfel_text(d)}** ({m} davon neu geworfen)" if k else "vor dem ersten Wurf"
    return f"{rolle}{', ' + ende_text(ende) if ende else ''}, {wo}"


def bericht(r, besuch, alle, top):
    gesamt = sum(z["wirkung"] for z in alle)
    md = [
        "# Abweichungen von der Basis-Strategie (zu zweit)", "",
        "Basis = die optimale Entscheidung in der neutralen Lage (Hälfte 1, Spielbeginn, 0:0).",
        "Gesucht sind Situationen, in denen der Spielstand eine andere Entscheidung verlangt.", "",
        "- **Gewinn**: um so viele Prozentpunkte sinkt die eigene Wahrscheinlichkeit, das Spiel zu verlieren.",
        "- **Wirkung**: Gewinn × Häufigkeit der Situation, in Prozentpunkten pro Spiel.",
        "- **Regel**: von einem Entscheidungsbaum aus allen Spielständen gelernt; *Treffer* = Anteil der "
        "Fälle (gewichtet nach Häufigkeit), in denen die Regel die optimale Entscheidung trifft.",
        "- **Vorsprung** = Deckel des Gegners − meine Deckel (positiv: ich liege vorn).",
        "- **halte 11 VERDECKT** = diese Würfel liegen lassen, den Rest verdeckt werfen (stehen lassen).", "",
        f"Situationen mit Abweichung: {len(alle)}. Summe der Wirkung: **{gesamt * 100:.2f} Prozentpunkte "
        "pro Spiel**: so viel weniger verliert man (näherungsweise), wenn man den Spielstand beachtet.", "",
        "## Muster", "",
        "| Rolle | Wurf | Basis | Besser | Situationen | Wirkung (%-Pkt./Spiel) |", "|---|---|---|---|---|---|",
    ]
    muster = defaultdict(lambda: [0, 0.0])
    for z in alle:
        schl = (z["rolle"], z["wurf"], typ(z["basis"]), typ(z["besser"]))
        muster[schl][0] += 1
        muster[schl][1] += z["wirkung"]
    for (rolle, wurf, b, o), (n, w) in sorted(muster.items(), key=lambda x: -x[1][1]):
        if w * 100 >= 0.001:
            md.append(f"| {rolle} | {wurf or 'vor 1.'} | {b} | {o} | {n} | {w * 100:.3f} |")

    situationen = defaultdict(list)
    for z in alle:
        situationen[z["_situation"]].append(z)
    sortiert = sorted(situationen.items(), key=lambda x: -sum(z["wirkung"] for z in x[1]))
    md += ["", f"## Die {top} wirkungsvollsten Situationen und wann man abweichen sollte", ""]
    for i, (situation, zs) in enumerate(sortiert[:top], 1):
        w = sum(z["wirkung"] for z in zs)
        g = max(z["gewinn"] for z in zs)
        basis = zs[0]["basis"]
        X, y, gew = situationsdaten(r, besuch, situation)
        blaetter, genauigkeit = lerne_regel(X, y, gew)
        md.append(f"### {i}. {situation_text(situation)}")
        md.append(f"Basis: *{basis}*. Wirkung {w * 100:.3f} %-Pkt./Spiel, Gewinn bis {g * 100:.1f} %-Pkt. "
                  f"Regel-Treffer {genauigkeit * 100:.0f} %.")
        md.append("")
        for grenzen, aktion, rein, anteil in sorted(blaetter, key=lambda b: (b[1] == basis, -b[3])):
            marke = "**" if aktion != basis else ""
            md.append(f"- {_bedingung(grenzen)} → {marke}{aktion}{marke} "
                      f"(stimmt in {rein * 100:.0f} %, {anteil * 100:.0f} % der Fälle)")
        md.append("")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spiele", type=int, default=20000, help="Simulierte Spiele für die Häufigkeiten")
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()
    s = lade_loesung2()
    r = Rechner(s)

    t = time.time()
    besuch = besuche(a.spiele)
    print(f"{len(besuch)} Spielstände, Häufigkeiten aus {a.spiele} Spielen ({time.time() - t:.0f}s)")
    t = time.time()
    alle = list(sammle(r, besuch))
    print(f"{len(alle)} Situationen mit Abweichung gefunden ({time.time() - t:.0f}s)")

    ERGEBNISSE.mkdir(exist_ok=True)
    felder = [k for k in alle[0] if not k.startswith("_")]
    with open(ERGEBNISSE / "abweichungen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=felder, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for z in sorted(alle, key=lambda z: -z["wirkung"]):
            w.writerow(z)
    t = time.time()
    text = bericht(r, besuch, alle, a.top)
    print(f"Regeln gelernt ({time.time() - t:.0f}s)")
    (ERGEBNISSE / "abweichungen.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
