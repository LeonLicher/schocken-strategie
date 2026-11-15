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

Eigene Strategie: von `engine.Strategie` erben und `entscheide(sicht) -> Aktion` implementieren.

## Fahrplan

1. Engine und Tests (fertig)
2. Terminal-Spiel (fertig, Grundversion)
3. Schneller Simulator und Benchmark der Bots
4. Exakte Lösung: beste Entscheidung pro Situation (Rückwärtsrechnung)
5. Auswertung und Spickzettel
