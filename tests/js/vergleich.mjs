// Prüft, dass die Browser-Version (site/js) dieselben Entscheidungen und Werte liefert wie Python.
// node tests/js/vergleich.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { legaleAktionen, gleicheAktion, bewerte } from "../../site/js/regeln.js";
import { Spiel2 } from "../../site/js/loeser.js";
import { Optimal2, Konter, KonterLoesung, optionen } from "../../site/js/bots.js";

const hier = path.dirname(fileURLToPath(import.meta.url));
const lies = p => JSON.parse(readFileSync(path.join(hier, p), "utf-8"));
const faelle = lies("faelle.json");
const spiel2 = new Spiel2(lies("../../site/daten/loesung2.json"));
const k2 = new KonterLoesung(lies("../../site/daten/konter2.json"));
const loesungen = { 2: k2 };
try { loesungen[3] = new KonterLoesung(lies("../../site/daten/konter3.json"), k2); } catch (e) { /* noch nicht berechnet */ }

const norm = a => ({ stopp: !!a.stopp, behalten: [...a.behalten].sort(), drehen: a.drehen, verdeckt: !!a.verdeckt });
let fehler = 0, geprueft = 0, maxDiff = 0;
for (const f of faelle) {
  const s = f.sicht;
  // Python liefert Wertung nur als Name; für die Bots reicht wuerfel + ausDerHand
  s.bisher.forEach(e => { if (e.wertung && e.wuerfel) e.wertung = bewerte(e.wuerfel, e.ausDerHand); });
  const bot = f.art === "optimal" ? new Optimal2(spiel2) : new Konter(loesungen);
  if (f.art !== "optimal" && !loesungen[Number(f.art.slice(-1))]) continue;
  geprueft++;
  const legal = legaleAktionen(s);
  if (legal.length !== f.anzahl_legal) { fehler++; console.log("Anzahl erlaubter Aktionen", legal.length, f.anzahl_legal); continue; }
  const a = await bot.entscheide(s);
  if (!gleicheAktion(norm(a), norm(f.aktion))) { fehler++; console.log("Entscheidung weicht ab", f.art, JSON.stringify(s), a, f.aktion); continue; }
  const opts = optionen(bot, s, () => "");
  for (const o of f.optionen) {
    const js = opts.find(x => gleicheAktion(norm(x.aktion), norm(o.aktion)));
    if (!js) { fehler++; console.log("Option fehlt", o.aktion); continue; }
    const d = Math.abs(js.p - o.p);
    maxDiff = Math.max(maxDiff, d);
    if (d > 1e-9) { fehler++; console.log("Wert weicht ab", f.art, o.aktion, js.p, o.p); }
  }
}
console.log(`${geprueft} Fälle geprüft, ${fehler} Fehler, größte Wertabweichung ${maxDiff.toExponential(2)}`);
process.exit(fehler ? 1 : 0);
