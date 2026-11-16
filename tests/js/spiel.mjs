// Spielt komplette Spiele mit der Browser-Engine (ohne Oberfläche).
// node tests/js/spiel.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { spieleSpiel } from "../../site/js/regeln.js";
import { Spiel2 } from "../../site/js/loeser.js";
import { Stammtisch, Faustregel, Optimal2, Konter, KonterLoesung } from "../../site/js/bots.js";
import { KonterNaeherung, Stammtischwerte } from "../../site/js/mehr.js";

const hier = path.dirname(fileURLToPath(import.meta.url));
const lies = p => JSON.parse(readFileSync(path.join(hier, "../../site/daten", p), "utf-8"));
const spiel2 = new Spiel2(lies("loesung2.json"));
const k2 = new KonterLoesung(lies("konter2.json"));
const L = { 2: k2, 3: new KonterLoesung(lies("konter3.json"), k2) };
const werte = {};
for (const n of lies("index.json").stammtisch) {
  const buf = readFileSync(path.join(hier, "../../site/daten", `stammtisch${n}.bin`));
  werte[n] = new Stammtischwerte(n, new Float32Array(buf.buffer, buf.byteOffset, buf.length / 4), k2);
}

// kleiner deterministischer Zufallsgenerator (mulberry32)
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

let fehler = 0;
const typen = new Set();
const log = new Proxy({}, { get: (_, name) => () => typen.add(name) });

// 1) Alle Bot-Kombinationen spielen fehlerfrei durch
const besetzungen = [
  () => [new Optimal2(spiel2), new Stammtisch()],
  () => [new Konter(L), new Faustregel(), new Stammtisch()],
  () => [new Stammtisch(), new Faustregel(), new Stammtisch(), new Faustregel(), new Stammtisch(), new Faustregel()],
];
for (const n of Object.keys(werte).map(Number))
  besetzungen.push(() => [new KonterNaeherung(werte, L), ...Array.from({ length: n - 1 }, () => new Stammtisch())]);
for (const b of besetzungen) {
  const anzahlSpiele = b().length >= 5 ? 3 : 20;  // 5-6 Spieler mit Konter sind rechenintensiv: Funktionstest reicht
  for (let i = 0; i < anzahlSpiele; i++) {
    try { await spieleSpiel(b(), rng(i + 1), log); } catch (e) { fehler++; console.log("Fehler:", e.message); }
  }
}
for (const t of ["haelfteStart", "rundeStart", "wurf", "aktion", "zugEnde", "runde", "haelfteEnde"]) {
  if (!typen.has(t)) { fehler++; console.log("Ereignis fehlt:", t); }
}

// 2) Konter gegen 2x Stammtisch: Verlustquote wie in Python (14,4 %)
const n = 400;  // genügt, um grobe Fehler zu erkennen; genaue Prüfung macht werkzeuge/pruefe_konter.py
let verloren = 0;
for (let i = 0; i < n; i++) {
  const e = await spieleSpiel([new Konter(L), new Stammtisch(), new Stammtisch()], rng(1000 + i), null, i % 3);
  if (e.verlierer === 0) verloren++;
}
const q = verloren / n, se = Math.sqrt(0.144 * 0.856 / n);
console.log(`Konter verliert ${(q * 100).toFixed(1)} % (Python: 14,4 %, Abweichung ${((q - 0.144) / se).toFixed(2)} SE)`);
if (Math.abs(q - 0.144) > 4 * se) fehler++;
console.log(fehler ? `${fehler} Fehler` : "alles in Ordnung");
process.exit(fehler ? 1 : 0);
