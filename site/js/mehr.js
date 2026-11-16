// Konter für 4 bis 6 Spieler (Näherung), Nachbau von schocken/mehr.py.
// Jede Runde exakt entscheiden; die Zukunft mit V0 bewerten (alle spielen Stammtisch, im Finale exakter Konter).
import { GESAMT } from "./regeln.js";
import { W, NH, RANG_W, DECK_W, AUS, P_VERDECKT, U, Uh, zugDp, entscheideAus, wId, hId } from "./loeser.js";
import { Konter } from "./bots.js";

const score = (w, k, pos) => RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos);

// P[h][a][t] als Float64Array (n*8*n), Index (h*8+a)*n+t
export function ausgangVerteilung(n, D) {
  const eintraege = [];
  for (let pos = 0; pos < n; pos++) for (let k = 1; k <= 3; k++) for (let w = 0; w < W; w++) {
    const p = D[pos][w][k];
    if (p > 0) eintraege.push([score(w, k, pos), pos, DECK_W[w], p]);
  }
  eintraege.sort((a, b) => a[0] - b[0]);
  const G = eintraege.length;
  const gpos = new Int32Array(G), gam = new Int32Array(G), gp = new Float64Array(G);
  eintraege.forEach((e, i) => { gpos[i] = e[1]; gam[i] = e[2]; gp[i] = e[3]; });
  const Gl = Array.from({ length: n }, () => new Float64Array(G));
  const lauf = new Float64Array(n);
  for (let g = 0; g < G; g++) { for (let o = 0; o < n; o++) Gl[o][g] = lauf[o]; lauf[gpos[g]] += gp[g]; }
  const P = new Float64Array(n * 8 * n);
  const andere = [];
  for (let h = 0; h < n; h++) for (let t = 0; t < n; t++) {
    if (h === t) continue;
    andere.length = 0;
    for (let o = 0; o < n; o++) if (o !== h && o !== t) andere.push(o);
    const m = andere.length;
    for (let maske = 0; maske < (1 << m); maske++) {
      let praefix = 0;
      for (let g = 0; g < G; g++) {
        const pos = gpos[g];
        if (pos === h) {
          let fx = 1;
          for (let i = 0; i < m; i++) if ((maske >> i) & 1) fx *= Gl[andere[i]][g];
          P[(h * 8 + gam[g]) * n + t] += gp[g] * fx * praefix;
        } else if (pos === t) {
          let fy = 1;
          for (let i = 0; i < m; i++) if (!((maske >> i) & 1)) fy *= -Gl[andere[i]][g];
          praefix += gp[g] * fy;
        }
      }
    }
  }
  return P;
}

function* produkt(n, max) {  // itertools.product(range(max), repeat=n)
  const t = Array(n).fill(0);
  for (;;) {
    yield t;
    let i = n - 1;
    while (i >= 0 && ++t[i] === max) { t[i] = 0; i--; }
    if (i < 0) return;
  }
}

// V0-Tabelle (aus daten/stammtischN.bin) mit derselben Zustandsreihenfolge wie Python
export class Stammtischwerte {
  constructor(n, werte, konter2) {
    this.n = n; this.werte = werte; this.zwei = konter2;
    this.phasen = [...Array.from({ length: n }, (_, l) => `H2_${l}`), "H1"];
    this.offset = new Map();  // Deckel-Code -> [Offset, Liste erlaubter Starter]
    let pos = 0;
    for (let mitte = 0; mitte <= GESAMT; mitte++) {
      for (const d of produkt(n, GESAMT)) {
        let s = 0; for (const x of d) s += x;
        if (s !== GESAMT - mitte) continue;
        const meiste = Math.max(...d);
        const starter = [];
        for (let i = 0; i < n; i++) if (mitte > 0 || d[i] === meiste) starter.push(i);
        this.offset.set(this.code(d), [pos, starter]);
        pos += starter.length;
      }
    }
    this.proPhase = pos;
    if (werte.length !== pos * this.phasen.length) throw new Error(`Stammtischwerte ${n}: falsche Länge`);
  }
  code(d) { let c = 0; for (const x of d) c = c * GESAMT + x; return c; }
  endwert(phase, t) {
    if (phase === "H1") return this.wert(`H2_${t}`, GESAMT, Array(this.n).fill(0), t);
    const l1 = Number(phase.split("_")[1]);
    if (t === l1) return l1 === 0 ? 1 : 0;
    if (l1 !== 0 && t !== 0) return 0;
    return this.zwei.wert("F", GESAMT, [0, 0], t === 0 ? 0 : 1);
  }
  wert(phase, mitte, deckel, starter) {
    for (let i = 0; i < deckel.length; i++) if (deckel[i] >= GESAMT) return this.endwert(phase, i);
    const [off, liste] = this.offset.get(this.code(deckel));
    return this.werte[this.phasen.indexOf(phase) * this.proPhase + off + liste.indexOf(starter)];
  }
  nachRunde(phase, mitte, deckel, h, a, t) {
    if (a === AUS) return this.endwert(phase, t);
    const d = [...deckel];
    let x;
    if (mitte > 0) { x = Math.min(a, mitte); mitte -= x; } else { x = Math.min(a, d[h]); d[h] -= x; }
    d[t] += x;
    if (d[t] >= GESAMT) return this.endwert(phase, t);
    if (mitte > 0) return this.wert(phase, mitte, d, t);
    const meiste = Math.max(...d);
    const kand = d.map((v, i) => i).filter(i => d[i] === meiste);
    return kand.reduce((s, c) => s + this.wert(phase, 0, d, c), 0) / kand.length;
  }
  reihenfolge(mitte, deckel, starter) {
    const aktiv = mitte > 0 ? deckel.map((_, i) => i) : deckel.map((_, i) => i).filter(i => deckel[i] > 0);
    const i = aktiv.indexOf(starter);
    return [...aktiv.slice(i), ...aktiv.slice(0, i)];
  }
}

const leerD = () => Array.from({ length: W }, () => new Float64Array(4));

export class KonterNaeherung {
  // werte: { n: Stammtischwerte }, konter: { 2: KonterLoesung, 3: KonterLoesung } für exakte Fälle
  constructor(werte, konter) { this.name = "Konter"; this.werte = werte; this.exakt = new Konter(konter); this.konter = konter; }
  tabellen(s) {
    const alle = s.deckel.map(([p]) => p), n = alle.length;
    if (this.konter[n]) return this.exakt.tabellen(s);
    const L = this.werte[n];
    if (!L) throw new Error(`Konter ist für ${n} Spieler nicht berechnet.`);
    const ich = s.spieler;
    const rel = new Map(alle.map(p => [p, (alle.indexOf(p) - alle.indexOf(ich) + n) % n]));
    const deckel = Array(n).fill(0);
    for (const [p, d] of s.deckel) deckel[rel.get(p)] = d;
    const phase = s.haelfte === "Hälfte 2" ? `H2_${rel.get(s.haelftenVerlierer[0])}` : "H1";
    const starter = s.istStarter ? ich : s.bisher[0].spieler;
    const reihe = L.reihenfolge(s.mitte, deckel, rel.get(starter));
    const na = reihe.length;
    const Vn = new Float64Array(na * 8 * na);
    for (let i = 0; i < na; i++) for (let j = 0; j < na; j++) if (i !== j)
      for (let a = 1; a < 8; a++) Vn[(i * 8 + a) * na + j] = L.nachRunde(phase, s.mitte, deckel, reihe[i], a, reihe[j]);
    const D = [];
    s.bisher.forEach(e => {
      const d = leerD();
      if (e.verdeckt) { const pv = P_VERDECKT[hId(e.sichtbar)]; for (let w = 0; w < W; w++) d[w][e.wuerfe] = pv[w]; }
      else d[wId(e.wuerfel, e.ausDerHand)][e.wuerfe] = 1;
      D.push(d);
    });
    const p = s.position;
    D.push(leerD());
    for (let pos = p + 1; pos < na; pos++) D.push(null);
    const F = this.konter[2].F;
    const Uo = U(), Uv = Uh();
    const kmax = s.istStarter ? 3 : s.grenze;
    for (let k = 1; k <= kmax; k++) {
      const Lg = s.istStarter ? k : s.grenze;
      const f = F[Lg].map(r => Float64Array.from(r));
      for (let pos = p + 1; pos < na; pos++) D[pos] = f;
      for (let w = 0; w < W; w++) {
        D[p] = leerD(); D[p][w][k] = 1;
        const P = ausgangVerteilung(na, D);
        let x = 0;
        for (let i = 0; i < P.length; i++) if (P[i] !== 0) x += P[i] * Vn[i];
        Uo[w][k] = -x;
      }
      if (s.istStarter || (s.verdecktModus && k === s.grenze))
        for (let h = 0; h < NH; h++) { let x = 0; for (let w = 0; w < W; w++) x += P_VERDECKT[h][w] * Uo[w][k]; Uv[h][k] = x; }
    }
    const grenze = s.istStarter ? 3 : s.grenze, darf = s.istStarter, vm = !s.istStarter && s.verdecktModus;
    const { EV } = zugDp(Uo, Uv, grenze, darf, vm);
    return { Uo, Uv, EV, grenze, darf, vm, umrechnen: q => -q };
  }
  async entscheide(s) { return entscheideAus(this.tabellen(s), s); }
}
