# Ergebnisse

Stand 2026-11-15. Regeln: [REGELN.md](REGELN.md).

## Zu zweit: exakt gelöst

Rückwärtsrechnung über alle Würfelzustände und alle Deckelstände (beide Hälften und Finale);
Ziel jedes Spielers ist, das Spiel möglichst selten zu verlieren.
Rechenzeit: 43 s (`python werkzeuge/loese2.py`).

**Geprüft:** Der Zug-Löser stimmt auf 10 Nachkommastellen mit einer Brute-Force-Suche über die
Engine-Regeln überein (`tests/test_loeser.py`). 40.000 simulierte Spiele Optimal gegen Optimal:
Der Spielbeginner verliert 49,21 % ± 0,49 %, berechnet sind 49,06 %.

| Kennzahl | Wert |
|---|---|
| Spielbeginner verliert das Spiel (beide optimal) | 49,06 % |
| Startspieler des Finales verliert das Finale | 48,13 % |
| Optimal gegen Faustregel: Optimal verliert | 33,3 % ± 0,5 % |

Finale, Mitte leer, Startspieler mit x Deckeln (Gegner 13 − x): Verlustwahrscheinlichkeit
1: 12 %, 3: 27 %, 6: 43 %, 7: 50 %, 9: 61 %, 12: 77 %.

### Was die optimale Strategie tut (Finale-Beginn, Startspieler)

- **Ohne Eins im ersten Wurf: sofort aufhören.** Auch bei 3-2-2. Der Gegner hat dann nur einen Wurf,
  und bei Gleichstand gewinnt der Startspieler. Einzige Ausnahme: 6-6-x, dann Sechsen drehen.
- **Mit einer Eins:** genau die Eins halten und zwei Würfel neu. Mit zwei Einsen: beide halten.
- **Sechsen drehen** lohnt sich immer, wenn es erlaubt ist (6-6-6 im ersten Wurf: zwei Einsen).
- **Der dritte Wurf wird immer verdeckt geworfen.** Dann muss auch der Gegner seinen dritten Wurf
  blind werfen und kann nicht reagieren.
- Würfe verteilt: 52 % ein Wurf, 28 % zwei, 20 % drei (verdeckt).
- Je mehr Deckel man selbst hat, desto öfter geht man bis zum verdeckten dritten Wurf
  (12 Deckel gegen 1: 69 %).

## Drei Spieler: beste Faustregel (Simulation)

Suche über 1152 einfache Parameter-Strategien gegen zwei Faustregel-Spieler (je 50.000 Spiele,
Top 15 nachgemessen mit 2 Mio. Spielen; `python werkzeuge/parametersuche.py`).

- Faustregel gegen Faustregel: 33,3 % (fair).
- Beste gefundene Regel: **31,8 %**. Der Startspieler würfelt alle drei Würfe (außer bei Schock Aus).
  Die anderen hören erst auf, wenn ihr Wurf deutlich über dem schlechtesten offenen Wurf liegt.
  Sechsen werden immer gedreht.
- Schlechteste Regeln (ohne Drehen, Startspieler hört nach Wurf 1 auf): 56–57 %.
- Pauschales Verdecken hilft in dieser einfachen Strategie-Familie nicht. Die exakte 2-Spieler-Lösung
  zeigt aber: Gezielt eingesetzt ist Verdecken sehr wertvoll.

Die 3-Spieler-Ergebnisse sind nur eine beste Antwort auf Faustregel-Gegner, keine exakte Lösung.
