"""Lokale Spiel-Website: python -m schocken.web  (öffnet http://localhost:8765)

Der Spielablauf läuft in einem eigenen Thread mit der normalen Engine. Ein Mensch-Spieler wartet dort,
bis die Website eine Aktion schickt. Alle Würfe und Entscheidungen werden als Ereignisse gesammelt;
die Seite holt sie ab und spielt sie nacheinander ab.
"""

import json
import os
import queue
import random
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("NUMBA_NUM_THREADS", "1")

from ..bots import Faustregel, Stammtisch  # noqa: E402
from ..engine import Aktion, Sicht, Strategie, legale_aktionen, spiele_spiel  # noqa: E402
from ..konter import Konter, datei as konter_datei, lade_konter  # noqa: E402
from ..loeser import H_ID, W_VON, D_ID, zug_dp  # noqa: E402
from ..optimal import Optimal2, lade_loesung2  # noqa: E402

HIER = Path(__file__).resolve().parent
PORT = 8765

BOTS = {
    "stammtisch": "Stammtisch",
    "konter": "Konter",
    "optimal": "Optimal",
    "faustregel": "Faustregel",
}


def verfuegbar(n):
    """Welche Bots und Berater es für n Spieler gibt."""
    bots = ["stammtisch", "faustregel"]
    berater = []
    if n == 2:
        bots += ["optimal"]
        berater += ["optimal"]
    from ..mehr import datei as werte_datei
    if konter_datei(n).exists() or (n >= 4 and werte_datei(n).exists()):
        bots += ["konter"]
        berater += ["konter"]
    return {"bots": bots, "berater": berater}


# --------------------------------------------------------------------------- Bewertung von Aktionen (Tipps)


class Berater:
    """Bewertet alle erlaubten Aktionen: P(ich verliere das Spiel) je Aktion."""

    def __init__(self, art):
        self.art = art
        if art == "optimal":
            self.bot = Optimal2(lade_loesung2())
        else:
            self.bot = Konter({2: lade_konter(2), **({3: lade_konter(3)} if konter_datei(3).exists() else {})})

    def tabellen(self, sicht):
        if self.art == "optimal":
            V, EV, (Uo, Uv, grenze, darf, vm), _ = self.bot._tabellen(sicht)
            umrechnen = (lambda q: -q) if sicht.ist_starter else (lambda q: 1.0 - q)
        else:
            Uo, Uv, grenze, darf, vm = self.bot.tabellen(sicht)
            _, V, EV = zug_dp(Uo, Uv, grenze, darf, vm)
            umrechnen = lambda q: -q  # noqa: E731
        return Uo, Uv, EV, umrechnen

    def optionen(self, sicht: Sicht):
        Uo, Uv, EV, umrechnen = self.tabellen(sicht)
        aus = []
        for a in legale_aktionen(sicht):
            if sicht.phase == "vor_wurf":
                q = Uv[0, 1] if a.verdeckt else EV[1, 0]
            elif a.stopp:
                d = D_ID[tuple(sorted(sicht.wuerfel))]
                q = Uo[W_VON[d, 1 if len(sicht.neu) == 3 else 0], sicht.wurf_nr]
            else:
                h = H_ID[tuple(sorted(a.behalten + (1,) * a.drehen))]
                q = Uv[h, sicht.wurf_nr + 1] if a.verdeckt else EV[sicht.wurf_nr + 1, h]
            aus.append({"aktion": aktion_json(a), "text": aktion_text(a, sicht), "p": float(umrechnen(q))})
        return sorted(aus, key=lambda o: o["p"])


# --------------------------------------------------------------------------- Texte und JSON


def aktion_json(a: Aktion):
    return {"stopp": a.stopp, "behalten": list(a.behalten), "drehen": a.drehen, "verdeckt": a.verdeckt}


def aktion_text(a: Aktion, sicht=None, du=True) -> str:
    if sicht is not None and sicht.phase == "vor_wurf":
        return ("würfelt verdeckt" if not du else "Verdeckt würfeln") if a.verdeckt else \
            ("würfelt offen" if not du else "Offen würfeln")
    if a.stopp:
        return "Fertig (stehen lassen)" if du else "lässt stehen"
    teile = []
    if a.drehen:
        teile.append(f"{'6-6' if a.drehen == 1 else '6-6-6'} zu {'1' if a.drehen == 1 else '1-1'} drehen" if du else
                     f"dreht {'6-6' if a.drehen == 1 else '6-6-6'} zu {'1' if a.drehen == 1 else '1-1'}")
    gehalten = sorted(a.behalten, reverse=True)
    neu = 3 - len(a.behalten) - a.drehen
    if gehalten:
        teile.append(("halten: " if du else "hält ") + "-".join(map(str, gehalten)))
    teile.append((f"{neu} neu würfeln" if du else f"würfelt {neu} neu") + (" (verdeckt)" if a.verdeckt else ""))
    text = ", ".join(teile)
    return text[0].upper() + text[1:] if du else text


def ergebnis_json(e):
    return {"spieler": e.spieler, "wuerfe": e.wuerfe, "verdeckt": e.verdeckt, "sichtbar": list(e.sichtbar),
            "wuerfel": list(e.wuerfel) if e.wuerfel else None,
            "wertung": e.wertung.name if e.wertung else None}


# --------------------------------------------------------------------------- Sitzung


class Abbruch(Exception):
    pass


class WebMensch(Strategie):
    name = "Du"

    def __init__(self, sitzung):
        self.sitzung = sitzung

    def entscheide(self, sicht: Sicht) -> Aktion:
        return self.sitzung.frage_mensch(sicht)


class Sitzung:
    def __init__(self, typen, tipps, berater_art, seed=None):
        self.typen = typen
        self.n = len(typen)
        self.ereignisse = []
        self.offen = None
        self.antworten = queue.Queue()
        self.abgebrochen = False
        self.fertig = False
        self.fehler = None
        self.lock = threading.Lock()
        self.berater = Berater(berater_art) if tipps and berater_art else None
        self.rng = random.Random(seed)
        loesungen = {}
        strategien = []
        for t in typen:
            if t == "mensch":
                strategien.append(WebMensch(self))
            elif t == "stammtisch":
                strategien.append(Stammtisch())
            elif t == "faustregel":
                strategien.append(Faustregel())
            elif t == "optimal":
                strategien.append(Optimal2(lade_loesung2()))
            elif t == "konter":
                for k in (2, self.n):
                    if k not in loesungen and konter_datei(k).exists():
                        loesungen[k] = lade_konter(k)
                strategien.append(Konter(loesungen))
        self.namen = []
        zaehler = {}
        for t in typen:
            basis = "Du" if t == "mensch" else BOTS[t]
            zaehler[basis] = zaehler.get(basis, 0) + 1
            self.namen.append(basis if typen.count(t) == 1 or t == "mensch" else f"{basis} {zaehler[basis]}")
        self.strategien = strategien
        self.thread = threading.Thread(target=self._lauf, daemon=True)

    # --- Ereignisse
    def melde(self, typ, **daten):
        with self.lock:
            self.ereignisse.append({"typ": typ, **daten})

    def _lauf(self):
        try:
            e = spiele_spiel(self.strategien, self.rng, log=self)
            self.melde("spiel_ende", verlierer=e.verlierer, haelften=e.haelften_verlierer)
        except Abbruch:
            return
        except Exception as ex:  # Fehler sichtbar machen statt still zu hängen
            self.fehler = repr(ex)
            self.melde("fehler", text=repr(ex))
        self.fertig = True

    # Engine-Beobachter
    def haelfte_start(self, h):
        self.melde("haelfte_start", name=h.name, teilnehmer=list(h.teilnehmer))

    def runde_start(self, reihenfolge):
        self.melde("runde_start", reihenfolge=reihenfolge)

    def wurf(self, spieler, wurf_nr, gehalten, neu, verdeckt):
        self.melde("wurf", spieler=spieler, wurf_nr=wurf_nr, gehalten=list(gehalten),
                   neu=list(neu) if neu is not None else None, verdeckt=verdeckt)

    def aktion(self, spieler, wurf_nr, aktion):
        sicht_vor = self.typen[spieler] == "mensch"
        self.melde("aktion", spieler=spieler, wurf_nr=wurf_nr, text=aktion_text(aktion, None, du=False)
                   if wurf_nr else ("würfelt verdeckt" if aktion.verdeckt else "würfelt offen"),
                   aktion=aktion_json(aktion), mensch=sicht_vor)

    def zug_ende(self, ergebnis):
        self.melde("zug_ende", ergebnis=ergebnis_json(ergebnis))

    def runde(self, h, r):
        self.melde("runde_ende", ergebnisse=[ergebnis_json(e) for e in r.ergebnisse], hoch=r.hoch.spieler,
                   tief=r.tief.spieler, deckel_bewegt=r.deckel_bewegt, deckel=dict(h.deckel), mitte=h.mitte,
                   naechster=h.starter, schock_aus=bool(r.hoch.wertung.ist_schock_aus))

    def haelfte_ende(self, h, verlierer):
        self.melde("haelfte_ende", name=h.name, verlierer=verlierer)

    # --- Mensch
    def frage_mensch(self, sicht: Sicht) -> Aktion:
        legal = legale_aktionen(sicht)
        offen = {
            "spieler": sicht.spieler, "phase": sicht.phase, "wurf_nr": sicht.wurf_nr,
            "wuerfel": list(sicht.wuerfel), "neu": list(sicht.neu), "grenze": sicht.grenze,
            "ist_starter": sicht.ist_starter, "verdeckt_modus": sicht.verdeckt_modus,
            "legal": [aktion_json(a) for a in legal], "nach_mir": sicht.nach_mir,
            "nummer": len(self.ereignisse),
        }
        if self.berater is not None:
            try:
                offen["optionen"] = self.berater.optionen(sicht)
            except Exception as ex:
                offen["optionen_fehler"] = repr(ex)
        with self.lock:
            self.offen = offen
        a = self.antworten.get()  # bereits in /api/aktion geprüft; offen wurde dort geleert
        if a is None:
            raise Abbruch()
        return a

    def beende(self):
        self.abgebrochen = True
        self.antworten.put(None)


SITZUNG = {"aktiv": None}


# --------------------------------------------------------------------------- HTTP


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, daten, code=200):
        body = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            body = (HIER / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/verfuegbar":
            self._json({str(n): verfuegbar(n) for n in range(2, 7)})
        elif url.path == "/api/zustand":
            s = SITZUNG["aktiv"]
            if s is None:
                return self._json({"aktiv": False})
            ab = int(parse_qs(url.query).get("ab", ["0"])[0])
            with s.lock:
                self._json({"aktiv": True, "ereignisse": s.ereignisse[ab:], "anzahl": len(s.ereignisse),
                            "offen": s.offen, "fertig": s.fertig, "namen": s.namen, "fehler": s.fehler})
        else:
            self._json({"fehler": "unbekannt"}, 404)

    def do_POST(self):
        url = urlparse(self.path)
        daten = self._body()
        if url.path == "/api/start":
            alt = SITZUNG["aktiv"]
            if alt is not None:
                alt.beende()
            typen = daten["spieler"]
            v = verfuegbar(len(typen))
            for t in typen:
                if t != "mensch" and t not in v["bots"]:
                    return self._json({"fehler": f"{BOTS.get(t, t)} gibt es für {len(typen)} Spieler (noch) nicht."}, 400)
            berater = daten.get("berater") if daten.get("berater") in v["berater"] else None
            s = Sitzung(typen, bool(daten.get("tipps")), berater)
            SITZUNG["aktiv"] = s
            s.thread.start()
            self._json({"ok": True, "namen": s.namen, "berater": berater})
        elif url.path == "/api/aktion":
            s = SITZUNG["aktiv"]
            if s is None or s.offen is None:
                return self._json({"fehler": "Gerade ist keine Entscheidung offen."}, 400)
            o = s.offen
            a = Aktion(stopp=bool(daten.get("stopp")), behalten=tuple(daten.get("behalten", [])),
                       drehen=int(daten.get("drehen", 0)), verdeckt=bool(daten.get("verdeckt"))).normalisiert()
            if not o["ist_starter"] and not a.stopp:
                # Nicht-Starter: ob verdeckt geworfen wird, bestimmt die Regel, nicht die Eingabe
                a = Aktion(behalten=a.behalten, drehen=a.drehen,
                           verdeckt=o["verdeckt_modus"] and o["wurf_nr"] + 1 == o["grenze"])
            legal = [Aktion(**{**x, "behalten": tuple(x["behalten"])}).normalisiert() for x in o["legal"]]
            if a not in legal:
                return self._json({"fehler": "Dieser Zug ist so nicht erlaubt. Es muss mindestens ein Würfel "
                                             "neu geworfen werden, und Sechsen drehen geht nur mit Sechsen aus "
                                             "dem letzten Wurf."}, 400)
            with s.lock:
                if s.offen is not o:
                    return self._json({"fehler": "Diese Entscheidung ist schon abgeschickt."}, 409)
                s.offen = None
            s.antworten.put(a)
            self._json({"ok": True})
        else:
            self._json({"fehler": "unbekannt"}, 404)


def main():
    port = int(os.environ.get("SCHOCKEN_PORT", PORT))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Schocken läuft auf {url}  (Beenden mit Strg+C)", flush=True)
    if not os.environ.get("SCHOCKEN_OHNE_BROWSER"):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
