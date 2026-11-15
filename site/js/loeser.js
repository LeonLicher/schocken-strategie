// Nachbau von schocken/loeser.py: Tabellen, Zug-Löser (zug_dp), Entscheidung (wahl) und Runde zu zweit.
import { bewerte, rang, SCHOCK_AUS, GESAMT } from "./regeln.js";

// ------------------------------------------------------------------ Tabellen
function cwr(n) {  // combinations_with_replacement(range(1,7), n), aufsteigend
  if (n === 0) return [[]];
  const aus = [];
  const rek = (start, praefix) => {
    if (praefix.length === n) { aus.push(praefix); return; }
    for (let v = start; v <= 6; v++) rek(v, [...praefix, v]);
  };
  rek(1, []);
  return aus;
}

const alle = new Map();
for (const d of cwr(3)) for (const adh of [false, true]) { const w = bewerte(d, adh); alle.set(w.name, w); }
export const WERTUNGEN = [...alle.values()].sort((a, b) => rang(a) - rang(b));
export const W = WERTUNGEN.length;
const W_ID = new Map(WERTUNGEN.map((w, i) => [w.name, i]));
export const wId = (wuerfel, adh) => W_ID.get(bewerte(wuerfel, adh).name);
export const RANG_W = WERTUNGEN.map(rang);
export const AUS = 7;
export const DECK_W = WERTUNGEN.map(w => (w.klasse === SCHOCK_AUS ? AUS : w.deckel));

export const D_LISTE = cwr(3);
const D_KEY = new Map(D_LISTE.map((d, i) => [d.join(","), i]));
export const dId = wuerfel => D_KEY.get([...wuerfel].sort((a, b) => a - b).join(","));
export const H_LISTE = [[], ...cwr(1), ...cwr(2)];
export const NH = H_LISTE.length;
const H_KEY = new Map(H_LISTE.map((h, i) => [h.join(","), i]));
export const hId = wuerfel => H_KEY.get([...wuerfel].sort((a, b) => a - b).join(","));
const SECHSEN = D_LISTE.map(d => d.filter(x => x === 6).length);

export const W_VON = D_LISTE.map(d => [wId(d, false), wId(d, true)]);

function produkt(r) {
  if (r === 0) return [[]];
  const aus = [];
  for (const rest of produkt(r - 1)) for (let v = 1; v <= 6; v++) aus.push([...rest, v]);
  return aus;
}
// Würfeln mit gehaltenen Würfeln h -> Verteilung über (d, s); P_VERDECKT[h][w]
export const ROLL = [];
export const P_VERDECKT = [];
H_LISTE.forEach((h, hi) => {
  const r = 3 - h.length;
  const vert = new Map();
  const pv = new Float64Array(W);
  for (const wurf of produkt(r)) {
    const d = dId([...h, ...wurf]);
    const s = wurf.filter(x => x === 6).length;
    const key = d * 4 + s;
    vert.set(key, (vert.get(key) || 0) + 6 ** -r);
    pv[W_VON[d][r === 3 ? 1 : 0]] += 6 ** -r;
  }
  ROLL.push([...vert.entries()].sort((a, b) => a[0] - b[0]).map(([key, p]) => [Math.floor(key / 4), key % 4, p]));
  P_VERDECKT.push(pv);
});
export const H_GROESSE = H_LISTE.map(h => h.length);

function kombis(liste, k) {
  if (k === 0) return [[]];
  const aus = [];
  liste.forEach((x, i) => kombis(liste.slice(i + 1), k - 1).forEach(r => aus.push([x, ...r])));
  return aus;
}
// ACT[d][s] = Liste [h, t] (je h das kleinste t), nach h sortiert
export const ACT = D_LISTE.map((d, di) => {
  const proS = [];
  for (let s = 0; s <= 3; s++) {
    const beste = new Map();
    if (s <= SECHSEN[di]) {
      for (let t = 0; t < 3; t++) {
        if (t && s < t + 1) continue;
        const pool = [...d];
        for (let i = 0; i < (t ? t + 1 : 0); i++) pool.splice(pool.indexOf(6), 1);
        pool.sort((a, b) => a - b);
        for (let g = 0; g < 3 - t; g++) {
          for (const k of kombis(pool, g)) {
            const h = hId([...k, ...Array(t).fill(1)]);
            if (!beste.has(h) || t < beste.get(h)) beste.set(h, t);
          }
        }
      }
    }
    proS.push([...beste.entries()].sort((a, b) => a[0] - b[0]));
  }
  return proS;
});

export function behaltenVon(h, t) {
  const rest = [...H_LISTE[h]];
  for (let i = 0; i < t; i++) rest.splice(rest.indexOf(1), 1);
  return rest;
}

// ------------------------------------------------------------------ Zug-Löser
const vIdx = (k, d, m, s) => ((k * 56 + d) * 4 + m) * 4 + s;
export const U = () => Array.from({ length: W }, () => new Float64Array(4));
export const Uh = () => Array.from({ length: NH }, () => new Float64Array(4));

export function zugDp(Uo, Uv, grenze, darf, vm) {
  const V = new Float64Array(4 * 56 * 4 * 4);
  const EV = Array.from({ length: 5 }, () => new Float64Array(NH));
  for (let k = grenze; k >= 1; k--) {
    const rest = grenze - k;
    for (let d = 0; d < 56; d++) {
      for (let m = 1; m <= 3; m++) {
        const stopp = Uo[W_VON[d][m === 3 ? 1 : 0]][k];
        const smax = Math.min(m, SECHSEN[d]);
        for (let s = 0; s <= smax; s++) {
          let best = stopp;
          if (rest > 0) {
            for (const [h, t] of ACT[d][s]) {
              if (t > rest) continue;
              let c;
              if (darf) c = Math.max(EV[k + 1][h], Uv[h][k + 1]);
              else if (vm && k + 1 === grenze) c = Uv[h][k + 1];
              else c = EV[k + 1][h];
              if (c > best) best = c;
            }
          }
          V[vIdx(k, d, m, s)] = best;
        }
      }
    }
    for (let h = 0; h < NH; h++) {
      const m = 3 - H_GROESSE[h];
      let e = 0;
      for (const [d, s, p] of ROLL[h]) e += p * V[vIdx(k, d, m, s)];
      EV[k][h] = e;
    }
  }
  let wert;
  if (darf) wert = Math.max(EV[1][0], Uv[0][1]);
  else if (vm && grenze === 1) wert = Uv[0][1];
  else wert = EV[1][0];
  return { wert, V, EV };
}

// Beste Entscheidung im Zustand (k, d, m, s): { j: Index in ACT[d][s] oder -1 (aufhören), verdeckt }
export function wahl(EV, Uo, Uv, grenze, darf, vm, k, d, m, s) {
  let best = Uo[W_VON[d][m === 3 ? 1 : 0]][k];
  let bj = -1, bv = false;
  if (grenze - k <= 0) return { j: bj, verdeckt: bv };
  ACT[d][s].forEach(([h, t], j) => {
    if (t > grenze - k) return;
    if (darf) {
      if (EV[k + 1][h] > best + 1e-12) { best = EV[k + 1][h]; bj = j; bv = false; }
      if (Uv[h][k + 1] > best + 1e-12) { best = Uv[h][k + 1]; bj = j; bv = true; }
    } else if (vm && k + 1 === grenze) {
      if (Uv[h][k + 1] > best + 1e-12) { best = Uv[h][k + 1]; bj = j; bv = true; }
    } else if (EV[k + 1][h] > best + 1e-12) { best = EV[k + 1][h]; bj = j; bv = false; }
  });
  return { j: bj, verdeckt: bv };
}

// Bewertung aller erlaubten Aktionen aus Tabellen (q = Wert für den Entscheider, größer = besser)
export function aktionsWert(t, sicht, a) {
  if (sicht.phase === "vor_wurf") return a.verdeckt ? t.Uv[0][1] : t.EV[1][0];
  if (a.stopp) return t.Uo[W_VON[dId(sicht.wuerfel)][sicht.neu.length === 3 ? 1 : 0]][sicht.wurfNr];
  const h = hId([...a.behalten, ...Array(a.drehen).fill(1)]);
  return a.verdeckt ? t.Uv[h][sicht.wurfNr + 1] : t.EV[sicht.wurfNr + 1][h];
}

// Entscheidung aus Tabellen ableiten
export function entscheideAus(t, sicht) {
  if (sicht.phase === "vor_wurf") return { stopp: false, behalten: [], drehen: 0, verdeckt: t.Uv[0][1] > t.EV[1][0] + 1e-12 };
  const d = dId(sicht.wuerfel), m = sicht.neu.length, s = sicht.neu.filter(x => x === 6).length;
  const { j, verdeckt } = wahl(t.EV, t.Uo, t.Uv, t.grenze, t.darf, t.vm, sicht.wurfNr, d, m, s);
  if (j < 0) return { stopp: true, behalten: [], drehen: 0, verdeckt: false };
  const [h, tt] = ACT[d][s][j];
  return { stopp: false, behalten: behaltenVon(h, tt), drehen: tt, verdeckt };
}

// ------------------------------------------------------------------ Runde zu zweit (Optimal)
function ausgang(w1, k1, w2, k2, A, B) {
  if (RANG_W[w2] > RANG_W[w1] || (RANG_W[w2] === RANG_W[w1] && k2 < k1)) return A[DECK_W[w2]];
  return B[DECK_W[w1]];
}

export function folgerBewertung(p1, k1, A, B, vm) {
  const Uo = U(), Uv = Uh();
  for (let w2 = 0; w2 < W; w2++) {
    for (let k2 = 1; k2 <= k1; k2++) {
      let x = 0;
      for (let w1 = 0; w1 < W; w1++) if (p1[w1] > 0) x += p1[w1] * ausgang(w1, k1, w2, k2, A, B);
      Uo[w2][k2] = x;
    }
  }
  if (vm) for (let h = 0; h < NH; h++) { let x = 0; for (let w = 0; w < W; w++) x += P_VERDECKT[h][w] * Uo[w][k1]; Uv[h][k1] = x; }
  return { Uo, Uv };
}

export function starterBewertung(A, B) {
  const Uo = U(), Uv = Uh();
  for (let k1 = 1; k1 <= 3; k1++) {
    for (let w1 = 0; w1 < W; w1++) {
      const p1 = new Float64Array(W); p1[w1] = 1;
      const f = folgerBewertung(p1, k1, A, B, false);
      Uo[w1][k1] = -zugDp(f.Uo, f.Uv, k1, false, false).wert;
    }
    for (let h1 = 0; h1 < (k1 === 1 ? 1 : NH); h1++) {
      const f = folgerBewertung(P_VERDECKT[h1], k1, A, B, true);
      Uv[h1][k1] = -zugDp(f.Uo, f.Uv, k1, false, true).wert;
    }
  }
  return { Uo, Uv };
}

// Lösung zu zweit (aus daten/loesung2.json): Hälfte -> {t0, t1, X: Map "mitte,d0,starter" -> P(Spieler 0 verliert)}
export class Haelfte2 {
  constructor(d) { this.t0 = d.t0; this.t1 = d.t1; this.X = new Map(d.X.map(([m, d0, s, v]) => [`${m},${d0},${s}`, v])); }
  wert(mitte, d0, starter) {
    const d1 = GESAMT - mitte - d0;
    if (d0 === GESAMT) return this.t0;
    if (d1 === GESAMT) return this.t1;
    return this.X.get(`${mitte},${d0},${starter}`);
  }
  nachTransfer(mitte, d0, empf, a) {
    if (a === AUS) return empf === 0 ? this.t0 : this.t1;
    const d = [d0, GESAMT - mitte - d0];
    let x;
    if (mitte > 0) { x = Math.min(a, mitte); mitte -= x; } else { x = Math.min(a, d[1 - empf]); d[1 - empf] -= x; }
    d[empf] += x;
    const starter = mitte > 0 ? empf : (d[0] > d[1] ? 0 : 1);
    return this.wert(mitte, d[0], starter);
  }
  AB(mitte, d0, starter) {
    const A = new Float64Array(8), B = new Float64Array(8);
    for (let a = 1; a < 8; a++) {
      const xa = this.nachTransfer(mitte, d0, starter, a), xb = this.nachTransfer(mitte, d0, 1 - starter, a);
      A[a] = starter === 0 ? xa : 1 - xa; B[a] = starter === 0 ? xb : 1 - xb;
    }
    return { A, B };
  }
}

export class Spiel2 {
  constructor(d) {
    this.finale = new Haelfte2(d.finale); this.h1 = new Haelfte2(d.h1);
    this.h2 = { 0: new Haelfte2(d.h2_0), 1: new Haelfte2(d.h2_1) };
  }
  haelfte(name, verlierer) { return name === "Finale" ? this.finale : name === "Hälfte 2" ? this.h2[verlierer[0]] : this.h1; }
}
