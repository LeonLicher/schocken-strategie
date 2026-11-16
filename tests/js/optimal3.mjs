// Prüft das Optimum zu dritt im Browser gegen die Python-Lösung und spielt Spiele damit.
// node tests/js/optimal3.mjs
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { spieleSpiel } from "../../site/js/regeln.js";
import { Spiel2 } from "../../site/js/loeser.js";
import { Stammtisch, optionen } from "../../site/js/bots.js";
import { Gleichgewicht3, Optimal3, dist, mitteE, spieleZug } from "../../site/js/optimal3.js";

const daten = path.join(path.dirname(fileURLToPath(import.meta.url)), "../../site/daten");
if (!existsSync(path.join(daten, "optimum3.json"))) { console.log("keine Optimum-Daten, übersprungen"); process.exit(0); }
const d = JSON.parse(readFileSync(path.join(daten, "optimum3.json"), "utf-8"));
const buf = readFileSync(path.join(daten, "optimum3_start.bin"));
const g = new Gleichgewicht3(d, new Float32Array(buf.buffer, buf.byteOffset, buf.length / 4));
const spiel2 = new Spiel2(JSON.parse(readFileSync(path.join(daten, "loesung2.json"), "utf-8")));
const voll = process.argv.includes("--voll");
let fehler = 0;

// 1) Live-Rechnung des mittleren Spielers stimmt mit der Python-Tabelle des Startspielers überein
const proben = [["H1", 13, [0, 0, 0], 0], ["H1", 4, [5, 3, 1], 2], ["H2_1", 0, [4, 6, 3], 1], ["H1", 0, [2, 9, 2], 1]];
let maxAbw = 0;
const t0 = Date.now();
for (const [phase, mitte, deckel, starter] of proben) {
  const reihe = g.reihenfolge(mitte, deckel, starter), Vn = g.vnext(phase, mitte, deckel);
  const { Eo, Ev } = g.starterE(phase, mitte, deckel, starter);
  const ts = voll ? d.t1.map((_, t) => t) : [0, 17, 40, d.n_t1 - 30, d.n_t1 - 1, d.n_t1 - 60];
  for (const t of ts) {
    const [art, x, L] = d.t1[t];
    const f = mitteE(dist(art === 1, x, L, 0), L, art === 1, reihe, Vn);
    const v = spieleZug(f.Eo, f.Ev, reihe[1], L, false, art === 1)[starter];
    const tab = (art === 0 ? Eo : Ev)[x][L][starter];
    maxAbw = Math.max(maxAbw, Math.abs(v - tab));
  }
}
console.log(`Mittlerer Spieler live gegen Python-Tabelle: größte Abweichung ${maxAbw.toExponential(2)} (${Date.now() - t0} ms)`);
if (!(maxAbw < 2e-6)) fehler++;

// 2) Spiele: alle Optimal, und Optimal gegen Stammtisch
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const n = Number(process.argv.find(a => a.startsWith("--spiele="))?.split("=")[1] ?? 6);
for (const [name, besetzung, soll] of [
  ["Optimal x3, Spielbeginner verliert", () => [new Optimal3(g, spiel2), new Optimal3(g, spiel2), new Optimal3(g, spiel2)], 0.3253],
  ["Optimal gegen 2x Stammtisch, Optimal verliert", () => [new Optimal3(g, spiel2), new Stammtisch(), new Stammtisch()], null],
]) {
  let verloren = 0;
  const t = Date.now();
  for (let i = 0; i < n; i++) {
    try {
      const e = await spieleSpiel(besetzung(), rng(5000 + i), null, i % 3);
      if (e.verlierer === (soll === null ? 0 : i % 3)) verloren++;
    } catch (e) { fehler++; console.log("Fehler:", e.stack); break; }
  }
  const q = verloren / n, se = Math.sqrt(0.33 * 0.67 / n);
  console.log(`${name}: ${(q * 100).toFixed(1)} % ± ${(se * 100).toFixed(1)} (${n} Spiele, ${((Date.now() - t) / n / 1000).toFixed(2)} s/Spiel)`);
  if (soll !== null && n >= 200 && Math.abs(q - soll) > 4 * se) fehler++;
}
// 3) Tipps (Berater Optimal) liefern in jeder Lage gültige Wahrscheinlichkeiten, auch im Finale
const berater = new Optimal3(g, spiel2), st = new Stammtisch();
let tipps = 0, kaputt = 0;
const mensch = { name: "Du", async entscheide(s) {
  const o = optionen(berater, s, a => "");
  tipps++; if (!o.length || o.some(x => !(x.p >= -1e-9 && x.p <= 1 + 1e-9))) kaputt++;
  return st.entscheide(s); } };
for (let i = 0; i < 3; i++) await spieleSpiel([mensch, new Optimal3(g, spiel2), new Stammtisch()], rng(9000 + i), null);
console.log(`Tipps: ${tipps} Entscheidungen, ${kaputt} ungültig`);
if (kaputt) fehler++;
console.log(fehler ? `${fehler} Fehler` : "alles in Ordnung");
process.exit(fehler ? 1 : 0);
