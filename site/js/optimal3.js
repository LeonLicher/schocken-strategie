// Echtes Optimum zu dritt (alle spielen perfekt), Nachbau von schocken/gleichgewicht.py.
// Spielstandswerte und die Tabellen des Startspielers kommen vorberechnet (daten/optimum3.json, optimum3_start.bin);
// der zweite und dritte Spieler werden live gerechnet: Der dritte antwortet optimal auf das, was vor ihm liegt,
// der zweite optimal unter Kenntnis dieser Antwort.
import { GESAMT } from "./regeln.js";
import { W, NH, RANG_W, DECK_W, AUS, P_VERDECKT, ROLL, W_VON, ACT, H_GROESSE, U, Uh, zugDp, wahl, entscheideAus, wId, hId }
  from "./loeser.js";
import { Optimal2 } from "./bots.js";

const N = 3;
const score = (w, k, pos) => RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos);
const vek = () => new Float64Array(N);
const E_O = () => Array.from({ length: W }, () => Array.from({ length: 4 }, vek));
const E_V = () => Array.from({ length: NH }, () => Array.from({ length: 4 }, vek));

// Ergebnis-Verteilung eines Zug-Endes, nach Score aufsteigend
export function dist(verdeckt, x, k, pos) {
  if (!verdeckt) return { sc: [score(x, k, pos)], am: [DECK_W[x]], p: [1], n: 1 };
  const sc = [], am = [], p = [];
  for (let w = 0; w < W; w++) if (P_VERDECKT[x][w] > 0) { sc.push(score(w, k, pos)); am.push(DECK_W[w]); p.push(P_VERDECKT[x][w]); }
  return { sc, am, p, n: sc.length };
}

function praefix(B) {
  const cum = new Float64Array(B.n + 1), cumAm = Array.from({ length: 8 }, () => new Float64Array(B.n + 1));
  for (let j = 0; j < B.n; j++) {
    cum[j + 1] = cum[j] + B.p[j];
    for (let a = 0; a < 8; a++) cumAm[a][j + 1] = cumAm[a][j];
    cumAm[B.am[j]][j + 1] += B.p[j];
  }
  return { cum, cumAm };
}

function suche(arr, n, x) {  // np.searchsorted(arr[:n], x), side="left"
  let lo = 0, hi = n;
  while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] < x) lo = m + 1; else hi = m; }
  return lo;
}

// Vn[h][a][t] = Wertvektor nach der Runde (h gibt a Deckel an t)
function erwPaar(xsc, xam, xz, A, Az, B, Bz, P, Vn, out) {
  for (let i = 0; i < A.n; i++) {
    const pa = A.p[i];
    let hiSc, hiAm, hiZ, loSc, loZ;
    if (A.sc[i] > xsc) { hiSc = A.sc[i]; hiAm = A.am[i]; hiZ = Az; loSc = xsc; loZ = xz; }
    else { hiSc = xsc; hiAm = xam; hiZ = xz; loSc = A.sc[i]; loZ = Az; }
    const iLo = suche(B.sc, B.n, loSc), iHi = suche(B.sc, B.n, hiSc);
    const pUnten = P.cum[iLo], pMitte = P.cum[iHi] - P.cum[iLo];
    for (let c = 0; c < N; c++) {
      let v = pUnten * Vn[hiZ][hiAm][Bz][c] + pMitte * Vn[hiZ][hiAm][loZ][c];
      for (let a = 1; a < 8; a++) {
        const pb = P.cumAm[a][B.n] - P.cumAm[a][iHi];
        if (pb > 0) v += pb * Vn[Bz][a][loZ][c];
      }
      out[c] += pa * v;
    }
  }
}

function erwEinzel(xsc, xam, xz, A, Az, Vn, out) {
  for (let i = 0; i < A.n; i++) {
    const r = A.sc[i] > xsc ? Vn[Az][A.am[i]][xz] : Vn[xz][xam][Az];
    for (let c = 0; c < N; c++) out[c] += A.p[i] * r[c];
  }
}

// Verteilung der Zug-Enden bei optimalem Spiel (Nachbau von gleichgewicht.verteilung)
function verteilung(EV, Uo, Uv, grenze, darf, vm) {
  const To = Array.from({ length: W }, () => new Float64Array(4)), Tv = Array.from({ length: NH }, () => new Float64Array(4));
  if (darf) { if (Uv[0][1] > EV[1][0] + 1e-12) { Tv[0][1] = 1; return { To, Tv }; } }
  else if (vm && grenze === 1) { Tv[0][1] = 1; return { To, Tv }; }
  let front = new Float64Array(NH); front[0] = 1;
  for (let k = 1; k <= grenze; k++) {
    const neu = new Float64Array(NH);
    for (let h = 0; h < NH; h++) {
      if (front[h] === 0) continue;
      const m = 3 - H_GROESSE[h], adh = m === 3 ? 1 : 0;
      for (const [d, s, p0] of ROLL[h]) {
        const p = front[h] * p0;
        if (k === grenze) { To[W_VON[d][adh]][k] += p; continue; }
        const { j, verdeckt } = wahl(EV, Uo, Uv, grenze, darf, vm, k, d, m, s);
        if (j < 0) To[W_VON[d][adh]][k] += p;
        else if (verdeckt) Tv[ACT[d][s][j][0]][k + 1] += p;
        else neu[ACT[d][s][j][0]] += p;
      }
    }
    front = neu;
  }
  return { To, Tv };
}

// Spieler auf Sitz z spielt optimal mit Zug-End-Werten Eo/Ev: Tabellen für seine Entscheidungen
function tabellenAus(Eo, Ev, z, grenze, darf, vm) {
  const Uo = U(), Uv = Uh();
  for (let w = 0; w < W; w++) for (let k = 1; k < 4; k++) Uo[w][k] = -Eo[w][k][z];
  for (let h = 0; h < NH; h++) for (let k = 1; k < 4; k++) Uv[h][k] = -Ev[h][k][z];
  const { EV } = zugDp(Uo, Uv, grenze, darf, vm);
  return { Uo, Uv, EV, grenze, darf, vm, umrechnen: q => -q };
}

// Erwarteter Wertvektor, wenn Sitz z mit Eo/Ev optimal spielt
export function spieleZug(Eo, Ev, z, grenze, darf, vm) {
  const t = tabellenAus(Eo, Ev, z, grenze, darf, vm);
  const { To, Tv } = verteilung(t.EV, t.Uo, t.Uv, grenze, darf, vm);
  const r = vek();
  for (let w = 0; w < W; w++) for (let k = 1; k < 4; k++) if (To[w][k] > 0) for (let c = 0; c < N; c++) r[c] += To[w][k] * Eo[w][k][c];
  for (let h = 0; h < NH; h++) for (let k = 1; k < 4; k++) if (Tv[h][k] > 0) for (let c = 0; c < N; c++) r[c] += Tv[h][k] * Ev[h][k][c];
  return r;
}

function verdecktAusOffen(Eo, Ev, k) {
  for (let h = 0; h < NH; h++) for (let c = 0; c < N; c++) {
    let x = 0;
    for (let w = 0; w < W; w++) x += P_VERDECKT[h][w] * Eo[w][k][c];
    Ev[h][k][c] = x;
  }
}

// Letzter Spieler (Position 2) gegen bekannte Verteilungen d1, d2: Werte seiner Zug-Enden
export function letzterE(d1, d2, L, vm, z, Vn) {
  let A = d1, Az = z[0], B = d2, Bz = z[1];
  if (d1.n > d2.n) { A = d2; Az = z[1]; B = d1; Bz = z[0]; }
  const P = praefix(B), Eo = E_O(), Ev = E_V();
  for (let k = 1; k <= L; k++) for (let w = 0; w < W; w++) erwPaar(score(w, k, 2), DECK_W[w], z[2], A, Az, B, Bz, P, Vn, Eo[w][k]);
  if (vm) verdecktAusOffen(Eo, Ev, L);
  return { Eo, Ev };
}
const letzter = (d1, d2, L, vm, z, Vn) => { const { Eo, Ev } = letzterE(d1, d2, L, vm, z, Vn); return spieleZug(Eo, Ev, z[2], L, false, vm); };

// Mittlerer Spieler gegen bekannte Verteilung d1 des Startspielers: Werte seiner Zug-Enden
export function mitteE(d1, L, vm, z, Vn) {
  const Eo = E_O(), Ev = E_V();
  for (let k2 = 1; k2 <= L; k2++) {
    if (vm && k2 === L) continue;
    for (let w2 = 0; w2 < W; w2++) Eo[w2][k2] = letzter(d1, dist(false, w2, k2, 1), L, vm, z, Vn);
  }
  if (vm) for (let h2 = 0; h2 < (L === 1 ? 1 : NH); h2++) Ev[h2][L] = letzter(d1, dist(true, h2, L, 1), L, vm, z, Vn);
  return { Eo, Ev };
}

// Runde zu zweit (ein Spieler ohne Deckel ist raus): Folgespieler gegen d1
export function letzter2E(d1, L, vm, z, Vn) {
  const Eo = E_O(), Ev = E_V();
  for (let k = 1; k <= L; k++) for (let w = 0; w < W; w++) erwEinzel(score(w, k, 1), DECK_W[w], z[1], d1, z[0], Vn, Eo[w][k]);
  if (vm) verdecktAusOffen(Eo, Ev, L);
  return { Eo, Ev };
}

export class Gleichgewicht3 {
  // d = optimum3.json, Q = Float32Array aus optimum3_start.bin
  constructor(d, Q) {
    this.f0 = d.f0; this.nT1 = d.n_t1; this.t1 = d.t1; this.Q = Q;
    this.V = new Map(); this.idx = new Map();
    for (const [phase, liste] of Object.entries(d.V)) {
      const m = new Map(), ix = new Map();
      for (const z of liste) { const k = z.slice(0, 5).join(","); m.set(k, Float64Array.from(z.slice(5, 8))); ix.set(k, z[8]); }
      this.V.set(phase, m); this.idx.set(phase, ix);
    }
  }
  endwert(phase, t) {
    if (phase === "H1") return this.wert(`H2_${t}`, GESAMT, [0, 0, 0], t);
    const l1 = Number(phase.split("_")[1]), v = vek();
    if (t === l1) v[l1] = 1; else { v[t] = this.f0; v[l1] = 1 - this.f0; }
    return v;
  }
  wert(phase, mitte, deckel, starter) {
    for (let i = 0; i < N; i++) if (deckel[i] >= GESAMT) return this.endwert(phase, i);
    return this.V.get(phase).get([mitte, ...deckel, starter].join(","));
  }
  nachRunde(phase, mitte, deckel, h, a, t) {
    if (a === AUS) return this.endwert(phase, t);
    const d = [...deckel];
    let x;
    if (mitte > 0) { x = Math.min(a, mitte); mitte -= x; } else { x = Math.min(a, d[h]); d[h] -= x; }
    d[t] += x;
    if (d[t] >= GESAMT) return this.endwert(phase, t);
    if (mitte > 0) return this.wert(phase, mitte, d, t);
    const meiste = Math.max(...d), kand = [0, 1, 2].filter(i => d[i] === meiste), v = vek();
    for (const c of kand) { const x2 = this.wert(phase, 0, d, c); for (let i = 0; i < N; i++) v[i] += x2[i] / kand.length; }
    return v;
  }
  vnext(phase, mitte, deckel) {
    return [0, 1, 2].map(h => Array.from({ length: 8 }, (_, a) => [0, 1, 2].map(t =>
      h !== t && a > 0 ? this.nachRunde(phase, mitte, deckel, h, a, t) : vek())));
  }
  reihenfolge(mitte, deckel, starter) {
    const aktiv = mitte > 0 ? [0, 1, 2] : [0, 1, 2].filter(i => deckel[i] > 0);
    const i = aktiv.indexOf(starter);
    return [...aktiv.slice(i), ...aktiv.slice(0, i)];
  }
  // Startspieler mit drei aktiven Spielern: Tabelle P(ich verliere | Zug-Ende t)
  starterE(phase, mitte, deckel, starter) {
    const i = this.idx.get(phase).get([mitte, ...deckel, starter].join(","));
    const Eo = E_O(), Ev = E_V();
    for (let t = 0; t < this.nT1; t++) {
      const [art, x, k] = this.t1[t];
      (art === 0 ? Eo : Ev)[x][k][starter] = this.Q[i * this.nT1 + t];
    }
    return { Eo, Ev };
  }
}

// Bot: spielt das Gleichgewicht (zu dritt; im Finale zu zweit exakt optimal)
export class Optimal3 {
  constructor(g, spiel2) { this.name = "Optimal"; this.g = g; this.zwei = new Optimal2(spiel2); this.cache = new Map(); }
  tabellen(s) {
    if (s.deckel.length === 2) {  // Finale: Optimal2 erwartet die Spieler 0 und 1
      const nr = new Map(s.deckel.map(([p], i) => [p, i]));
      return this.zwei.tabellen({ ...s, spieler: nr.get(s.spieler), deckel: s.deckel.map(([p, d]) => [nr.get(p), d]),
        bisher: s.bisher.map(e => ({ ...e, spieler: nr.get(e.spieler) })), haelftenVerlierer: [] });
    }
    if (s.deckel.length !== 3) throw new Error("Optimal ist nur für 2 und 3 Spieler gelöst.");
    const sitz = new Map(s.deckel.map(([p], i) => [p, i]));
    const deckel = s.deckel.map(([, d]) => d);
    const phase = s.haelfte === "Hälfte 2" ? `H2_${sitz.get(s.haelftenVerlierer[0])}` : "H1";
    const starter = sitz.get(s.istStarter ? s.spieler : s.bisher[0].spieler);
    const ich = sitz.get(s.spieler);
    const reihe = this.g.reihenfolge(s.mitte, deckel, starter);
    const vor = s.bisher.map((e, pos) => e.verdeckt ? dist(true, hId(e.sichtbar), e.wuerfe, pos)
      : dist(false, wId(e.wuerfel, e.ausDerHand), e.wuerfe, pos));
    const schl = [phase, s.mitte, ...deckel, starter, ich, ...s.bisher.map(e => e.verdeckt ? `v${hId(e.sichtbar)}/${e.wuerfe}`
      : `o${wId(e.wuerfel, e.ausDerHand)}/${e.wuerfe}`)].join("|");
    if (this.cache.has(schl)) return this.cache.get(schl);
    const z = [...reihe, 0, 0].slice(0, 3);
    let t;
    if (s.istStarter && reihe.length === 3) {
      const { Eo, Ev } = this.g.starterE(phase, s.mitte, deckel, starter);
      t = tabellenAus(Eo, Ev, ich, 3, true, false);
    } else {
      const Vn = this.g.vnext(phase, s.mitte, deckel);
      if (s.istStarter) {  // zu zweit: Folgespieler antwortet optimal
        const Eo = E_O(), Ev = E_V();
        for (const [art, x, L] of this.g.t1) {
          const f = letzter2E(dist(art === 1, x, L, 0), L, art === 1, z, Vn);
          (art === 0 ? Eo : Ev)[x][L] = spieleZug(f.Eo, f.Ev, z[1], L, false, art === 1);
        }
        t = tabellenAus(Eo, Ev, ich, 3, true, false);
      } else {
        const L = s.grenze, vm = s.verdecktModus;
        let f;
        if (reihe.length === 2) f = letzter2E(vor[0], L, vm, z, Vn);
        else if (s.position === 1) f = mitteE(vor[0], L, vm, z, Vn);
        else f = letzterE(vor[0], vor[1], L, vm, z, Vn);
        t = tabellenAus(f.Eo, f.Ev, ich, L, false, vm);
      }
    }
    if (this.cache.size > 200) this.cache.clear();
    this.cache.set(schl, t);
    return t;
  }
  async entscheide(s) { return entscheideAus(this.tabellen(s), s); }
}
