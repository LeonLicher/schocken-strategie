# Schocken

Schocken im Terminal und eine Grundlage, um die optimale Strategie zu berechnen. Die Regeln stehen in [REGELN.md](REGELN.md).

## Spielen

```
python -m schocken --spieler mensch,faustregel,faustregel
python -m schocken --spieler faustregel,zufall,faustregel --seed 3
```

Strategien: `mensch`, `faustregel`, `zufall`. Mit `--seed` lässt sich ein Spiel wiederholen.

## Tests

```
python -m unittest discover -s tests -t .
```

## Aufbau

- `schocken/wertung.py`: Bewertung eines Wurfs (Rang und Deckel).
- `schocken/engine.py`: Zug, Runde, Hälfte und Spiel; erlaubte Aktionen; `Sicht` = was ein Spieler weiß.
- `schocken/bots.py`: Vergleichs-Strategien (`Zufall`, `Faustregel`).
- `schocken/cli.py`: Terminal-Spiel.
- `schocken/schnell.py`: Schneller Simulator (Numba, alle Kerne, ~275.000 Spiele/s) für Parameter-Strategien.
- `werkzeuge/vergleich.py`: Prüft den Simulator statistisch gegen die Engine.
- `werkzeuge/parametersuche.py`: Sucht die beste Parameter-Strategie gegen ein Faustregel-Feld.

Abhängigkeiten für Simulator und Lösung: `pip install numpy numba`.

Eigene Strategie: von `engine.Strategie` erben und `entscheide(sicht) -> Aktion` implementieren.

## Fahrplan

1. Engine und Tests (fertig)
2. Terminal-Spiel (fertig, Grundversion)
3. Schneller Simulator und Benchmark der Bots (fertig)
4. Exakte Lösung: beste Entscheidung pro Situation (Rückwärtsrechnung)
5. Auswertung und Spickzettel
