# Abweichungen von der Basis-Strategie (zu zweit)

Basis = die optimale Entscheidung in der neutralen Lage (Hälfte 1, Spielbeginn, 0:0).
Gesucht sind Situationen, in denen der Spielstand eine andere Entscheidung verlangt.

- **Gewinn**: um so viele Prozentpunkte sinkt die eigene Wahrscheinlichkeit, das Spiel zu verlieren.
- **Wirkung**: Gewinn × Häufigkeit der Situation, in Prozentpunkten pro Spiel.
- **Regel**: von einem Entscheidungsbaum aus allen Spielständen gelernt; *Treffer* = Anteil der Fälle (gewichtet nach Häufigkeit), in denen die Regel die optimale Entscheidung trifft.
- **Vorsprung** = Deckel des Gegners − meine Deckel (positiv: ich liege vorn).
- **halte 11 VERDECKT** = diese Würfel liegen lassen, den Rest verdeckt werfen (stehen lassen).

Situationen mit Abweichung: 91917. Summe der Wirkung: **5.76 Prozentpunkte pro Spiel**: so viel weniger verliert man (näherungsweise), wenn man den Spielstand beachtet.

## Muster

| Rolle | Wurf | Basis | Besser | Situationen | Wirkung (%-Pkt./Spiel) |
|---|---|---|---|---|---|
| Startspieler | 2 | aufhören | weiter verdeckt | 3571 | 1.926 |
| Startspieler | 2 | weiter verdeckt | aufhören | 689 | 1.420 |
| Startspieler | 1 | aufhören | weiter offen | 1184 | 0.697 |
| Startspieler | 1 | weiter offen | aufhören | 541 | 0.592 |
| Folgespieler | 2 | weiter verdeckt | aufhören | 2625 | 0.511 |
| Folgespieler | 1 | weiter offen | aufhören | 40409 | 0.322 |
| Folgespieler | 1 | weiter offen | weiter offen | 34509 | 0.140 |
| Folgespieler | 2 | weiter verdeckt | weiter verdeckt | 3750 | 0.127 |
| Folgespieler | 2 | aufhören | weiter verdeckt | 432 | 0.008 |
| Startspieler | 1 | weiter offen | weiter offen | 20 | 0.007 |
| Folgespieler | 2 | aufhören | weiter offen | 900 | 0.006 |

## Die 30 wirkungsvollsten Situationen und wann man abweichen sollte

### 1. Startspieler, nach Wurf 2: **6-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.519 %-Pkt./Spiel, Gewinn bis 29.6 %-Pkt. Regel-Treffer 92 %.

- Mitte leer → **fertig** (stimmt in 100 %, 31 % der Fälle)
- Mitte ≥ 4, Vorsprung ≥ 1 → **fertig** (stimmt in 76 %, 14 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 4, Vorsprung ≤ 0 → **halte 11** (stimmt in 76 %, 4 % der Fälle)
- Mitte 1 bis 3, Vorsprung ≥ 1 → **halte 11** (stimmt in 76 %, 3 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≤ 3, Vorsprung ≤ 0 → halte 11 VERDECKT (stimmt in 94 %, 48 % der Fälle)

### 2. Startspieler, nach Wurf 2: **6-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.330 %-Pkt./Spiel, Gewinn bis 29.6 %-Pkt. Regel-Treffer 92 %.

- Mitte leer → **fertig** (stimmt in 100 %, 30 % der Fälle)
- Mitte ≥ 4, Vorsprung ≥ 1 → **fertig** (stimmt in 76 %, 14 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 4, Vorsprung ≤ 0 → **halte 11** (stimmt in 76 %, 4 % der Fälle)
- Mitte 1 bis 3, Vorsprung ≥ 1 → **halte 11** (stimmt in 78 %, 4 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≤ 3, Vorsprung ≤ 0 → halte 11 VERDECKT (stimmt in 94 %, 48 % der Fälle)

### 3. Startspieler, nach Wurf 1: **3-2-1** (3 davon neu geworfen)
Basis: *halte 1*. Wirkung 0.194 %-Pkt./Spiel, Gewinn bis 18.0 %-Pkt. Regel-Treffer 98 %.

- Mitte leer, meine Deckel ≥ 7 → **fertig** (stimmt in 100 %, 24 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 7, Gegner-Deckel ≤ 0 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- meine Deckel ≤ 6, Vorsprung ≥ 8 → **fertig** (stimmt in 100 %, 2 % der Fälle)
- Mitte ≥ 4, meine Deckel ≤ 6, Vorsprung ≤ 7 → halte 1 (stimmt in 100 %, 51 % der Fälle)
- Mitte ≤ 3, meine Deckel ≤ 6, Vorsprung ≤ 7 → halte 1 (stimmt in 87 %, 14 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 7, Gegner-Deckel ≥ 1 → halte 1 (stimmt in 93 %, 6 % der Fälle)

### 4. Startspieler, nach Wurf 1: **6-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.185 %-Pkt./Spiel, Gewinn bis 22.4 %-Pkt. Regel-Treffer 99 %.

- Mitte leer, Vorsprung ≥ -5 → **fertig** (stimmt in 100 %, 26 % der Fälle)
- Mitte nicht leer, Vorsprung ≤ 4 → halte 11 (stimmt in 100 %, 62 % der Fälle)
- Mitte leer, Vorsprung ≤ -6 → halte 11 (stimmt in 100 %, 9 % der Fälle)
- Mitte nicht leer, Vorsprung ≥ 5 → halte 11 (stimmt in 64 %, 3 % der Fälle)

### 5. Startspieler, nach Wurf 2: **5-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.167 %-Pkt./Spiel, Gewinn bis 19.7 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, meine Deckel ≤ 10 → **fertig** (stimmt in 100 %, 26 % der Fälle)
- Mitte 1 bis 3, Gegner-Deckel ≥ 4 → **halte 11** (stimmt in 89 %, 6 % der Fälle)
- Mitte ≥ 4, Vorsprung ≥ 4 → **fertig** (stimmt in 62 %, 3 % der Fälle)
- Mitte ≥ 4, Vorsprung ≤ 3 → halte 11 VERDECKT (stimmt in 100 %, 55 % der Fälle)
- Mitte leer, meine Deckel ≥ 11 → halte 11 VERDECKT (stimmt in 60 %, 5 % der Fälle)
- Mitte 1 bis 3, Gegner-Deckel ≤ 3 → halte 11 VERDECKT (stimmt in 84 %, 4 % der Fälle)

### 6. Startspieler, nach Wurf 2: **3-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.167 %-Pkt./Spiel, Gewinn bis 15.1 %-Pkt. Regel-Treffer 96 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte ≥ 2, Gegner-Deckel ≤ 0, Vorsprung ≤ -5 → **halte 1 VERDECKT** (stimmt in 100 %, 5 % der Fälle)
- Mitte ≥ 2, Gegner-Deckel ≥ 1, Vorsprung ≤ -5 → **halte 1 VERDECKT** (stimmt in 54 %, 5 % der Fälle)
- Mitte 1 → **halte 1 VERDECKT** (stimmt in 59 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung -4 bis 4 → fertig (stimmt in 100 %, 53 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 74 %, 3 % der Fälle)

### 7. Startspieler, nach Wurf 2: **4-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.150 %-Pkt./Spiel, Gewinn bis 14.9 %-Pkt. Regel-Treffer 98 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte nicht leer, Vorsprung ≤ -7 → **halte 1 VERDECKT** (stimmt in 100 %, 5 % der Fälle)
- Mitte nicht leer, Vorsprung -6 → **halte 1 VERDECKT** (stimmt in 77 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 6, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 58 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 7, Vorsprung ≥ -5 → fertig (stimmt in 70 %, 3 % der Fälle)

### 8. Startspieler, nach Wurf 2: **4-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.141 %-Pkt./Spiel, Gewinn bis 14.7 %-Pkt. Regel-Treffer 98 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 8, Hälfte 2 (Gegner verlor H1) oder Finale oder Hälfte 2 (ich verlor H1) → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 8, Hälfte 1 → **halte 1 VERDECKT** (stimmt in 100 %, 2 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 60 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≤ -6 → fertig (stimmt in 53 %, 3 % der Fälle)

### 9. Startspieler, nach Wurf 2: **6-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.136 %-Pkt./Spiel, Gewinn bis 29.6 %-Pkt. Regel-Treffer 100 %.

- immer → **fertig** (stimmt in 100 %, 100 % der Fälle)

### 10. Startspieler, nach Wurf 2: **5-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.123 %-Pkt./Spiel, Gewinn bis 13.9 %-Pkt. Regel-Treffer 97 %.

- Mitte leer, meine Deckel ≤ 7 → **halte 1 VERDECKT** (stimmt in 100 %, 14 % der Fälle)
- Mitte leer, meine Deckel ≥ 9 → **halte 1 VERDECKT** (stimmt in 100 %, 12 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 9 → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel 8 → **halte 1 VERDECKT** (stimmt in 74 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 60 % der Fälle)
- Mitte leer, meine Deckel 8 → fertig (stimmt in 100 %, 4 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≤ -6 → fertig (stimmt in 53 %, 3 % der Fälle)

### 11. Startspieler, nach Wurf 2: **5-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.117 %-Pkt./Spiel, Gewinn bis 13.4 %-Pkt. Regel-Treffer 97 %.

- Mitte leer, meine Deckel ≤ 7 → **halte 1 VERDECKT** (stimmt in 100 %, 14 % der Fälle)
- Mitte leer, meine Deckel ≥ 9 → **halte 1 VERDECKT** (stimmt in 100 %, 12 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 9 → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel 8 → **halte 1 VERDECKT** (stimmt in 74 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 60 % der Fälle)
- Mitte leer, meine Deckel 8 → fertig (stimmt in 100 %, 4 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≤ -6 → fertig (stimmt in 53 %, 3 % der Fälle)

### 12. Startspieler, nach Wurf 2: **5-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.106 %-Pkt./Spiel, Gewinn bis 12.2 %-Pkt. Regel-Treffer 97 %.

- Mitte leer, meine Deckel ≤ 7 → **halte 1 VERDECKT** (stimmt in 100 %, 14 % der Fälle)
- Mitte leer, meine Deckel ≥ 9 → **halte 1 VERDECKT** (stimmt in 100 %, 12 % der Fälle)
- Mitte 1 bis 4, Vorsprung ≤ -6 → **halte 1 VERDECKT** (stimmt in 100 %, 4 % der Fälle)
- Mitte nicht leer, Vorsprung -5 bis 4 → fertig (stimmt in 99 %, 58 % der Fälle)
- Mitte leer, meine Deckel 8 → fertig (stimmt in 100 %, 4 % der Fälle)
- Mitte ≥ 5, Vorsprung ≤ -6 → fertig (stimmt in 61 %, 4 % der Fälle)
- Mitte nicht leer, Vorsprung ≥ 5 → fertig (stimmt in 76 %, 3 % der Fälle)

### 13. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **6-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.090 %-Pkt./Spiel, Gewinn bis 27.1 %-Pkt. Regel-Treffer 98 %.

- Mitte leer → **fertig** (stimmt in 100 %, 78 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 0 → **fertig** (stimmt in 100 %, 7 % der Fälle)
- Mitte ≥ 4, meine Deckel ≥ 1 → **fertig** (stimmt in 51 %, 4 % der Fälle)
- Mitte 1 bis 3, meine Deckel ≥ 1 → halte 11 VERDECKT (stimmt in 100 %, 10 % der Fälle)

### 14. Startspieler, nach Wurf 2: **2-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.086 %-Pkt./Spiel, Gewinn bis 15.1 %-Pkt. Regel-Treffer 96 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte ≥ 2, Gegner-Deckel ≤ 0, Vorsprung ≤ -5 → **halte 1 VERDECKT** (stimmt in 100 %, 5 % der Fälle)
- Mitte ≥ 2, Gegner-Deckel ≥ 1, Vorsprung ≤ -5 → **halte 1 VERDECKT** (stimmt in 54 %, 5 % der Fälle)
- Mitte 1 → **halte 1 VERDECKT** (stimmt in 59 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung -4 bis 4 → fertig (stimmt in 100 %, 53 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 74 %, 3 % der Fälle)

### 15. Startspieler, nach Wurf 2: **6-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.086 %-Pkt./Spiel, Gewinn bis 9.0 %-Pkt. Regel-Treffer 93 %.

- meine Deckel ≥ 10 → **halte 1 VERDECKT** (stimmt in 100 %, 10 % der Fälle)
- meine Deckel ≤ 4, Gegner-Deckel ≥ 7 → **halte 1 VERDECKT** (stimmt in 56 %, 7 % der Fälle)
- meine Deckel 5 bis 9, Gegner-Deckel ≥ 7 → **halte 61 VERDECKT** (stimmt in 94 %, 6 % der Fälle)
- meine Deckel ≤ 9, Gegner-Deckel ≤ 6, Vorsprung ≥ -5 → fertig (stimmt in 98 %, 70 % der Fälle)
- meine Deckel ≤ 9, Gegner-Deckel ≤ 6, Vorsprung ≤ -6 → fertig (stimmt in 65 %, 6 % der Fälle)

### 16. Startspieler, nach Wurf 2: **3-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.080 %-Pkt./Spiel, Gewinn bis 15.1 %-Pkt. Regel-Treffer 97 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte ≥ 2, Vorsprung ≤ -7 → **halte 1 VERDECKT** (stimmt in 100 %, 4 % der Fälle)
- Mitte 1 → **halte 1 VERDECKT** (stimmt in 59 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung -6 → **halte 1 VERDECKT** (stimmt in 74 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung -5 bis 4 → fertig (stimmt in 99 %, 56 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 74 %, 3 % der Fälle)

### 17. Startspieler, nach Wurf 1: **3-2-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.079 %-Pkt./Spiel, Gewinn bis 16.8 %-Pkt. Regel-Treffer 98 %.

- Mitte ≤ 1, Vorsprung ≤ -6 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung 1 bis 7 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung ≥ 8 → **halte nichts** (stimmt in 97 %, 2 % der Fälle)
- Mitte ≥ 2, Vorsprung -7 bis 4 → fertig (stimmt in 100 %, 57 % der Fälle)
- Mitte ≤ 1, Vorsprung -5 bis 0 → fertig (stimmt in 95 %, 16 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 87 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung ≤ -8 → fertig (stimmt in 64 %, 2 % der Fälle)

### 18. Startspieler, nach Wurf 2: **6-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.077 %-Pkt./Spiel, Gewinn bis 8.3 %-Pkt. Regel-Treffer 93 %.

- meine Deckel ≥ 10 → **halte 1 VERDECKT** (stimmt in 100 %, 10 % der Fälle)
- meine Deckel ≤ 4, Gegner-Deckel ≥ 7 → **halte 1 VERDECKT** (stimmt in 56 %, 7 % der Fälle)
- meine Deckel 5 bis 9, Gegner-Deckel ≥ 7 → **halte 61 VERDECKT** (stimmt in 94 %, 6 % der Fälle)
- meine Deckel ≤ 9, Gegner-Deckel ≤ 6, Vorsprung ≥ -5 → fertig (stimmt in 98 %, 70 % der Fälle)
- meine Deckel ≤ 9, Gegner-Deckel ≤ 6, Vorsprung ≤ -6 → fertig (stimmt in 55 %, 6 % der Fälle)

### 19. Startspieler, nach Wurf 2: **5-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.075 %-Pkt./Spiel, Gewinn bis 19.7 %-Pkt. Regel-Treffer 98 %.

- Mitte leer, meine Deckel ≤ 10, Vorsprung ≥ -5 → **fertig** (stimmt in 100 %, 21 % der Fälle)
- Mitte 1 bis 3, Gegner-Deckel ≥ 4 → **halte 11** (stimmt in 90 %, 7 % der Fälle)
- Mitte leer, meine Deckel ≤ 10, Vorsprung ≤ -6 → **fertig** (stimmt in 100 %, 5 % der Fälle)
- Mitte ≥ 4, Vorsprung ≥ 4 → **fertig** (stimmt in 62 %, 3 % der Fälle)
- Mitte leer, meine Deckel ≥ 12 → **fertig** (stimmt in 100 %, 2 % der Fälle)
- Mitte ≥ 4, Vorsprung ≤ 3 → halte 11 VERDECKT (stimmt in 100 %, 56 % der Fälle)
- Mitte 1 bis 3, Gegner-Deckel ≤ 3 → halte 11 VERDECKT (stimmt in 84 %, 4 % der Fälle)
- Mitte leer, meine Deckel 11 → halte 11 VERDECKT (stimmt in 100 %, 3 % der Fälle)

### 20. Startspieler, nach Wurf 1: **3-3-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.073 %-Pkt./Spiel, Gewinn bis 15.9 %-Pkt. Regel-Treffer 98 %.

- Mitte ≤ 1, Vorsprung ≤ -6 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung 1 bis 7 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung ≥ 8 → **halte nichts** (stimmt in 97 %, 2 % der Fälle)
- Mitte ≥ 2, Vorsprung -7 bis 4 → fertig (stimmt in 100 %, 57 % der Fälle)
- Mitte ≤ 1, Vorsprung -5 bis 0 → fertig (stimmt in 95 %, 16 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 87 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung ≤ -8 → fertig (stimmt in 64 %, 2 % der Fälle)

### 21. Startspieler, nach Wurf 1: **5-3-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.069 %-Pkt./Spiel, Gewinn bis 8.6 %-Pkt. Regel-Treffer 99 %.

- Mitte leer, Gegner-Deckel ≥ 7 → **halte nichts** (stimmt in 100 %, 11 % der Fälle)
- meine Deckel ≥ 12, Gegner-Deckel ≤ 6 → **halte nichts** (stimmt in 100 %, 2 % der Fälle)
- meine Deckel ≤ 11, Gegner-Deckel ≤ 6, Vorsprung ≥ -7 → fertig (stimmt in 99 %, 78 % der Fälle)
- meine Deckel ≤ 11, Gegner-Deckel ≤ 6, Vorsprung ≤ -8 → fertig (stimmt in 86 %, 6 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 7 → fertig (stimmt in 100 %, 3 % der Fälle)

### 22. Startspieler, nach Wurf 2: **4-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.067 %-Pkt./Spiel, Gewinn bis 14.4 %-Pkt. Regel-Treffer 98 %.

- Mitte leer → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 8, Hälfte 2 (Gegner verlor H1) oder Finale oder Hälfte 2 (ich verlor H1) → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 8, Hälfte 1 → **halte 1 VERDECKT** (stimmt in 100 %, 2 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 60 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Vorsprung ≤ -6 → fertig (stimmt in 53 %, 3 % der Fälle)

### 23. Startspieler, nach Wurf 2: **6-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.065 %-Pkt./Spiel, Gewinn bis 6.5 %-Pkt. Regel-Treffer 93 %.

- meine Deckel ≤ 4, Gegner-Deckel ≥ 7 → **halte 1 VERDECKT** (stimmt in 56 %, 7 % der Fälle)
- meine Deckel 5 bis 10, Gegner-Deckel ≥ 7 → **halte 61 VERDECKT** (stimmt in 94 %, 6 % der Fälle)
- meine Deckel ≥ 11 → **halte 1 VERDECKT** (stimmt in 100 %, 5 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≥ -5 → fertig (stimmt in 99 %, 70 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≤ -6 → fertig (stimmt in 71 %, 11 % der Fälle)

### 24. Startspieler, nach Wurf 1: **4-2-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.065 %-Pkt./Spiel, Gewinn bis 14.5 %-Pkt. Regel-Treffer 98 %.

- Mitte ≤ 1, Vorsprung ≤ -6 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung 1 bis 7 → **halte nichts** (stimmt in 100 %, 10 % der Fälle)
- Mitte ≤ 1, Vorsprung ≥ 8 → **halte nichts** (stimmt in 97 %, 2 % der Fälle)
- Mitte ≥ 2, Vorsprung -7 bis 4 → fertig (stimmt in 100 %, 57 % der Fälle)
- Mitte ≤ 1, Vorsprung -5 bis 0 → fertig (stimmt in 95 %, 16 % der Fälle)
- Mitte ≥ 2, Vorsprung ≥ 5 → fertig (stimmt in 87 %, 3 % der Fälle)
- Mitte ≥ 2, Vorsprung ≤ -8 → fertig (stimmt in 64 %, 2 % der Fälle)

### 25. Startspieler, nach Wurf 2: **6-1-1** (3 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.061 %-Pkt./Spiel, Gewinn bis 29.6 %-Pkt. Regel-Treffer 100 %.

- Mitte leer → **fertig** (stimmt in 100 %, 90 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 8, Gegner-Deckel ≥ 2 → **halte 11** (stimmt in 100 %, 4 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 7, Gegner-Deckel ≥ 2 → **halte 11** (stimmt in 88 %, 3 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 100 %, 4 % der Fälle)

### 26. Startspieler, nach Wurf 1: **4-3-3** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.057 %-Pkt./Spiel, Gewinn bis 13.1 %-Pkt. Regel-Treffer 98 %.

- Mitte ≤ 1, meine Deckel ≥ 4, Gegner-Deckel ≥ 7 → **halte nichts** (stimmt in 100 %, 9 % der Fälle)
- meine Deckel ≥ 11, Gegner-Deckel ≤ 6 → **halte nichts** (stimmt in 100 %, 5 % der Fälle)
- Mitte ≤ 1, meine Deckel ≤ 3, Gegner-Deckel ≥ 7 → **halte nichts** (stimmt in 89 %, 3 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≥ -7 → fertig (stimmt in 99 %, 78 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≤ -8 → fertig (stimmt in 76 %, 2 % der Fälle)
- Mitte ≥ 2, Gegner-Deckel ≥ 7 → fertig (stimmt in 100 %, 2 % der Fälle)

### 27. Startspieler, nach Wurf 1: **5-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.056 %-Pkt./Spiel, Gewinn bis 14.3 %-Pkt. Regel-Treffer 98 %.

- meine Deckel ≥ 4, Gegner-Deckel ≥ 8 → **fertig** (stimmt in 94 %, 4 % der Fälle)
- meine Deckel ≤ 3, Gegner-Deckel ≥ 8, Vorsprung ≤ 7 → **fertig** (stimmt in 56 %, 2 % der Fälle)
- meine Deckel ≤ 3, Gegner-Deckel ≥ 8, Vorsprung ≥ 8 → **fertig** (stimmt in 82 %, 2 % der Fälle)
- Gegner-Deckel ≤ 7, Hälfte 2 (Gegner verlor H1) oder Finale oder Hälfte 2 (ich verlor H1) → halte 11 (stimmt in 100 %, 55 % der Fälle)
- Gegner-Deckel ≤ 7, Hälfte 1 → halte 11 (stimmt in 100 %, 36 % der Fälle)

### 28. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **6-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.054 %-Pkt./Spiel, Gewinn bis 27.1 %-Pkt. Regel-Treffer 98 %.

- Mitte leer → **fertig** (stimmt in 100 %, 77 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 0 → **fertig** (stimmt in 100 %, 7 % der Fälle)
- Mitte ≥ 4, meine Deckel ≥ 1 → **fertig** (stimmt in 51 %, 5 % der Fälle)
- Mitte 1 bis 3, meine Deckel ≥ 1 → halte 11 VERDECKT (stimmt in 100 %, 11 % der Fälle)

### 29. Startspieler, nach Wurf 1: **4-4-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.053 %-Pkt./Spiel, Gewinn bis 12.2 %-Pkt. Regel-Treffer 98 %.

- Mitte leer, Gegner-Deckel ≥ 7 → **halte nichts** (stimmt in 100 %, 11 % der Fälle)
- meine Deckel ≥ 11, Gegner-Deckel ≤ 6 → **halte nichts** (stimmt in 100 %, 5 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≥ -7 → fertig (stimmt in 99 %, 78 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 7 → fertig (stimmt in 89 %, 3 % der Fälle)
- meine Deckel ≤ 10, Gegner-Deckel ≤ 6, Vorsprung ≤ -8 → fertig (stimmt in 76 %, 2 % der Fälle)

### 30. Startspieler, nach Wurf 1: **5-4-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.052 %-Pkt./Spiel, Gewinn bis 6.3 %-Pkt. Regel-Treffer 98 %.

- Mitte leer, Gegner-Deckel ≥ 7, Vorsprung ≤ 6 → **halte nichts** (stimmt in 100 %, 8 % der Fälle)
- Mitte leer, Gegner-Deckel ≥ 7, Vorsprung ≥ 7 → **halte nichts** (stimmt in 77 %, 3 % der Fälle)
- meine Deckel ≥ 12, Gegner-Deckel ≤ 6 → **halte nichts** (stimmt in 100 %, 2 % der Fälle)
- meine Deckel ≤ 11, Gegner-Deckel ≤ 6, Vorsprung ≥ -5 → fertig (stimmt in 100 %, 69 % der Fälle)
- meine Deckel ≤ 11, Gegner-Deckel ≤ 6, Vorsprung ≤ -6 → fertig (stimmt in 94 %, 14 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 7 → fertig (stimmt in 100 %, 3 % der Fälle)

