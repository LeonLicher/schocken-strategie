# Ergebnisse

Stand 2026-11-15. Regeln: [REGELN.md](REGELN.md) (inkl. „bei leerer Mitte beginnt, wer die meisten
Deckel hat“).

## Zu zweit: exakt gelöst

Rückwärtsrechnung über alle Würfelzustände und alle Deckelstände (beide Hälften und Finale);
Ziel jedes Spielers ist, das Spiel möglichst selten zu verlieren.
Rechenzeit: rund 45 s (`python werkzeuge/loese2.py`).

**Geprüft:** Der Zug-Löser stimmt auf 10 Nachkommastellen mit einer Brute-Force-Suche über die
Engine-Regeln überein (`tests/test_loeser.py`). 40.000 simulierte Spiele Optimal gegen Optimal:
Der Spielbeginner verliert 48,85 % ± 0,49 %, berechnet sind 49,09 %.

| Kennzahl | Wert |
|---|---|
| Spielbeginner verliert das Spiel (beide optimal) | 49,09 % |
| Startspieler des Finales verliert das Finale | 48,19 % |
| Optimal gegen Faustregel: Optimal verliert | 30,9 % ± 0,5 % |

Finale, Mitte leer (es beginnt, wer mehr Deckel hat), meine Verlustwahrscheinlichkeit bei x eigenen
Deckeln: 1: 27 %, 3: 38 %, 6: 50 %, 7: 50 %, 9: 58 %, 12: 73 %.

### Was die optimale Strategie tut (Finale-Beginn, Startspieler)

- **Ohne Eins im ersten Wurf: sofort aufhören.** Auch bei 3-2-2. Der Gegner hat dann nur einen Wurf,
  und bei Gleichstand gewinnt der Startspieler. Einzige Ausnahme: 6-6-x, dann Sechsen drehen.
- **Mit einer Eins:** genau die Eins halten und zwei Würfel neu. Mit zwei Einsen: beide halten.
- **Sechsen drehen** lohnt sich immer, wenn es erlaubt ist (6-6-6 im ersten Wurf: zwei Einsen).
- **Der dritte Wurf wird immer verdeckt geworfen.** Dann muss auch der Gegner seinen dritten Wurf
  blind werfen und kann nicht reagieren.
- Würfe verteilt: 52 % ein Wurf, 29 % zwei, 19 % drei (verdeckt).
- Bei leerer Mitte geht man umso öfter bis zum verdeckten dritten Wurf, je höher man hinten liegt
  (7 : 6 → 27 %, 12 : 1 → 54 %).

### Wann sich Abweichen lohnt (Abweichungsanalyse)

Verglichen wird die optimale Entscheidung in jedem Spielstand mit der Entscheidung, die in der neutralen
Lage (Spielbeginn, 0:0) richtig ist. **Am leichtesten zu lesen:** [ergebnisse/abweichungen.html](ergebnisse/abweichungen.html)
(Spielstand-Karten je Situation, im Browser öffnen). Alle Situationen mit Regeln als Text: [ergebnisse/abweichungen.md](ergebnisse/abweichungen.md)
(`python werkzeuge/abweichungen.py`). Einzelne Situation nachschlagen: `python werkzeuge/situation.py --help`.

Wer den Spielstand beachtet, verliert rund **5,8 Prozentpunkte** seltener als jemand, der immer wie
zu Spielbeginn spielt. Fast alle wichtigen Abweichungen hängen an einer Frage: **Ist die Mitte leer?**
(Dann beginnt der Spieler mit den meisten Deckeln, und Deckel wandern zwischen den Spielern.)

1. **Schock 6 bei leerer Mitte: stehen lassen**, im 1. wie im 2. Wurf. Zu Spielbeginn hält man die
   zwei Einsen und wirft weiter auf Schock Aus. (Ausnahme im 1. Wurf: Man liegt 6 oder mehr Deckel
   hinten, dann weiter.) 6-1-1 nach dem 2. Wurf mit nur einem neu geworfenen Würfel: immer stehen lassen.
   **Schock 5 im 2. Wurf** ebenso bei leerer Mitte stehen lassen (außer man hat selbst 11 oder 12 Deckel);
   im 1. Wurf nur, wenn der Gegner 8 oder mehr Deckel hat. Größte Wirkung.
2. **Startspieler, 2. Wurf, eine Eins plus schwache Würfel** (2-2-1 bis 6-4-1): Zu Spielbeginn aufhören.
   **Bei leerer Mitte die Eins halten und den Rest verdeckt nachwerfen.** Bei voller Mitte nur, wenn
   man 5 oder mehr Deckel hinten liegt.
3. **Startspieler, 1. Wurf, 3-2-1:** Normalerweise die Eins halten. **Bei leerer Mitte sofort stehen lassen.**
4. **Folgespieler gegen einen verdeckten Gegner** (sichtbar eine Eins), 6-1-1 nach dem 2. Wurf: Zu
   Spielbeginn blind weiterwerfen; **bei leerer Mitte offen stehen lassen.**
5. **Startspieler, 1. Wurf, schwacher Wurf ohne Eins** (3-2-2, 3-3-2, 4-2-2, 5-3-2 …): normalerweise
   fertig. Wenn die Mitte (fast) leer ist und man 6 oder mehr Deckel hinten liegt: alle drei neu werfen.

Beispiel (Finale, eigener Start, Mitte leer, 7 : 6, nach Wurf 2, alle drei neu geworfen):
**ohne Eins aufhören**, genau wie zu Spielbeginn. Abweichungen gibt es nur mit Einsen:
6-1-1 und 5-1-1 stehen lassen (12,5 bzw. 3,3 %-Pkt. besser als weiterzuwerfen); eine Eins plus
schwache Würfel: Eins halten, verdeckt nachwerfen (bis 1 %-Pkt. besser).

## Gegen Stammtisch-Spieler: Konter (exakt)

**Stammtisch-Spielweise** (Modell, `bots.stammtisch_entscheidung`): Sonderwürfe (Straße, General, Schock)
bleiben stehen. Der Startspieler hört ab dem 2. Wurf mit einer Eins auf, ohne Eins wirft er alle drei neu.
Alle anderen halten Einsen und jagen den Schock, ohne auf die anderen zu achten. Sechsen werden gedreht,
verdeckt wird nie.

**Konter** ist die exakt berechnete beste Antwort darauf (`python werkzeuge/loese_konter.py`).
Weil Stammtisch-Spieler nicht auf andere reagieren, ist das viel einfacher zu rechnen als das echte Optimum.

| Spieler am Tisch | Konter verliert | fair wäre | geprüft per Simulation |
|---|---|---|---|
| 2 | **26,0 %** | 50 % | 26,2 % ± 0,9 % (10.000 Spiele) |
| 3 | **14,0 %** | 33,3 % | 14,0 % ± 0,8 % (8.000 Spiele) |
| 4 | **8,6 %** (Näherung) | 25 % | 8,6 % ± 1,4 % (1.600 Spiele) |
| 5 | **6,3 %** (Näherung) | 20 % | 6,3 % ± 1,7 % (800 Spiele) |
| 6 | **4,2 %** (Näherung) | 16,7 % | 4,2 % ± 1,8 % (500 Spiele) |

Ab 4 Spielern ist Konter eine Näherung (`schocken/mehr.py`, `python werkzeuge/loese_mehr.py --spieler N`):
Jede Runde wird exakt entschieden, spätere Runden werden so bewertet, als spiele man dort selbst wie der
Stammtisch (im Finale exakter Konter). Zu dritt, wo es die exakte Lösung gibt, kommt die Näherung auf
14,4 % ± 1,3 %, also praktisch gleich gut wie exakt (14,0 %).

Was Konter zu zweit anders macht (Startspieler, Spielbeginn; `python werkzeuge/analyse_konter.py --spieler 2`):
- **Schock (1-1-x) im 1. oder 2. Wurf nicht stehen lassen**, sondern die Einsen halten und weiter auf
  Schock Aus gehen (bis +4 %-Pkt.). Die Gegner jagen ohnehin den Schock; ein kleiner Schock reicht selten.
- **Eine Eins nach dem 2. Wurf: Eins halten und nochmal offen würfeln**, statt aufzuhören (+0,2 bis 0,6 %-Pkt.
  je Lage). Verdecken bringt gegen Stammtisch-Spieler nichts, weil sie nicht auf andere reagieren.
- **Schwacher 1. Wurf ohne Eins (z. B. 6-5-3): stehen lassen**, statt alle neu zu würfeln. Dann haben
  die anderen nur einen Wurf.

Zu dritt (`python werkzeuge/analyse_konter.py --spieler 3`) gilt dasselbe Muster, teils noch stärker:
- Schock im 1. oder 2. Wurf: weiter auf Schock Aus (bis +2,4 %-Pkt.), auch als Zweiter.
- Eine Eins nach dem 2. Wurf: Eins halten und nochmal würfeln (bis +1,7 %-Pkt., z. B. bei 2-2-1, 3-2-1, 3-3-1).
- Schwacher 1. Wurf mit einer Sechs (6-5-2, 6-4-3 …): stehen lassen (bis +1 %-Pkt.).

**Spielt ihr am Stammtisch „idealerweise“?** Das hängt davon ab, wie die anderen spielen:
- Gegen Leute, die auf das Spielgeschehen reagieren (beste Annahme: alle spielen perfekt, siehe 2-Spieler-Lösung),
  ist „mit einer Eins nach dem 2. Wurf aufhören“ zu Spielbeginn richtig. Bei leerer Mitte ist es besser,
  die Eins zu halten und verdeckt nachzuwerfen.
- Gegen typische Stammtisch-Spieler, die nur den Schock jagen, ist **Weiterwürfeln** besser. Wer das
  ausnutzt, verliert zu dritt nur noch 14 % statt 33 % der Spiele.

## Drei Spieler: beste Faustregel (Simulation)

Suche über 1152 einfache Parameter-Strategien gegen zwei Faustregel-Spieler (je 50.000 Spiele,
Top 15 nachgemessen mit 2 Mio. Spielen; `python werkzeuge/parametersuche.py`).

- Faustregel gegen Faustregel: 33,3 % (fair).
- Beste gefundene Regel: **31,6 %**. Der Startspieler würfelt alle drei Würfe (außer bei Schock Aus).
  Die anderen hören erst auf, wenn ihr Wurf deutlich über dem schlechtesten offenen Wurf liegt.
  Sechsen werden immer gedreht.
- Schlechteste Regeln (ohne Drehen): 54,6–54,8 %.
- Pauschales Verdecken hilft in dieser einfachen Strategie-Familie nicht. Die exakte 2-Spieler-Lösung
  zeigt aber: Gezielt eingesetzt ist Verdecken sehr wertvoll.

Die 3-Spieler-Ergebnisse sind nur eine beste Antwort auf Faustregel-Gegner, keine exakte Lösung.
