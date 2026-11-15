# Schocken – Hausregeln (Stand 2026-11-15)

## Material & Struktur
- 3 Würfel pro Spieler, 13 Deckel in der Mitte.
- Ein Spiel = 2 Hälften. Verliert ein Spieler beide Hälften → er hat das Spiel verloren.
  Sonst Finale zwischen den beiden Hälften-Verlierern, gespielt wie eine normale Hälfte (13 Deckel).
- Eine Hälfte endet, wenn ein Spieler alle 13 Deckel hat.

## Ablauf einer Runde
- Startspieler = Verlierer der letzten Runde (Spielstart: auswürfeln).
- **Ist die Mitte leer, beginnt der Spieler mit den meisten Deckeln.** Bei Gleichstand (erst ab 3 Spielern
  möglich) beginnt in der Simulation ein zufälliger der Gleichstände (am Tisch: wer es zuerst merkt und sagt). Annahme: Die neue Hälfte beginnt der Verlierer der vorigen Hälfte.
- Startspieler würfelt bis zu 3-mal. Seine Wurfzahl ist für alle anderen die Obergrenze (Annahme: weniger Würfe sind erlaubt).
- Nach jedem Wurf darf man beliebige Würfel herauslegen. Herausgelegte Würfel dürfen **alle** wieder zurück in den Becher.
- Sechsen drehen: 2 Sechsen aus einem Wurf → 1 Eins (der zweite Würfel geht zurück in den Becher), 3 Sechsen → 2 Einsen.
  Nur erlaubt, wenn man danach noch **mindestens so viele Würfe übrig hat, wie man Einsen dreht**
  (also 2 Einsen nur nach dem 1. Wurf; 1 Eins nach dem 1. oder 2. Wurf; die Grenze ist die Wurfzahl des Startspielers).
- Der höchste Wurf der Runde gibt dem niedrigsten Wurf so viele Deckel, wie der höchste Wurf wert ist.

## Wertigkeit (aufsteigend)
| Wurf | Beispiel | Deckel |
|---|---|---|
| Einfacher Wurf (absteigend sortiert verglichen) | 2-2-1 (schlechtester) … 6-6-5 | 1 |
| Straße – **nur aus der Hand**, höhere schlägt niedrigere | 1-2-3 < 2-3-4 < 3-4-5 < 4-5-6 | 2 |
| General – darf zusammengelegt werden | 2-2-2 < … < 6-6-6 | 3 |
| Schock 2 … Schock 6 (Schock 2 schlägt jeden General) | 1-1-2 … 1-1-6 | 2 … 6 |
| Schock Aus (auch zusammengelegt) | 1-1-1 | Hälfte sofort verloren |

- Eine zusammengelegte Straße zählt als einfacher Wurf.
- Keine Sonderwürfe (keine Jule, kein 2-2-1-Sonderwurf, keine Blockregel).

## Gleichstand
1. Wer für den gleichen Wurf weniger Würfe gebraucht hat, gewinnt.
2. Bei gleicher Wurfzahl verliert der spätere Werfer (bzw. gewinnt der frühere).

## Deckel
- Zuerst aus der Mitte. Ist die Mitte leer, gibt der Gewinner der Runde.
- Ist die Mitte leer, scheiden Spieler ohne Deckel für den Rest der Hälfte aus.
- Reicht die Mitte nicht (z. B. 2 übrig, 3 fällig), bekommt der Verlierer nur den Rest aus der Mitte.
  Erst wenn die Mitte leer ist, gibt der Gewinner (höchstens so viele, wie er hat).
- Hälfte 2 beginnt der Verlierer von Hälfte 1, das Finale der Verlierer von Hälfte 2.

## Ziel der Umsetzung
- Terminal-Spiel, lokal; Mensch und Computer mischbar.
- Hauptziel: sehr schnelle Computer-gegen-Computer-Simulation, um optimale Entscheidungen zu finden.

## Information (verdeckt/offen)
- Der Startspieler legt mit seiner Wurfanzahl n (1, 2 oder 3) die Obergrenze für alle fest.
- Er kann einen Wurf **stehen lassen** (Becher bleibt umgedreht). Ein stehen gelassener Wurf ist für **niemanden** sichtbar,
  auch nicht für den Werfer selbst. Die Entscheidung fällt also nur aufgrund der Informationen vor dem Wurf.
- Stehen lassen beendet den Zug. Vor dem 3. Wurf sagt der Startspieler an, dass er fertig ist. Dieser Wurf legt dann n fest.
  Das geht auch schon beim 1. Wurf.
- Unsichtbar sind nur die geworfenen Würfel. Vorher herausgelegte Würfel bleiben sichtbar.
- Hat der Startspieler stehen lassen, gilt für alle anderen: Würfe vor dem n-ten sind offen. Wer bis zum n-ten Wurf würfelt,
  **muss** diesen stehen lassen. Das gilt genauso bei n = 1 (alle lassen den ersten Wurf stehen) und n = 2.
- Hat der Startspieler offen gespielt, spielen alle offen.
- Wer vor der Grenze aufhört, hat ein offenes Ergebnis.
- Aufgedeckt wird alles am Ende der Runde.

### Folge für die Analyse
Kein Spieler hat private Information, denn verdeckte Würfe sind für alle gleich unbekannt. Es gibt also nichts zu bluffen.
Das Spiel lässt sich exakt durch Rückwärtsrechnung (Expectimax über die Verteilungen der verdeckten Würfe) lösen.
