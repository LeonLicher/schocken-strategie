// Schocken-Regeln und Spielablauf (Nachbau von schocken/wertung.py und schocken/engine.py).
// Strategien liefern ihre Entscheidung als Promise; so kann ein Mensch per Klick antworten.

export const EINFACH = 0, STRASSE = 1, GENERAL = 2, SCHOCK = 3, SCHOCK_AUS = 4;
export const GESAMT = 13;

export function bewerte(wuerfel, ausDerHand) {
  const w = [...wuerfel].sort((x, y) => y - x);
  const [a, b, c] = w;
  const einsen = w.filter(x => x === 1).length;
  if (einsen === 3) return { klasse: SCHOCK_AUS, schluessel: 0, deckel: GESAMT, name: "Schock Aus" };
  if (einsen === 2) return { klasse: SCHOCK, schluessel: a, deckel: a, name: `Schock ${a}` };
  if (a === b && b === c) return { klasse: GENERAL, schluessel: a, deckel: 3, name: `General ${a}` };
  if (ausDerHand && a - 1 === b && b - 1 === c) return { klasse: STRASSE, schluessel: a, deckel: 2, name: `Straße ${c}-${b}-${a}` };
  return { klasse: EINFACH, schluessel: a * 100 + b * 10 + c, deckel: 1, name: `${a}-${b}-${c}` };
}
export const rang = wt => wt.klasse * 1000 + wt.schluessel;

export const STOPP = Object.freeze({ stopp: true, behalten: [], drehen: 0, verdeckt: false });
export function aktion(behalten = [], drehen = 0, verdeckt = false) {
  return { stopp: false, behalten: [...behalten].sort((x, y) => x - y), drehen, verdeckt };
}
export function gleicheAktion(a, b) {
  if (a.stopp || b.stopp) return a.stopp === b.stopp;
  return a.drehen === b.drehen && a.verdeckt === b.verdeckt &&
    a.behalten.length === b.behalten.length && [...a.behalten].sort().every((x, i) => x === [...b.behalten].sort()[i]);
}

function kombinationen(liste, k) {
  if (k === 0) return [[]];
  const aus = [];
  liste.forEach((x, i) => kombinationen(liste.slice(i + 1), k - 1).forEach(r => aus.push([x, ...r])));
  return aus;
}

export function legaleAktionen(s) {
  if (s.phase === "vor_wurf") return s.istStarter ? [aktion(), aktion([], 0, true)] : [aktion()];
  const rest = s.grenze - s.wurfNr;
  if (rest <= 0) return [STOPP];
  const verdecktOpt = s.istStarter ? [false, true] : [s.verdecktModus && s.wurfNr + 1 === s.grenze];
  const aus = [STOPP];
  const sechsen = s.neu.filter(x => x === 6).length;
  for (let drehen = 0; drehen < 3; drehen++) {
    if (drehen && (sechsen < drehen + 1 || rest < drehen)) continue;
    const pool = [...s.wuerfel];
    for (let i = 0; i < (drehen ? drehen + 1 : 0); i++) pool.splice(pool.indexOf(6), 1);
    pool.sort((x, y) => x - y);
    for (let anzahl = 0; anzahl < 3 - drehen; anzahl++) {
      const gesehen = new Set();
      for (const k of kombinationen(pool, anzahl)) {
        const key = k.join(",");
        if (gesehen.has(key)) continue;
        gesehen.add(key);
        for (const v of verdecktOpt) aus.push(aktion(k, drehen, v));
      }
    }
  }
  return aus;
}

export class RegelVerstoss extends Error {}

function melde(log, ereignis, daten) { if (log && typeof log[ereignis] === "function") log[ereignis](daten); }

export const vergleich = e => [rang(e.wertung), -e.wuerfe, -e.position];
function groesser(a, b) { for (let i = 0; i < 3; i++) { if (a[i] !== b[i]) return a[i] > b[i]; } return false; }

export function oeffentlich(e) { return e.verdeckt ? { ...e, wuerfel: null, ausDerHand: null, wertung: null } : e; }

export async function spieleZug(strategie, spieler, position, grenze, verdecktModus, kontext, rng, log) {
  const istStarter = position === 0;
  if (istStarter) grenze = 3;
  const sicht = (phase, wurfNr, wuerfel, neu) => ({ phase, spieler, position, istStarter, grenze, verdecktModus,
    wurfNr, wuerfel, neu, ...kontext });
  const pruefe = async (s, erzwungen) => {
    let a = await strategie.entscheide(s);
    a = a.stopp ? STOPP : aktion(a.behalten, a.drehen, a.verdeckt);
    if (!istStarter && !a.stopp) a.verdeckt = erzwungen;
    if (!legaleAktionen(s).some(x => gleicheAktion(x, a))) throw new RegelVerstoss(`${strategie.name}: unerlaubte Aktion`);
    return a;
  };
  let verdeckt;
  if (istStarter) {
    const a = await pruefe(sicht("vor_wurf", 0, [], []), false);
    verdeckt = a.verdeckt;
    melde(log, "aktion", { spieler, wurfNr: 0, aktion: a });
  } else {
    verdeckt = verdecktModus && grenze === 1;
  }
  let gehalten = [], wurfNr = 0, neu = [], wuerfel = [];
  for (;;) {
    neu = Array.from({ length: 3 - gehalten.length }, () => 1 + Math.floor(rng() * 6));
    wurfNr++;
    wuerfel = [...gehalten, ...neu];
    melde(log, "wurf", { spieler, wurfNr, gehalten: [...gehalten], neu: verdeckt ? null : [...neu], verdeckt });
    if (verdeckt || wurfNr >= grenze) break;
    const a = await pruefe(sicht("nach_wurf", wurfNr, wuerfel, neu), !istStarter && verdecktModus && wurfNr + 1 === grenze);
    melde(log, "aktion", { spieler, wurfNr, aktion: a });
    if (a.stopp) break;
    gehalten = [...a.behalten, ...Array(a.drehen).fill(1)];
    verdeckt = a.verdeckt;
  }
  const ausDerHand = neu.length === 3;
  const e = { spieler, position, wuerfe: wurfNr, verdeckt, sichtbar: verdeckt ? gehalten : wuerfel, wuerfel, ausDerHand,
              wertung: bewerte(wuerfel, ausDerHand) };
  melde(log, "zugEnde", { ergebnis: oeffentlich(e) });
  return e;
}

export async function spieleRunde(reihenfolge, strategien, kontextBasis, rng, log) {
  const ergebnisse = [];
  let grenze = 3, verdecktModus = false;
  melde(log, "rundeStart", { reihenfolge: [...reihenfolge] });
  for (let position = 0; position < reihenfolge.length; position++) {
    const spieler = reihenfolge[position];
    const kontext = { ...kontextBasis, bisher: ergebnisse.map(oeffentlich), nachMir: reihenfolge.length - position - 1 };
    const e = await spieleZug(strategien[spieler], spieler, position, grenze, verdecktModus, kontext, rng, log);
    if (position === 0) { grenze = e.wuerfe; verdecktModus = e.verdeckt; }
    ergebnisse.push(e);
  }
  let hoch = ergebnisse[0], tief = ergebnisse[0];
  for (const e of ergebnisse) {
    if (groesser(vergleich(e), vergleich(hoch))) hoch = e;
    if (groesser(vergleich(tief), vergleich(e))) tief = e;
  }
  return { ergebnisse, hoch, tief, deckelBewegt: 0 };
}

export async function spieleHaelfte(teilnehmer, starter, strategien, rng, name, log, haelftenVerlierer = []) {
  const deckel = Object.fromEntries(teilnehmer.map(p => [p, 0]));
  let mitte = GESAMT;
  melde(log, "haelfteStart", { name, teilnehmer: [...teilnehmer] });
  for (;;) {
    const aktiv = mitte > 0 ? [...teilnehmer] : teilnehmer.filter(p => deckel[p] > 0);
    const i = aktiv.indexOf(starter);
    const reihe = [...aktiv.slice(i), ...aktiv.slice(0, i)];
    const kontext = { deckel: teilnehmer.map(p => [p, deckel[p]]), mitte, haelfte: name, haelftenVerlierer: [...haelftenVerlierer] };
    const r = await spieleRunde(reihe, strategien, kontext, rng, log);
    const hoch = r.hoch.spieler, tief = r.tief.spieler;
    const vorher = deckel[tief];
    if (r.hoch.wertung.klasse === SCHOCK_AUS) {
      for (const p of teilnehmer) if (p !== tief) { deckel[tief] += deckel[p]; deckel[p] = 0; }
      deckel[tief] += mitte; mitte = 0;
    } else if (mitte > 0) {
      const menge = Math.min(r.hoch.wertung.deckel, mitte);
      mitte -= menge; deckel[tief] += menge;
    } else {
      const menge = Math.min(r.hoch.wertung.deckel, deckel[hoch]);
      deckel[hoch] -= menge; deckel[tief] += menge;
    }
    r.deckelBewegt = deckel[tief] - vorher;
    if (mitte > 0) starter = tief;
    else {
      const meiste = Math.max(...teilnehmer.map(p => deckel[p]));
      const kandidaten = teilnehmer.filter(p => deckel[p] === meiste);
      starter = kandidaten.length === 1 ? kandidaten[0] : kandidaten[Math.floor(rng() * kandidaten.length)];
    }
    melde(log, "runde", { r, deckel: { ...deckel }, mitte, naechster: starter });
    if (deckel[tief] === GESAMT) { melde(log, "haelfteEnde", { name, verlierer: tief }); return tief; }
  }
}

export async function spieleSpiel(strategien, rng, log, starter = null) {
  const alle = strategien.map((_, i) => i);
  if (starter === null) starter = Math.floor(rng() * alle.length);
  const v1 = await spieleHaelfte(alle, starter, strategien, rng, "Hälfte 1", log);
  const v2 = await spieleHaelfte(alle, v1, strategien, rng, "Hälfte 2", log, [v1]);
  if (v1 === v2) return { verlierer: v1, haelften: [v1, v2] };
  const vf = await spieleHaelfte([v1, v2].sort((a, b) => a - b), v2, strategien, rng, "Finale", log, [v1, v2]);
  return { verlierer: vf, haelften: [v1, v2, vf] };
}
