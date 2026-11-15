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

### Wann sich Abweichen lohnt (Abweichungsanalyse)

Verglichen wird die optimale Entscheidung in jedem Spielstand mit der Entscheidung, die in der neutralen
Lage (Spielbeginn, 0:0) richtig ist. Alle Situationen mit Regeln: [ergebnisse/abweichungen.md](ergebnisse/abweichungen.md)
(`python werkzeuge/abweichungen.py`). Einzelne Situation nachschlagen: `python werkzeuge/situation.py --help`.

Wer den Spielstand beachtet, verliert rund **3,7 Prozentpunkte** seltener als jemand, der immer wie
zu Spielbeginn spielt. Die wichtigsten Muster:

1. **Startspieler, 2. Wurf, eine Eins plus zwei schwache Würfel** (z. B. 4-2-1, 5-3-1):
   Zu Spielbeginn aufhören. Sobald man selbst 2 oder mehr Deckel hat oder die Mitte leer ist:
   **die Eins halten und den Rest verdeckt nachwerfen.** Größte Einzelwirkung (zusammen 1,4 %-Pkt./Spiel).
2. **Schock 5 oder Schock 6 bei leerer Mitte: sofort aufhören**, statt auf Schock Aus zu gehen.
   Mit voller Mitte hält man dagegen die beiden Einsen und wirft weiter.
3. **Folgespieler gegen verdeckten Gegner (sichtbar eine Eins):** Mit 6-1-1 oder 5-1-1 offen
   aufhören, sobald der Gegner 2 oder mehr Deckel hat. Zu Spielbeginn würde man blind weiterwerfen.
4. **Startspieler, 1. Wurf, schwacher Wurf ohne Eins** (3-2-2, 3-3-2, 4-2-2): zu Spielbeginn fertig;
   wenn die Mitte (fast) leer ist und man selbst Deckel hat, besser alle drei neu werfen.
5. **Startspieler, 1. Wurf, 3-2-1:** normalerweise die Eins halten; hat der Gegner 5 bis 6 Deckel
   (oder 7+ und ich wenige), sofort aufhören.

Beispiel (Finale, eigener Start, Mitte leer, 7 : 6, nach Wurf 2 ohne Eins): **aufhören** ist bei jedem
Wurf richtig, genau wie zu Spielbeginn. Hat man dort aber eine Eins (z. B. 5-4-1), sollte man die Eins
halten und verdeckt nachwerfen (bis 2,5 %-Pkt. besser); mit 5-1-1 aufhören (5,2 %-Pkt. besser).

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
