// Prüft, dass die Browser-Version (site/js) dieselben Entscheidungen und Werte liefert wie Python.
// node tests/js/vergleich.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { legaleAktionen, gleicheAktion, bewerte } from "../../site/js/regeln.js";
import { Spiel2 } from "../../site/js/loeser.js";
import { Optimal2, Konter, KonterLoesung, optionen } from "../../site/js/bots.js";
import { KonterNaeherung, Stammtischwerte } from "../../site/js/mehr.js";

const hier = path.dirname(fileURLToPath(import.meta.url));
const daten = p => path.join(hier, "../../site/daten", p);
const lies = p => JSON.parse(readFileSync(p, "utf-8"));
const faelle = lies(path.join(hier, "faelle.json"));
const index = lies(daten("index.json"));
const spiel2 = new Spiel2(lies(daten("loesung2.json")));
const konter = {};
for (const n of index.konter) konter[n] = new KonterLoesung(lies(daten(`konter${n}.json`)), n > 2 ? null : null);
if (konter[3]) konter[3].zwei = konter[2];
const werte = {};
for (const n of index.stammtisch) {
  const buf = readFileSync(daten(`stammtisch${n}.bin`));
  werte[n] = new Stammtischwerte(n, new Float32Array(buf.buffer, buf.byteOffset, buf.length / 4), konter[2]);
}

const norm = a => ({ stopp: !!a.stopp, behalten: [...a.behalten].sort(), drehen: a.drehen, verdeckt: !!a.verdeckt });
let fehler = 0, geprueft = 0, maxDiff = 0;
for (const f of faelle) {
  const s = f.sicht;
  s.bisher.forEach(e => { if (e.wertung && e.wuerfel) e.wertung = bewerte(e.wuerfel, e.ausDerHand); });
  const n = Number(f.art.slice(-1));
  let bot, toleranz = 1e-9;
  if (f.art === "optimal") bot = new Optimal2(spiel2);
  else if (n <= 3) { if (!konter[n]) continue; bot = new Konter(konter); }
  else { if (!werte[n]) continue; bot = new KonterNaeherung(werte, konter); toleranz = 1e-5; }  // Float32-Daten
  geprueft++;
  const legal = legaleAktionen(s);
  if (legal.length !== f.anzahl_legal) { fehler++; console.log("Anzahl erlaubter Aktionen", legal.length, f.anzahl_legal); continue; }
  const a = await bot.entscheide(s);
  if (!gleicheAktion(norm(a), norm(f.aktion))) {
    // nur ein Fehler, wenn die beiden Aktionen laut Python wirklich unterschiedlich gut sind
    const pPy = o => (f.optionen.find(x => gleicheAktion(norm(x.aktion), norm(o))) || { p: NaN }).p;
    if (!(Math.abs(pPy(a) - pPy(f.aktion)) <= toleranz)) { fehler++; console.log("Entscheidung weicht ab", f.art, a, f.aktion); continue; }
  }
  const opts = optionen(bot, s, () => "");
  for (const o of f.optionen) {
    const js = opts.find(x => gleicheAktion(norm(x.aktion), norm(o.aktion)));
    if (!js) { fehler++; console.log("Option fehlt", o.aktion); continue; }
    const d = Math.abs(js.p - o.p);
    maxDiff = Math.max(maxDiff, d);
    if (d > toleranz) { fehler++; console.log("Wert weicht ab", f.art, o.aktion, js.p, o.p); }
  }
}
console.log(`${geprueft} Fälle geprüft, ${fehler} Fehler, größte Wertabweichung ${maxDiff.toExponential(2)}`);
process.exit(fehler ? 1 : 0);
