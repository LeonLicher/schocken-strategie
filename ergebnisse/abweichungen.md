# Abweichungen von der Basis-Strategie (zu zweit)

Basis = die optimale Entscheidung in der neutralen Lage (Hälfte 1, Spielbeginn, 0:0).
Gesucht sind Situationen, in denen der Spielstand eine andere Entscheidung verlangt.

- **Gewinn**: um so viele Prozentpunkte sinkt die eigene Wahrscheinlichkeit, das Spiel zu verlieren.
- **Wirkung**: Gewinn × Häufigkeit der Situation, in Prozentpunkten pro Spiel.
- **Regel**: von einem Entscheidungsbaum aus allen Spielständen gelernt; *Treffer* = Anteil der Fälle (gewichtet nach Häufigkeit), in denen die Regel die optimale Entscheidung trifft.
- **Vorsprung** = Deckel des Gegners − meine Deckel (positiv: ich liege vorn).
- **halte 11 VERDECKT** = diese Würfel liegen lassen, den Rest verdeckt werfen (stehen lassen).

Situationen mit Abweichung: 89899. Summe der Wirkung: **3.71 Prozentpunkte pro Spiel**: so viel weniger verliert man (näherungsweise), wenn man den Spielstand beachtet.

## Muster

| Rolle | Wurf | Basis | Besser | Situationen | Wirkung (%-Pkt./Spiel) |
|---|---|---|---|---|---|
| Startspieler | 2 | aufhören | weiter verdeckt | 5423 | 1.449 |
| Folgespieler | 2 | weiter verdeckt | aufhören | 2670 | 0.523 |
| Startspieler | 1 | weiter offen | aufhören | 704 | 0.499 |
| Startspieler | 2 | weiter verdeckt | aufhören | 912 | 0.477 |
| Startspieler | 1 | aufhören | weiter offen | 1451 | 0.340 |
| Folgespieler | 1 | weiter offen | aufhören | 27701 | 0.198 |
| Startspieler | 2 | aufhören | weiter offen | 240 | 0.077 |
| Folgespieler | 2 | weiter verdeckt | weiter verdeckt | 2420 | 0.073 |
| Folgespieler | 1 | weiter offen | weiter offen | 32463 | 0.030 |
| Folgespieler | 2 | aufhören | weiter offen | 2070 | 0.019 |
| Startspieler | 1 | aufhören | weiter verdeckt | 25 | 0.006 |
| Folgespieler | 1 | aufhören | weiter offen | 11100 | 0.006 |
| Folgespieler | 1 | weiter verdeckt | weiter verdeckt | 155 | 0.006 |
| Folgespieler | 1 | weiter verdeckt | aufhören | 45 | 0.003 |
| Folgespieler | 2 | aufhören | weiter verdeckt | 290 | 0.002 |
| Folgespieler | 2 | weiter offen | weiter offen | 2185 | 0.002 |
| Startspieler | 1 | weiter offen | weiter verdeckt | 45 | 0.002 |

## Die 30 wirkungsvollsten Situationen und wann man abweichen sollte

### 1. Startspieler, nach Wurf 2: **5-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.230 %-Pkt./Spiel, Gewinn bis 18.5 %-Pkt. Regel-Treffer 95 %.

- Mitte leer, Vorsprung ≥ -5 → **fertig** (stimmt in 100 %, 23 % der Fälle)
- Mitte ≥ 4, Vorsprung ≥ 2 → **fertig** (stimmt in 86 %, 9 % der Fälle)
- Mitte 1 bis 2, Vorsprung ≤ 1 → **halte 11** (stimmt in 85 %, 5 % der Fälle)
- Mitte leer, Vorsprung ≤ -8 → **fertig** (stimmt in 58 %, 4 % der Fälle)
- Mitte leer, Vorsprung -7 bis -6 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- Mitte 1 bis 3, Vorsprung ≥ 2 → **halte 11** (stimmt in 77 %, 3 % der Fälle)
- Mitte ≥ 3, Vorsprung ≤ 1 → halte 11 VERDECKT (stimmt in 99 %, 53 % der Fälle)

### 2. Startspieler, nach Wurf 1: **6-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.190 %-Pkt./Spiel, Gewinn bis 21.2 %-Pkt. Regel-Treffer 98 %.

- Mitte leer, meine Deckel ≤ 10 → **fertig** (stimmt in 100 %, 27 % der Fälle)
- Mitte ≥ 6, Vorsprung ≥ 3 → **fertig** (stimmt in 89 %, 4 % der Fälle)
- Mitte leer, meine Deckel ≥ 11 → **fertig** (stimmt in 58 %, 4 % der Fälle)
- Mitte nicht leer, Vorsprung ≤ 2 → halte 11 (stimmt in 100 %, 61 % der Fälle)
- Mitte 1 bis 5, Vorsprung ≥ 3 → halte 11 (stimmt in 94 %, 5 % der Fälle)

### 3. Startspieler, nach Wurf 2: **4-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.142 %-Pkt./Spiel, Gewinn bis 12.6 %-Pkt. Regel-Treffer 92 %.

- meine Deckel ≥ 2, Gegner-Deckel ≤ 2, Vorsprung ≤ -2 → **halte 1 VERDECKT** (stimmt in 100 %, 26 % der Fälle)
- Mitte leer, meine Deckel ≥ 2, Vorsprung ≥ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 16 % der Fälle)
- meine Deckel ≥ 2, Gegner-Deckel ≥ 3, Vorsprung ≤ -2 → **halte 1 VERDECKT** (stimmt in 92 %, 14 % der Fälle)
- meine Deckel ≤ 0, Vorsprung ≥ 1 → **halte 1 VERDECKT** (stimmt in 100 %, 7 % der Fälle)
- meine Deckel ≤ 1, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 20 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 2, Vorsprung ≥ -1 → fertig (stimmt in 55 %, 14 % der Fälle)
- meine Deckel 1, Vorsprung ≥ 1 → fertig (stimmt in 100 %, 4 % der Fälle)

### 4. Startspieler, nach Wurf 2: **4-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.136 %-Pkt./Spiel, Gewinn bis 12.4 %-Pkt. Regel-Treffer 97 %.

- Mitte nicht leer, meine Deckel ≥ 2, Gegner-Deckel ≤ 5 → **halte 1 VERDECKT** (stimmt in 92 %, 35 % der Fälle)
- Mitte leer, meine Deckel ≥ 2 → **halte 1 VERDECKT** (stimmt in 100 %, 30 % der Fälle)
- meine Deckel ≤ 0, Vorsprung ≥ 1 → **halte 1 VERDECKT** (stimmt in 100 %, 7 % der Fälle)
- meine Deckel ≤ 1, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 20 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 2, Gegner-Deckel ≥ 6 → fertig (stimmt in 100 %, 5 % der Fälle)
- meine Deckel 1, Vorsprung ≥ 1 → fertig (stimmt in 100 %, 4 % der Fälle)

### 5. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **6-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.132 %-Pkt./Spiel, Gewinn bis 25.4 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 100 %, 47 % der Fälle)
- Mitte ≥ 5, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 93 %, 31 % der Fälle)
- Mitte 1 bis 4, Gegner-Deckel ≥ 2 → halte 11 VERDECKT (stimmt in 86 %, 13 % der Fälle)
- Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 100 %, 10 % der Fälle)

### 6. Startspieler, nach Wurf 2: **5-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.124 %-Pkt./Spiel, Gewinn bis 11.9 %-Pkt. Regel-Treffer 96 %.

- meine Deckel ≥ 2, Vorsprung ≤ -2 → **halte 1 VERDECKT** (stimmt in 97 %, 40 % der Fälle)
- meine Deckel ≥ 2, Vorsprung -1 bis 1 → **halte 1 VERDECKT** (stimmt in 83 %, 15 % der Fälle)
- Mitte leer, meine Deckel ≥ 2, Vorsprung ≥ 2 → **halte 1 VERDECKT** (stimmt in 100 %, 9 % der Fälle)
- meine Deckel ≤ 0, Vorsprung ≥ 2 → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- meine Deckel ≤ 1, Vorsprung ≤ 1 → fertig (stimmt in 100 %, 24 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 2, Vorsprung ≥ 2 → fertig (stimmt in 93 %, 5 % der Fälle)
- meine Deckel 1, Vorsprung ≥ 2 → fertig (stimmt in 100 %, 3 % der Fälle)

### 7. Startspieler, nach Wurf 2: **5-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.118 %-Pkt./Spiel, Gewinn bis 11.6 %-Pkt. Regel-Treffer 91 %.

- Mitte ≤ 10, Gegner-Deckel ≤ 3, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 31 % der Fälle)
- Mitte ≤ 10, Gegner-Deckel ≥ 4, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 87 %, 13 % der Fälle)
- Mitte leer, Vorsprung ≥ 0 → **halte 1 VERDECKT** (stimmt in 100 %, 13 % der Fälle)
- Mitte ≥ 11, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 23 % der Fälle)
- Mitte 1 bis 10, Vorsprung ≥ 0 → fertig (stimmt in 61 %, 16 % der Fälle)
- Mitte ≥ 11, Vorsprung ≥ 1 → fertig (stimmt in 73 %, 5 % der Fälle)

### 8. Startspieler, nach Wurf 2: **5-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.110 %-Pkt./Spiel, Gewinn bis 10.8 %-Pkt. Regel-Treffer 90 %.

- Mitte ≤ 10, Gegner-Deckel ≤ 2, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 25 % der Fälle)
- Mitte ≤ 10, Gegner-Deckel ≥ 3, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 89 %, 19 % der Fälle)
- Mitte leer, Vorsprung ≥ 0 → **halte 1 VERDECKT** (stimmt in 100 %, 13 % der Fälle)
- Mitte ≥ 11, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 23 % der Fälle)
- Mitte 1 bis 10, Vorsprung ≥ 0 → fertig (stimmt in 61 %, 16 % der Fälle)
- Mitte ≥ 11, Vorsprung ≥ 1 → fertig (stimmt in 73 %, 5 % der Fälle)

### 9. Startspieler, nach Wurf 2: **5-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.101 %-Pkt./Spiel, Gewinn bis 18.5 %-Pkt. Regel-Treffer 91 %.

- Mitte leer, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 100 %, 22 % der Fälle)
- Mitte 1 bis 2, Gegner-Deckel ≥ 2 → **halte 11** (stimmt in 99 %, 7 % der Fälle)
- Mitte ≥ 3, Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 100 %, 45 % der Fälle)
- Mitte ≥ 3, Gegner-Deckel ≥ 2 → halte 11 VERDECKT (stimmt in 61 %, 23 % der Fälle)
- Mitte ≤ 2, Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 89 %, 3 % der Fälle)

### 10. Startspieler, nach Wurf 1: **3-2-1** (3 davon neu geworfen)
Basis: *halte 1*. Wirkung 0.096 %-Pkt./Spiel, Gewinn bis 16.5 %-Pkt. Regel-Treffer 97 %.

- Mitte nicht leer, Gegner-Deckel 5 bis 6 → **fertig** (stimmt in 86 %, 7 % der Fälle)
- meine Deckel ≤ 3, Gegner-Deckel ≥ 7 → **fertig** (stimmt in 96 %, 7 % der Fälle)
- Mitte leer, Gegner-Deckel 5 bis 6 → **fertig** (stimmt in 100 %, 7 % der Fälle)
- Gegner-Deckel ≤ 0, Vorsprung ≤ -8 → **fertig** (stimmt in 57 %, 2 % der Fälle)
- Gegner-Deckel ≤ 4, Vorsprung -7 bis 1 → halte 1 (stimmt in 100 %, 58 % der Fälle)
- meine Deckel ≥ 4, Gegner-Deckel ≥ 7 → halte 1 (stimmt in 96 %, 10 % der Fälle)
- Gegner-Deckel 1 bis 4, Vorsprung ≤ -8 → halte 1 (stimmt in 100 %, 5 % der Fälle)
- Gegner-Deckel ≤ 4, Vorsprung ≥ 2 → halte 1 (stimmt in 91 %, 4 % der Fälle)

### 11. Startspieler, nach Wurf 2: **6-2-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.095 %-Pkt./Spiel, Gewinn bis 8.8 %-Pkt. Regel-Treffer 86 %.

- Mitte 1 bis 10, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 84 %, 26 % der Fälle)
- Mitte leer, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 17 % der Fälle)
- Mitte leer, Vorsprung ≥ 0 → **halte 1 VERDECKT** (stimmt in 72 %, 13 % der Fälle)
- Mitte ≥ 11, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 23 % der Fälle)
- Mitte 1 bis 10, Vorsprung ≥ 0 → fertig (stimmt in 72 %, 16 % der Fälle)
- Mitte ≥ 11, Vorsprung ≥ 1 → fertig (stimmt in 73 %, 5 % der Fälle)

### 12. Startspieler, nach Wurf 2: **6-1-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.092 %-Pkt./Spiel, Gewinn bis 12.1 %-Pkt. Regel-Treffer 93 %.

- Mitte 3 bis 6 → **halte 11 VERDECKT** (stimmt in 62 %, 16 % der Fälle)
- Mitte 1 bis 2 → **halte 11** (stimmt in 88 %, 7 % der Fälle)
- Mitte ≥ 7 → fertig (stimmt in 100 %, 47 % der Fälle)
- Mitte leer → fertig (stimmt in 100 %, 30 % der Fälle)

### 13. Startspieler, nach Wurf 2: **6-3-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.087 %-Pkt./Spiel, Gewinn bis 8.3 %-Pkt. Regel-Treffer 86 %.

- Mitte 1 bis 10, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 84 %, 26 % der Fälle)
- Mitte leer, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 17 % der Fälle)
- Mitte leer, Vorsprung ≥ 0 → **halte 1 VERDECKT** (stimmt in 72 %, 13 % der Fälle)
- Mitte ≥ 11, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 23 % der Fälle)
- Mitte 1 bis 10, Vorsprung ≥ 0 → fertig (stimmt in 72 %, 16 % der Fälle)
- Mitte ≥ 11, Vorsprung ≥ 1 → fertig (stimmt in 73 %, 5 % der Fälle)

### 14. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **6-1-1** (1 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.076 %-Pkt./Spiel, Gewinn bis 25.4 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 100 %, 43 % der Fälle)
- Mitte ≥ 5, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 93 %, 32 % der Fälle)
- Mitte 1 bis 4, Gegner-Deckel ≥ 2 → halte 11 VERDECKT (stimmt in 87 %, 14 % der Fälle)
- Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 100 %, 10 % der Fälle)

### 15. Startspieler, nach Wurf 2: **6-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.076 %-Pkt./Spiel, Gewinn bis 7.2 %-Pkt. Regel-Treffer 85 %.

- Mitte ≤ 9, meine Deckel ≥ 3, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 90 %, 40 % der Fälle)
- Mitte ≤ 9, meine Deckel ≥ 3, Vorsprung ≥ 0 → **halte 1 VERDECKT** (stimmt in 51 %, 18 % der Fälle)
- Mitte ≤ 10, meine Deckel 2 → **halte 1 VERDECKT** (stimmt in 58 %, 7 % der Fälle)
- meine Deckel ≤ 1 → fertig (stimmt in 100 %, 30 % der Fälle)
- Mitte ≥ 11, meine Deckel 2 → fertig (stimmt in 100 %, 3 % der Fälle)
- Mitte ≥ 10, meine Deckel ≥ 3 → fertig (stimmt in 100 %, 2 % der Fälle)

### 16. Startspieler, nach Wurf 1: **5-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.071 %-Pkt./Spiel, Gewinn bis 13.9 %-Pkt. Regel-Treffer 99 %.

- Mitte leer, Gegner-Deckel ≥ 8 → **fertig** (stimmt in 100 %, 10 % der Fälle)
- Gegner-Deckel 6 bis 7, Vorsprung ≤ -1 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- Gegner-Deckel ≤ 5, Vorsprung ≥ -10 → halte 11 (stimmt in 100 %, 73 % der Fälle)
- Gegner-Deckel 6 bis 7, Vorsprung ≥ 0 → halte 11 (stimmt in 88 %, 10 % der Fälle)
- Gegner-Deckel ≤ 5, Vorsprung ≤ -11 → halte 11 (stimmt in 100 %, 2 % der Fälle)
- Mitte nicht leer, Gegner-Deckel ≥ 8 → halte 11 (stimmt in 100 %, 2 % der Fälle)

### 17. Startspieler, nach Wurf 2: **4-4-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.066 %-Pkt./Spiel, Gewinn bis 12.2 %-Pkt. Regel-Treffer 92 %.

- meine Deckel ≥ 2, Gegner-Deckel ≤ 2, Vorsprung ≤ -2 → **halte 1 VERDECKT** (stimmt in 100 %, 26 % der Fälle)
- Mitte leer, meine Deckel ≥ 2, Vorsprung ≥ -1 → **halte 1 VERDECKT** (stimmt in 100 %, 16 % der Fälle)
- meine Deckel ≥ 2, Gegner-Deckel ≥ 3, Vorsprung ≤ -2 → **halte 1 VERDECKT** (stimmt in 92 %, 14 % der Fälle)
- meine Deckel ≤ 0, Vorsprung ≥ 2 → **halte 1 VERDECKT** (stimmt in 100 %, 3 % der Fälle)
- meine Deckel ≤ 1, Vorsprung ≤ 1 → fertig (stimmt in 100 %, 24 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 2, Vorsprung ≥ -1 → fertig (stimmt in 51 %, 14 % der Fälle)
- meine Deckel 1, Vorsprung ≥ 2 → fertig (stimmt in 100 %, 3 % der Fälle)

### 18. Startspieler, nach Wurf 2: **6-1-1** (1 davon neu geworfen)
Basis: *fertig*. Wirkung 0.064 %-Pkt./Spiel, Gewinn bis 12.1 %-Pkt. Regel-Treffer 92 %.

- Mitte 3 bis 6 → **halte 11 VERDECKT** (stimmt in 63 %, 18 % der Fälle)
- Mitte 1 bis 2 → **halte 11** (stimmt in 88 %, 8 % der Fälle)
- Mitte ≥ 7 → fertig (stimmt in 100 %, 50 % der Fälle)
- Mitte leer → fertig (stimmt in 100 %, 24 % der Fälle)

### 19. Startspieler, nach Wurf 2: **4-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.062 %-Pkt./Spiel, Gewinn bis 11.9 %-Pkt. Regel-Treffer 95 %.

- Mitte 1 bis 3, Gegner-Deckel ≤ 8 → **halte 11** (stimmt in 63 %, 10 % der Fälle)
- Gegner-Deckel ≥ 9, Vorsprung ≥ 6 → **fertig** (stimmt in 92 %, 4 % der Fälle)
- Gegner-Deckel ≥ 9, Vorsprung ≤ 5 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- Mitte ≥ 4, Gegner-Deckel ≤ 8, Vorsprung ≤ 4 → halte 11 VERDECKT (stimmt in 100 %, 57 % der Fälle)
- Mitte leer, Gegner-Deckel ≤ 8 → halte 11 VERDECKT (stimmt in 100 %, 24 % der Fälle)
- Mitte ≥ 4, Gegner-Deckel ≤ 8, Vorsprung ≥ 5 → halte 11 VERDECKT (stimmt in 78 %, 2 % der Fälle)

### 20. Startspieler, nach Wurf 2: **6-5-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.062 %-Pkt./Spiel, Gewinn bis 5.0 %-Pkt. Regel-Treffer 81 %.

- meine Deckel ≥ 2, Gegner-Deckel ≥ 1, Vorsprung ≥ -3 → **halte 1 VERDECKT** (stimmt in 58 %, 39 % der Fälle)
- meine Deckel ≥ 2, Gegner-Deckel ≥ 1, Vorsprung ≤ -4 → **halte 1 VERDECKT** (stimmt in 98 %, 18 % der Fälle)
- meine Deckel ≥ 2, Gegner-Deckel ≤ 0, Vorsprung ≤ -4 → **halte 1 VERDECKT** (stimmt in 65 %, 7 % der Fälle)
- meine Deckel ≤ 1 → fertig (stimmt in 100 %, 30 % der Fälle)
- meine Deckel ≥ 2, Gegner-Deckel ≤ 0, Vorsprung ≥ -3 → fertig (stimmt in 100 %, 5 % der Fälle)

### 21. Startspieler, nach Wurf 2: **5-5-1** (2 davon neu geworfen)
Basis: *fertig*. Wirkung 0.051 %-Pkt./Spiel, Gewinn bis 9.9 %-Pkt. Regel-Treffer 93 %.

- Mitte ≤ 10, Vorsprung ≤ -1 → **halte 1 VERDECKT** (stimmt in 95 %, 44 % der Fälle)
- Mitte ≤ 10, Vorsprung 0 bis 1 → **halte 1 VERDECKT** (stimmt in 78 %, 10 % der Fälle)
- Mitte leer, Vorsprung ≥ 2 → **halte 1 VERDECKT** (stimmt in 100 %, 9 % der Fälle)
- Mitte ≥ 11, Vorsprung ≤ 0 → fertig (stimmt in 100 %, 23 % der Fälle)
- Mitte 1 bis 10, Vorsprung ≥ 2 → fertig (stimmt in 80 %, 10 % der Fälle)
- Mitte ≥ 11, Vorsprung ≥ 1 → fertig (stimmt in 73 %, 5 % der Fälle)

### 22. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **5-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.048 %-Pkt./Spiel, Gewinn bis 15.4 %-Pkt. Regel-Treffer 99 %.

- Mitte leer → **fertig** (stimmt in 100 %, 47 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 0, Vorsprung ≥ 6 → **fertig** (stimmt in 100 %, 5 % der Fälle)
- Mitte nicht leer, Vorsprung -2 bis 5 → halte 11 VERDECKT (stimmt in 100 %, 38 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 1, Vorsprung ≥ 6 → halte 11 VERDECKT (stimmt in 85 %, 6 % der Fälle)
- Mitte nicht leer, Vorsprung ≤ -3 → halte 11 VERDECKT (stimmt in 100 %, 3 % der Fälle)

### 23. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 2: **6-1-1** (3 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.044 %-Pkt./Spiel, Gewinn bis 25.4 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 100 %, 47 % der Fälle)
- Mitte ≥ 5, Gegner-Deckel ≥ 2 → **fertig** (stimmt in 93 %, 31 % der Fälle)
- Mitte 1 bis 4, Gegner-Deckel ≥ 2 → halte 11 VERDECKT (stimmt in 87 %, 12 % der Fälle)
- Gegner-Deckel ≤ 1 → halte 11 VERDECKT (stimmt in 100 %, 10 % der Fälle)

### 24. Startspieler, nach Wurf 1: **3-2-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.043 %-Pkt./Spiel, Gewinn bis 13.4 %-Pkt. Regel-Treffer 94 %.

- Mitte leer, meine Deckel ≥ 3 → **halte nichts** (stimmt in 100 %, 28 % der Fälle)
- Mitte 1 bis 3, Vorsprung ≤ 1 → **halte nichts** (stimmt in 74 %, 8 % der Fälle)
- Mitte ≥ 4, meine Deckel 6 → **halte nichts** (stimmt in 56 %, 3 % der Fälle)
- Mitte leer, meine Deckel ≤ 2 → **halte nichts** (stimmt in 60 %, 3 % der Fälle)
- Mitte ≥ 4, meine Deckel ≤ 5, Vorsprung ≤ 4 → fertig (stimmt in 100 %, 48 % der Fälle)
- Mitte ≥ 4, meine Deckel ≥ 7 → fertig (stimmt in 87 %, 4 % der Fälle)
- Mitte 1 bis 3, Vorsprung ≥ 2 → fertig (stimmt in 100 %, 4 % der Fälle)
- Mitte ≥ 4, meine Deckel ≤ 5, Vorsprung ≥ 5 → fertig (stimmt in 68 %, 3 % der Fälle)

### 25. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 11), nach Wurf 2: **5-1-1** (2 davon neu geworfen)
Basis: *halte 11 VERDECKT*. Wirkung 0.042 %-Pkt./Spiel, Gewinn bis 17.0 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, Gegner-Deckel ≥ 5 → **fertig** (stimmt in 100 %, 22 % der Fälle)
- Mitte ≥ 5, Gegner-Deckel ≥ 5 → **fertig** (stimmt in 100 %, 11 % der Fälle)
- Mitte ≤ 9, Gegner-Deckel ≤ 4, Vorsprung ≥ 3 → **fertig** (stimmt in 65 %, 3 % der Fälle)
- Mitte ≥ 10, Gegner-Deckel ≤ 4, Vorsprung ≥ 3 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- meine Deckel ≥ 9, Gegner-Deckel ≤ 4, Vorsprung ≤ 2 → **fertig** (stimmt in 100 %, 2 % der Fälle)
- meine Deckel ≤ 8, Gegner-Deckel ≤ 4, Vorsprung ≤ 2 → halte 11 VERDECKT (stimmt in 100 %, 51 % der Fälle)
- Mitte 1 bis 4, Gegner-Deckel ≥ 5 → halte 11 VERDECKT (stimmt in 67 %, 9 % der Fälle)

### 26. Startspieler, nach Wurf 1: **3-3-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.039 %-Pkt./Spiel, Gewinn bis 12.8 %-Pkt. Regel-Treffer 94 %.

- Mitte leer, Vorsprung ≤ 8 → **halte nichts** (stimmt in 100 %, 28 % der Fälle)
- Mitte 1 bis 3, meine Deckel ≥ 6 → **halte nichts** (stimmt in 71 %, 7 % der Fälle)
- Mitte leer, Vorsprung ≥ 9 → **halte nichts** (stimmt in 60 %, 3 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 5, Vorsprung ≤ 5 → fertig (stimmt in 99 %, 53 % der Fälle)
- Mitte ≥ 4, meine Deckel ≥ 6 → fertig (stimmt in 75 %, 7 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 5, Vorsprung ≥ 6 → fertig (stimmt in 67 %, 3 % der Fälle)

### 27. Startspieler, nach Wurf 1: **4-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.033 %-Pkt./Spiel, Gewinn bis 8.7 %-Pkt. Regel-Treffer 99 %.

- Gegner-Deckel 9 bis 10, Vorsprung ≥ 6 → **fertig** (stimmt in 70 %, 3 % der Fälle)
- Gegner-Deckel ≥ 11, Vorsprung ≥ 6 → **fertig** (stimmt in 97 %, 3 % der Fälle)
- Gegner-Deckel ≥ 9, Vorsprung ≤ 5 → **fertig** (stimmt in 100 %, 3 % der Fälle)
- Gegner-Deckel ≤ 8 → halte 11 (stimmt in 100 %, 92 % der Fälle)

### 28. Folgespieler, Gegner verdeckt nach 3 (sichtbar: 1), nach Wurf 1: **6-1-1** (3 davon neu geworfen)
Basis: *halte 11*. Wirkung 0.033 %-Pkt./Spiel, Gewinn bis 16.4 %-Pkt. Regel-Treffer 100 %.

- Mitte leer, meine Deckel ≤ 9 → **fertig** (stimmt in 100 %, 43 % der Fälle)
- Mitte nicht leer, meine Deckel ≤ 0, Vorsprung ≥ 5 → **fertig** (stimmt in 100 %, 7 % der Fälle)
- Mitte nicht leer, Vorsprung ≤ 4 → halte 11 (stimmt in 100 %, 36 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 1, Vorsprung ≥ 5 → halte 11 (stimmt in 100 %, 8 % der Fälle)
- Mitte leer, meine Deckel ≥ 10 → halte 11 (stimmt in 100 %, 6 % der Fälle)

### 29. Startspieler, nach Wurf 1: **4-2-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.033 %-Pkt./Spiel, Gewinn bis 12.0 %-Pkt. Regel-Treffer 96 %.

- Mitte leer, Vorsprung ≤ 8 → **halte nichts** (stimmt in 100 %, 28 % der Fälle)
- Mitte nicht leer, meine Deckel ≥ 9 → **halte nichts** (stimmt in 75 %, 3 % der Fälle)
- Mitte leer, Vorsprung ≥ 9 → **halte nichts** (stimmt in 60 %, 3 % der Fälle)
- Mitte ≥ 4, meine Deckel ≤ 8 → fertig (stimmt in 100 %, 58 % der Fälle)
- Mitte 1 bis 3, meine Deckel ≤ 8 → fertig (stimmt in 80 %, 8 % der Fälle)

### 30. Startspieler, nach Wurf 1: **5-3-2** (3 davon neu geworfen)
Basis: *fertig*. Wirkung 0.030 %-Pkt./Spiel, Gewinn bis 8.2 %-Pkt. Regel-Treffer 98 %.

- meine Deckel 5 bis 9, Gegner-Deckel ≥ 7 → **halte nichts** (stimmt in 94 %, 7 % der Fälle)
- meine Deckel ≥ 10, Vorsprung ≥ -9 → **halte nichts** (stimmt in 100 %, 6 % der Fälle)
- meine Deckel ≥ 10, Vorsprung ≤ -10 → **halte nichts** (stimmt in 87 %, 3 % der Fälle)
- meine Deckel ≤ 9, Gegner-Deckel ≤ 6 → fertig (stimmt in 100 %, 74 % der Fälle)
- meine Deckel ≤ 4, Gegner-Deckel ≥ 7 → fertig (stimmt in 85 %, 10 % der Fälle)

