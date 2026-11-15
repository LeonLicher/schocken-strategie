"""Erzeugt die lesbare Abweichungs-Seite ergebnisse/abweichungen.html.

Für die wirkungsvollsten Situationen wird für jeden Spielstand (meine Deckel x Gegner-Deckel, je Phase)
berechnet, was optimal ist und wie viel das gegenüber der normalen Spielweise (Spielbeginn) bringt.

python werkzeuge/abweichungen_seite.py --spiele 20000 --anzahl 40
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from abweichungen import (PHASEN, Rechner, besuche, lerne_regel, sammle, situationsdaten, typ,  # noqa: E402
                          vergleich, _bedingung)
from schocken.analyse import Lage, _q, aktion_text, folger_tabellen  # noqa: E402
from schocken.loeser import (ACT_H, ACT_T, D_LISTE, GESAMT, H_LISTE, WERTUNGEN, behalten_von,  # noqa: E402
                             wahl)
from schocken.optimal import lade_loesung2  # noqa: E402

HIER = Path(__file__).resolve().parent
ZIEL = HIER.parent / "ergebnisse" / "abweichungen.html"
PHASEN_SCHLUESSEL = [("Hälfte 1", None), ("Hälfte 2", "gegner"), ("Finale", None), ("Hälfte 2", "ich")]


# --------------------------------------------------------------------------- Klartext


def wuerfel_liste(werte):
    return sorted(werte, reverse=True)


def aktion(d, m, s, j, verdeckt):
    """Aktion als Datensatz für die Seite: Kategorie, Kurz- und Langtext, alter Name (für die Kurzregel)."""
    a = _aktion(d, m, s, j, verdeckt)
    a["alt"] = aktion_text(d, m, s, j, verdeckt)
    return a


def _aktion(d, m, s, j, verdeckt):
    if j == -2:
        return {"kat": "verdeckt" if verdeckt else "offen", "kurz": "verdeckt anfangen" if verdeckt else "offen anfangen",
                "lang": "Den ersten Wurf verdeckt stehen lassen" if verdeckt else "Offen anfangen"}
    if j < 0:
        return {"kat": "stopp", "kurz": "stehen lassen", "lang": "Fertig: den Wurf so stehen lassen"}
    h, t = int(ACT_H[d, m, s, j]), int(ACT_T[d, m, s, j])
    liegen = list(behalten_von(h, t))
    neu = 3 - len(H_LISTE[h])
    teile = []
    if t:
        teile.append(f"{t + 1} Sechsen zu {'einer Eins' if t == 1 else 'zwei Einsen'} drehen")
    if liegen:
        teile.append("-".join(map(str, wuerfel_liste(liegen))) + " liegen lassen")
    if neu == 3:
        teile.append("alle drei neu werfen")
    else:
        teile.append(f"{'einen Würfel' if neu == 1 else 'zwei Würfel'} neu werfen")
    halten = wuerfel_liste(liegen + [1] * t)
    if verdeckt:
        teile[-1] += ", verdeckt (stehen lassen)"
    kurz = ("halte " + "-".join(map(str, halten)) if halten else "alle neu") + (", verdeckt" if verdeckt else "")
    lang = ", ".join(teile)
    return {"kat": "verdeckt" if verdeckt else "weiter", "kurz": kurz, "lang": lang[0].upper() + lang[1:]}


def gegner_daten(ende):
    if ende is None:
        return None
    art, x, k = ende
    if art == "v":
        return {"verdeckt": True, "wuerfe": k, "sichtbar": wuerfel_liste(H_LISTE[x])}
    return {"verdeckt": False, "wuerfe": k, "wertung": WERTUNGEN[x].name}


def thema(rolle, d):
    if rolle == "Folgespieler":
        return "zweiter"
    einsen = D_LISTE[d].count(1)
    return "schock" if einsen >= 2 else ("eins" if einsen == 1 else "ohne")


# --------------------------------------------------------------------------- Karten berechnen


class Karten:
    def __init__(self, r: Rechner, besuch):
        self.r = r
        self.besuch = besuch
        self.erreicht = {}
        self.folger = {}

    def _erreicht(self, schluessel, t):
        if schluessel not in self.erreicht:
            self.erreicht[schluessel] = vergleich(t, t)[3]
        return self.erreicht[schluessel]

    def zelle(self, situation, lage, basis):
        rolle, ende, k, d, m, s = situation
        if rolle == "Startspieler":
            t, haeufig = self.r.starter_tab(lage), self.besuch.get(lage, 0.0)
            erreicht_schl = ("s", lage)
        else:
            schl = (lage, ende)
            if schl not in self.folger:
                self.folger[schl] = folger_tabellen(self.r.s, lage, ende)
            t = self.folger[schl]
            haeufig = self.besuch.get(lage, 0.0) * self.r.gegner_enden(lage).get(ende, 0.0)
            erreicht_schl = ("f", lage, ende)
        if k == 0:
            vo = bool(t.Uv[0, 1] > t.EV[1, 0] + 1e-12)
            vb = bool(basis.Uv[0, 1] > basis.EV[1, 0] + 1e-12)
            q = {True: t.Uv[0, 1], False: t.EV[1, 0]}
            return aktion(0, 3, 0, -2, vo), float(q[vo] - q[vb]), haeufig
        jo, vo = wahl(t.V, t.EV, *t.args, k, d, m, s)
        jb, vb = wahl(basis.V, basis.EV, *basis.args, k, d, m, s)
        gewinn = (_q(t.V, t.EV, t.Uo, t.Uv, t.grenze, t.darf, t.vm, k, d, m, s, jo, vo)
                  - _q(t.V, t.EV, t.Uo, t.Uv, t.grenze, t.darf, t.vm, k, d, m, s, jb, vb))
        if haeufig > 0:
            haeufig *= self._erreicht(erreicht_schl, t)[k, d, m, s]
        return aktion(d, m, s, jo, vo), float(gewinn), haeufig

    def karte(self, situation, basis):
        rolle = situation[0]
        aktionen, karten = [], []
        for haelfte, h1 in PHASEN_SCHLUESSEL:
            gitter = []
            for gegner in range(GESAMT):
                zeile = []
                for ich in range(GESAMT):
                    mitte = GESAMT - ich - gegner
                    ich_start = rolle == "Startspieler"
                    if mitte < 0 or (mitte == 0 and (ich > gegner) != ich_start):
                        zeile.append(None)
                        continue
                    lage = Lage(haelfte, h1, mitte, ich, gegner, "ich" if ich_start else "gegner")
                    a, gewinn, haeufig = self.zelle(situation, lage, basis)
                    if a["kurz"] not in [x["kurz"] for x in aktionen]:
                        aktionen.append(a)
                    idx = [x["kurz"] for x in aktionen].index(a["kurz"])
                    zeile.append([idx, round(gewinn * 100, 2), round(haeufig, 6)])
                gitter.append(zeile)
            karten.append(gitter)
        return aktionen, karten


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spiele", type=int, default=20000)
    ap.add_argument("--anzahl", type=int, default=40)
    a = ap.parse_args()
    s = lade_loesung2()
    r = Rechner(s)

    t0 = time.time()
    besuch = besuche(a.spiele)
    alle = list(sammle(r, besuch))
    print(f"Analyse: {len(alle)} Abweichungen ({time.time() - t0:.0f}s)")

    gesamt = sum(z["wirkung"] for z in alle)
    muster = defaultdict(float)
    for z in alle:
        muster[(z["rolle"], z["wurf"], typ(z["basis"]), typ(z["besser"]))] += z["wirkung"]

    gruppen = defaultdict(list)
    for z in alle:
        gruppen[z["_situation"]].append(z)
    top = sorted(gruppen.items(), key=lambda x: -sum(z["wirkung"] for z in x[1]))[: a.anzahl]

    k = Karten(r, besuch)
    situationen = []
    t0 = time.time()
    for rang, (situation, zs) in enumerate(top, 1):
        rolle, ende, wurf, d, m, sx = situation
        basis = r.basis_starter if rolle == "Startspieler" else r.basis_folger_tab(ende)
        aktionen, karten = k.karte(situation, basis)
        jb, vb = (wahl(basis.V, basis.EV, *basis.args, wurf, d, m, sx) if wurf else (-2, False))
        if wurf == 0:
            vb = bool(basis.Uv[0, 1] > basis.EV[1, 0] + 1e-12)
        basis_aktion = aktion(d, m, sx, jb, vb)
        X, y, gew = situationsdaten(r, besuch, situation)
        blaetter, genauigkeit = lerne_regel(X, y, gew)
        kurzregel = [{"wenn": _bedingung(g), "dann": akt, "stimmt": round(rein * 100), "anteil": round(ant * 100)}
                     for g, akt, rein, ant in sorted(blaetter, key=lambda b: -b[3])]
        situationen.append({
            "rang": rang, "rolle": rolle, "thema": thema(rolle, d), "wurf": wurf,
            "wuerfel": wuerfel_liste(D_LISTE[d]) if wurf else [], "neu": m if wurf else 3,
            "gegner": gegner_daten(ende),
            "wirkung": round(sum(z["wirkung"] for z in zs) * 100, 3),
            "gewinn_max": round(max(z["gewinn"] for z in zs) * 100, 1),
            "basis": basis_aktion, "aktionen": aktionen, "karten": karten,
            "kurzregel": kurzregel, "regel_treffer": round(genauigkeit * 100),
        })
        print(f"  {rang:2d}/{len(top)} fertig ({time.time() - t0:.0f}s)")

    daten = {
        "stand": time.strftime("%Y-%m-%d"),
        "gesamt": round(gesamt * 100, 2), "anzahl_abweichungen": len(alle),
        "phasen": PHASEN,
        "muster": [{"rolle": ro, "wurf": w, "basis": b, "besser": o, "wirkung": round(v * 100, 3)}
                   for (ro, w, b, o), v in sorted(muster.items(), key=lambda x: -x[1]) if v * 100 >= 0.005],
        "situationen": situationen,
    }
    vorlage = (HIER / "abweichungen_vorlage.html").read_text(encoding="utf-8")
    ZIEL.write_text(vorlage.replace("__DATEN__", json.dumps(daten, ensure_ascii=False, separators=(",", ":"))),
                    encoding="utf-8")
    print(f"Geschrieben: {ZIEL} ({ZIEL.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
