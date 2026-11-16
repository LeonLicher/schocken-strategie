# Schocken

Schocken zum Spielen (Browser oder Terminal) und zum Berechnen der besten Strategie. Die Regeln stehen in
[REGELN.md](REGELN.md), die Erkenntnisse in [ERGEBNISSE.md](ERGEBNISSE.md).

## Spielen im Browser

```
python -m schocken.web
```

Öffnet http://localhost:8765. Würfel anklicken = liegen lassen; Knöpfe für Würfeln, Verdeckt würfeln, Fertig
und Sechsen drehen. Die Züge der Gegner laufen Wurf für Wurf ab (Tempo einstellbar). Mit **Tipps** siehst du
nach jeder Entscheidung, was am besten gewesen wäre, und am Ende deine teuersten Fehler.

Gegner:
- **Stammtisch**: wie am Tisch üblich (Startspieler hört mit einer Eins nach dem 2. Wurf auf, die anderen jagen den Schock).
- **Konter**: exakt berechnete beste Antwort auf Stammtisch-Spieler (2 und 3 Spieler).
- **Optimal**: perfektes Spiel, wenn alle perfekt spielen (nur zu zweit).
- **Faustregel**: einfacher Bot.

### Online-Version (GitHub Pages)

**https://leonlicher.github.io/schocken-strategie/** — mit Ansicht „Am Tisch“ (Becher, Würfeln, Bierdeckel).

`site/` ist dasselbe Spiel komplett im Browser (JavaScript, ohne Server). Bei jedem Push nach `main` prüft
eine GitHub Action, dass die Browser-Version exakt wie Python rechnet (`node tests/js/vergleich.mjs`,
`node tests/js/spiel.mjs`), und veröffentlicht die Seite. Nach neuen Lösungen die Daten aktualisieren:
`python werkzeuge/export_web.py`.

Lokal ansehen: `python -m http.server -d site 8000` und http://localhost:8000 öffnen.

## Spielen im Terminal

```
python -m schocken --spieler mensch,stammtisch,konter
```

Strategien: `mensch`, `stammtisch`, `konter`, `optimal`, `faustregel`, `zufall`. Mit `--seed` lässt sich ein Spiel wiederholen.

## Tests

```
python -m unittest discover -s tests -t .
```

## Aufbau

- `schocken/wertung.py`: Bewertung eines Wurfs (Rang und Deckel).
- `schocken/engine.py`: Zug, Runde, Hälfte und Spiel; erlaubte Aktionen; `Sicht` = was ein Spieler weiß;
  optionaler Beobachter für jeden Wurf und jede Entscheidung.
- `schocken/bots.py`: `Stammtisch`, `Faustregel`, `Zufall`, Parameter-Strategien.
- `schocken/cli.py`: Terminal-Spiel. `schocken/web/`: Browser-Spiel (lokaler Server, nur Python-Standardbibliothek).
- `schocken/schnell.py`: Schneller Simulator (Numba, ~275.000 Spiele/s) für Parameter-Strategien.
- `schocken/loeser.py`: Exakte Lösung zu zweit (Zug-Löser, Runde, Wertiteration über alle Deckelstände).
- `schocken/optimal.py`: `Optimal2`, spielt zu zweit exakt optimal.
- `schocken/konter.py`: Konter, die beste Antwort auf Stammtisch-Gegner (2 und 3 Spieler).
- `schocken/analyse.py`: Abfragen und Abweichungsanalyse der 2-Spieler-Lösung.

Werkzeuge (`werkzeuge/`):
- `loese2.py`: löst das Spiel zu zweit (~45 s) → `ergebnisse/loesung2.pkl`.
- `loese_konter.py --spieler 2|3`: löst Konter (2 Kerne, niedrige Priorität) → `ergebnisse/konter2.pkl`, `konter3.pkl`.
- `pruefe_optimal2.py`, `pruefe_konter.py`, `vergleich.py`: prüfen Lösungen und Simulator per Simulation.
- `situation.py`: beste Entscheidung in einer beliebigen Situation nachschlagen (`--help`).
- `abweichungen.py`, `abweichungen_seite.py`: Abweichungsanalyse → `ergebnisse/abweichungen.md` / `.html`.
- `analyse2.py`, `parametersuche.py`: weitere Auswertungen.

Abhängigkeiten für Simulator und Lösungen: `pip install numpy numba scikit-learn`.

Eigene Strategie: von `engine.Strategie` erben und `entscheide(sicht) -> Aktion` implementieren.
