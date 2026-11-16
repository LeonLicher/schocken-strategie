// Bots: Stammtisch, Faustregel, Optimal (zu zweit), Konter (beste Antwort auf Stammtisch), Berater für Tipps.
import { bewerte, rang, STRASSE, STOPP, GESAMT, legaleAktionen } from "./regeln.js";
import { W, NH, RANG_W, DECK_W, AUS, P_VERDECKT, U, Uh, zugDp, entscheideAus, aktionsWert, folgerBewertung,
         starterBewertung, wId, hId } from "./loeser.js";

// ------------------------------------------------------------------ Stammtisch und Faustregel
export function stammtischEntscheidung(wurfNr, wuerfel, neu, grenze, istStarter) {
  if (bewerte(wuerfel, neu.length === 3).klasse >= STRASSE) return null;
  const einsen = Math.min(wuerfel.filter(x => x === 1).length, 2);
  if (istStarter && wurfNr >= 2 && einsen >= 1) return null;
  const rest = grenze - wurfNr, sechsen = neu.filter(x => x === 6).length;
  if (einsen === 0 && sechsen >= 3 && rest >= 2) return [[], 2];
  if (einsen < 2 && sechsen >= 2) return [Array(einsen).fill(1), 1];
  return [Array(einsen).fill(1), 0];
}

export class Stammtisch {
  constructor() { this.name = "Stammtisch"; }
  async entscheide(s) {
    if (s.phase === "vor_wurf") return { stopp: false, behalten: [], drehen: 0, verdeckt: false };
    const e = stammtischEntscheidung(s.wurfNr, s.wuerfel, s.neu, s.grenze, s.istStarter);
    return e === null ? STOPP : { stopp: false, behalten: e[0], drehen: e[1], verdeckt: s.istStarter && s.wurfNr === 2 };
  }
}

const vergleich = (r, wurf, pos) => [r, -wurf, -pos];
const groesser = (a, b) => { for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] > b[i]; return false; };

export class Faustregel {  // Parameter (1, 3, 1, 0, 1): Startspieler wirft den dritten Wurf verdeckt
  constructor() { this.name = "Faustregel"; }
  async entscheide(s) {
    if (s.phase === "vor_wurf") return { stopp: false, behalten: [], drehen: 0, verdeckt: false };
    const w = bewerte(s.wuerfel, s.neu.length === 3);
    let zufrieden;
    const offen = s.bisher.filter(e => !e.verdeckt).map(e => vergleich(rang(e.wertung), e.wuerfe, e.position));
    if (s.istStarter || !offen.length) zufrieden = w.klasse >= STRASSE;
    else {
      const schlechtester = offen.reduce((a, b) => (groesser(a, b) ? b : a));
      zufrieden = groesser(vergleich(rang(w), s.wurfNr, s.position), schlechtester);
    }
    if (zufrieden) return STOPP;
    const einsen = Math.min(s.wuerfel.filter(x => x === 1).length, 2), sechsen = s.neu.filter(x => x === 6).length;
    const rest = s.grenze - s.wurfNr, verdeckt = s.istStarter && s.wurfNr === 2;
    if (einsen === 0 && sechsen >= 3 && rest >= 2) return { stopp: false, behalten: [], drehen: 2, verdeckt };
    if (einsen < 2 && sechsen >= 2) return { stopp: false, behalten: Array(einsen).fill(1), drehen: 1, verdeckt };
    return { stopp: false, behalten: Array(einsen).fill(1), drehen: 0, verdeckt };
  }
}

// ------------------------------------------------------------------ Optimal zu zweit
export class Optimal2 {
  constructor(spiel2) { this.name = "Optimal"; this.s = spiel2; this.cache = new Map(); }
  tabellen(s) {
    if (s.deckel.length !== 2) throw new Error("Optimal ist nur für 2 Spieler gelöst.");
    const h = this.s.haelfte(s.haelfte, s.haelftenVerlierer);
    const d0 = Object.fromEntries(s.deckel)[0];
    const starter = s.istStarter ? s.spieler : s.bisher[0].spieler;
    let schl, e;
    if (s.istStarter) schl = `${s.haelfte}|${s.haelftenVerlierer}|${s.mitte}|${d0}|${starter}`;
    else {
      e = s.bisher[0];
      const ende = e.verdeckt ? `v${hId(e.sichtbar)}` : `o${e.wertung.name}`;
      schl = `${s.haelfte}|${s.haelftenVerlierer}|${s.mitte}|${d0}|${starter}|${ende}|${e.wuerfe}`;
    }
    if (this.cache.has(schl)) return this.cache.get(schl);
    const { A, B } = h.AB(s.mitte, d0, starter);
    let Uo, Uv, grenze, darf, vm, umrechnen;
    if (s.istStarter) {
      ({ Uo, Uv } = starterBewertung(A, B)); grenze = 3; darf = true; vm = false; umrechnen = q => -q;
    } else {
      let p1;
      if (e.verdeckt) { p1 = P_VERDECKT[hId(e.sichtbar)]; vm = true; }
      else { p1 = new Float64Array(W); p1[wId(e.wuerfel, e.ausDerHand)] = 1; vm = false; }
      ({ Uo, Uv } = folgerBewertung(p1, e.wuerfe, A, B, vm)); grenze = e.wuerfe; darf = false; umrechnen = q => 1 - q;
    }
    const { EV } = zugDp(Uo, Uv, grenze, darf, vm);
    const t = { Uo, Uv, EV, grenze, darf, vm, umrechnen };
    this.cache.set(schl, t);
    return t;
  }
  async entscheide(s) { return entscheideAus(this.tabellen(s), s); }
}

// ------------------------------------------------------------------ Konter (beste Antwort auf Stammtisch)
const score = (w, k, pos) => RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos);

function traeger(Dpos, pos) {
  const sc = [], am = [], p = [];
  for (let k = 1; k <= 3; k++) for (let w = 0; w < W; w++) if (Dpos[w][k] > 0) { sc.push(score(w, k, pos)); am.push(DECK_W[w]); p.push(Dpos[w][k]); }
  return { sc: Int32Array.from(sc), am: Int32Array.from(am), p: Float64Array.from(p), n: sc.length };
}

function erwartung(n, seats, D, Vn) {
  // D[pos] = Array W von Float64Array(4): Verteilung über (w, k). Schnell, ohne Hilfsobjekte in der Schleife.
  const T = [];
  for (let pos = 0; pos < n; pos++) T.push(traeger(D[pos], pos));
  const z0 = seats[0], z1 = seats[1], z2 = seats[2];
  let tot = 0;
  const A = T[0], B = T[1];
  for (let i = 0; i < A.n; i++) {
    const s0 = A.sc[i], a0 = A.am[i], p0 = A.p[i];
    for (let j = 0; j < B.n; j++) {
      const s1 = B.sc[j], a1 = B.am[j], p01 = p0 * B.p[j];
      if (n === 2) {
        tot += p01 * (s1 > s0 ? Vn[(z1 * 8 + a1) * n + z0] : Vn[(z0 * 8 + a0) * n + z1]);
        continue;
      }
      const C = T[2];
      for (let l = 0; l < C.n; l++) {
        const s2 = C.sc[l];
        let hz = z0, ha = a0, hs = s0, tz = z0, ts = s0;
        if (s1 > hs) { hz = z1; ha = a1; hs = s1; }
        if (s1 < ts) { tz = z1; ts = s1; }
        if (s2 > hs) { hz = z2; ha = C.am[l]; hs = s2; }
        if (s2 < ts) { tz = z2; ts = s2; }
        tot += p01 * C.p[l] * Vn[(hz * 8 + ha) * n + tz];
      }
    }
  }
  return tot;
}

const leerD = () => Array.from({ length: W }, () => new Float64Array(4));

export class KonterLoesung {
  constructor(d, zwei = null) {
    this.n = d.n; this.zwei = zwei;
    this.V = new Map();
    for (const [phase, liste] of Object.entries(d.V)) {
      const m = new Map();
      for (const z of liste) m.set(z.slice(0, -1).join(","), z[z.length - 1]);
      this.V.set(phase, m);
    }
    this.S = d.S; this.F = d.F;  // S[w][k], F[L][w][k]
  }
  endwert(phase, t) {
    if (phase === "F") return t === 0 ? 1 : 0;
    if (phase === "H1") return this.wert(`H2_${t}`, GESAMT, Array(this.n).fill(0), t);
    const l1 = Number(phase.split("_")[1]);
    if (t === l1) return l1 === 0 ? 1 : 0;
    if (l1 !== 0 && t !== 0) return 0;
    if (this.n === 2) return this.wert("F", GESAMT, [0, 0], t);
    return this.zwei.wert("F", GESAMT, [0, 0], t === 0 ? 0 : 1);
  }
  wert(phase, mitte, deckel, starter) {
    for (let i = 0; i < deckel.length; i++) if (deckel[i] >= GESAMT) return this.endwert(phase, i);
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
    const meiste = Math.max(...d);
    const kand = d.map((v, i) => i).filter(i => d[i] === meiste);
    return kand.reduce((s, c) => s + this.wert(phase, 0, d, c), 0) / kand.length;
  }
  vnext(phase, mitte, deckel) {
    const n = this.n, V = new Float64Array(n * 8 * n);
    for (let h = 0; h < n; h++) for (let t = 0; t < n; t++) if (h !== t)
      for (let a = 1; a < 8; a++) V[(h * 8 + a) * n + t] = this.nachRunde(phase, mitte, deckel, h, a, t);
    return V;
  }
  reihenfolge(mitte, deckel, starter) {
    const aktiv = mitte > 0 ? deckel.map((_, i) => i) : deckel.map((_, i) => i).filter(i => deckel[i] > 0);
    const i = aktiv.indexOf(starter);
    return [...aktiv.slice(i), ...aktiv.slice(0, i)];
  }
  folgerVerteilung(L) { return this.F[L].map(r => Float64Array.from(r)); }
}

export class Konter {
  constructor(loesungen) { this.name = "Konter"; this.L = loesungen; }
  tabellen(s) {
    const alle = s.deckel.map(([p]) => p), n = alle.length, ich = s.spieler;
    const rel = new Map(alle.map(p => [p, (alle.indexOf(p) - alle.indexOf(ich) + n) % n]));
    const deckel = Array(n).fill(0);
    for (const [p, d] of s.deckel) deckel[rel.get(p)] = d;
    const L = this.L[n];
    if (!L) throw new Error(`Konter ist für ${n} Spieler nicht berechnet.`);
    const phase = s.haelfte === "Finale" ? "F" : s.haelfte === "Hälfte 2" ? `H2_${rel.get(s.haelftenVerlierer[0])}` : "H1";
    const Vn = L.vnext(phase, s.mitte, deckel);
    const starter = s.istStarter ? ich : s.bisher[0].spieler;
    const reihe = L.reihenfolge(s.mitte, deckel, rel.get(starter));
    const nA = reihe.length;
    // Vnext auf aktive Sitze umrechnen: Vn ist über alle n Sitze indiziert
    const Vs = (h, a, t) => Vn[(h * 8 + a) * n + t];
    const VnAktiv = new Float64Array(nA * 8 * nA);
    for (let i = 0; i < nA; i++) for (let j = 0; j < nA; j++) for (let a = 0; a < 8; a++) VnAktiv[(i * 8 + a) * nA + j] = Vs(reihe[i], a, reihe[j]);
    const sitze = reihe.map((_, i) => i);
    const Uo = U(), Uv = Uh();
    if (s.istStarter) {
      for (let k = 1; k <= 3; k++) {
        const D = [leerD(), ...Array.from({ length: nA - 1 }, () => L.folgerVerteilung(k))];
        for (let w = 0; w < W; w++) { D[0] = leerD(); D[0][w][k] = 1; Uo[w][k] = -erwartung(nA, sitze, D, VnAktiv); }
        for (let h = 0; h < NH; h++) { let x = 0; for (let w = 0; w < W; w++) x += P_VERDECKT[h][w] * Uo[w][k]; Uv[h][k] = x; }
      }
      const { EV } = zugDp(Uo, Uv, 3, true, false);
      return { Uo, Uv, EV, grenze: 3, darf: true, vm: false, umrechnen: q => -q };
    }
    const k1 = s.grenze, p = s.position;
    const D = [];
    s.bisher.forEach(e => {
      const d = leerD();
      if (e.verdeckt) { const pv = P_VERDECKT[hId(e.sichtbar)]; for (let w = 0; w < W; w++) d[w][e.wuerfe] = pv[w]; }
      else d[wId(e.wuerfel, e.ausDerHand)][e.wuerfe] = 1;
      D.push(d);
    });
    D.push(leerD());
    for (let pos = p + 1; pos < nA; pos++) D.push(L.folgerVerteilung(k1));
    for (let k = 1; k <= k1; k++) for (let w = 0; w < W; w++) {
      D[p] = leerD(); D[p][w][k] = 1; Uo[w][k] = -erwartung(nA, sitze, D, VnAktiv);
    }
    if (s.verdecktModus) for (let h = 0; h < NH; h++) { let x = 0; for (let w = 0; w < W; w++) x += P_VERDECKT[h][w] * Uo[w][k1]; Uv[h][k1] = x; }
    const { EV } = zugDp(Uo, Uv, k1, false, s.verdecktModus);
    return { Uo, Uv, EV, grenze: k1, darf: false, vm: s.verdecktModus, umrechnen: q => -q };
  }
  async entscheide(s) { return entscheideAus(this.tabellen(s), s); }
}

// ------------------------------------------------------------------ Berater (Tipps)
export function optionen(bot, s, beschreibe) {
  const t = bot.tabellen(s);
  return legaleAktionen(s).map(a => ({ aktion: a, text: beschreibe(a, s), p: t.umrechnen(aktionsWert(t, s, a)) }))
    .sort((x, y) => x.p - y.p);
}
