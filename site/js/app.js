// Oberfläche: Einrichtung, Tisch, eigene Züge, Tipps. Das Spiel läuft komplett im Browser.
import { spieleSpiel, legaleAktionen, gleicheAktion } from "./regeln.js";
import { Spiel2 } from "./loeser.js";
import { Stammtisch, Faustregel, Optimal2, Konter, KonterLoesung, optionen } from "./bots.js";

const BOT_NAMEN = { stammtisch: "Stammtisch", konter: "Konter", optimal: "Optimal", faustregel: "Faustregel" };
const BERATER_NAMEN = { optimal: "Optimal (alle spielen perfekt)", konter: "Konter (Gegner spielen Stammtisch)" };
const TEMPO = [["langsam", "Langsam", 1.6], ["normal", "Normal", 1], ["schnell", "Schnell", 0.4], ["sofort", "Sofort", 0]];
const pct = x => (x * 100).toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " %";
const $ = id => document.getElementById(id);

function lies(k, std) { try { return localStorage.getItem(k) ?? std; } catch (e) { return std; } }
function merke(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

let anzahl = Number(lies("anzahl", "3"));
let gegnerTypen = (() => { try { return JSON.parse(lies("gegner", "")); } catch (e) { return null; } })() ||
  ["konter", "stammtisch", "stammtisch", "stammtisch", "stammtisch"];
let tempo = lies("tempo", "normal");
let tippsAn = lies("tipps", "1") === "1";

// ------------------------------------------------------------------ Lösungsdaten
const DATEN = { spiel2: null, konter: {} };
async function ladeDaten() {
  const json = async p => { const r = await fetch(p); if (!r.ok) throw new Error(p); return r.json(); };
  DATEN.spiel2 = new Spiel2(await json("daten/loesung2.json"));
  DATEN.konter[2] = new KonterLoesung(await json("daten/konter2.json"));
  for (const n of [3, 4]) {
    try { DATEN.konter[n] = new KonterLoesung(await json(`daten/konter${n}.json`), DATEN.konter[2]); } catch (e) { /* nicht berechnet */ }
  }
}

function verfuegbar(n) {
  const bots = ["stammtisch", "faustregel"], berater = [];
  if (n === 2) { bots.push("optimal"); berater.push("optimal"); }
  if (DATEN.konter[n]) { bots.push("konter"); berater.push("konter"); }
  return { bots, berater };
}

// ------------------------------------------------------------------ Texte
function aktionText(a, phase, du = true) {
  if (phase === "vor_wurf") return du ? (a.verdeckt ? "Verdeckt würfeln" : "Offen würfeln") : (a.verdeckt ? "würfelt verdeckt" : "würfelt offen");
  if (a.stopp) return du ? "Fertig (stehen lassen)" : "lässt stehen";
  const teile = [];
  if (a.drehen) teile.push(du ? `${a.drehen === 1 ? "6-6" : "6-6-6"} zu ${a.drehen === 1 ? "1" : "1-1"} drehen`
                              : `dreht ${a.drehen === 1 ? "6-6" : "6-6-6"} zu ${a.drehen === 1 ? "1" : "1-1"}`);
  const gehalten = [...a.behalten].sort((x, y) => y - x);
  const neu = 3 - a.behalten.length - a.drehen;
  if (gehalten.length) teile.push((du ? "halten: " : "hält ") + gehalten.join("-"));
  teile.push((du ? `${neu} neu würfeln` : `würfelt ${neu} neu`) + (a.verdeckt ? " (verdeckt)" : ""));
  const t = teile.join(", ");
  return du ? t[0].toUpperCase() + t.slice(1) : t;
}

const ergebnisJson = e => ({ spieler: e.spieler, wuerfe: e.wuerfe, verdeckt: e.verdeckt, sichtbar: e.sichtbar,
  wuerfel: e.wuerfel, wertung: e.wertung ? e.wertung.name : null });

// ------------------------------------------------------------------ Sitzung: Spiel im Browser
class Sitzung {
  constructor(typen, berater) {
    this.ereignisse = [];
    this.offen = null;
    this.beendet = false;
    this.berater = berater === "optimal" ? new Optimal2(DATEN.spiel2) : berater === "konter" ? new Konter(DATEN.konter) : null;
    const sitzung = this;
    const langsam = bot => ({ name: bot.name, async entscheide(s) { await new Promise(r => setTimeout(r, 0)); return bot.entscheide(s); } });
    this.strategien = typen.map(t => {
      if (t === "mensch") return { name: "Du", entscheide: s => sitzung.frage(s) };
      if (t === "stammtisch") return langsam(new Stammtisch());
      if (t === "faustregel") return langsam(new Faustregel());
      if (t === "optimal") return langsam(new Optimal2(DATEN.spiel2));
      return langsam(new Konter(DATEN.konter));
    });
    const zaehler = {};
    this.namen = typen.map(t => {
      if (t === "mensch") return "Du";
      const basis = BOT_NAMEN[t];
      zaehler[basis] = (zaehler[basis] || 0) + 1;
      return typen.filter(x => x === t).length === 1 ? basis : `${basis} ${zaehler[basis]}`;
    });
    this.log = {
      haelfteStart: d => this.melde({ typ: "haelfte_start", name: d.name, teilnehmer: d.teilnehmer }),
      rundeStart: d => this.melde({ typ: "runde_start", reihenfolge: d.reihenfolge }),
      wurf: d => this.melde({ typ: "wurf", spieler: d.spieler, wurf_nr: d.wurfNr, gehalten: d.gehalten, neu: d.neu, verdeckt: d.verdeckt }),
      aktion: d => this.melde({ typ: "aktion", spieler: d.spieler, wurf_nr: d.wurfNr, text: aktionText(d.aktion, d.wurfNr ? "nach_wurf" : "vor_wurf", false) }),
      zugEnde: d => this.melde({ typ: "zug_ende", ergebnis: ergebnisJson(d.ergebnis) }),
      runde: d => this.melde({ typ: "runde_ende", ergebnisse: d.r.ergebnisse.map(ergebnisJson), hoch: d.r.hoch.spieler,
        tief: d.r.tief.spieler, deckel_bewegt: d.r.deckelBewegt, deckel: d.deckel, mitte: d.mitte,
        schock_aus: d.r.hoch.wertung.name === "Schock Aus" }),
      haelfteEnde: d => this.melde({ typ: "haelfte_ende", name: d.name, verlierer: d.verlierer }),
    };
  }
  melde(e) { if (!this.beendet) { this.ereignisse.push(e); neueEreignisse(); } }
  frage(s) {
    return new Promise(resolve => {
      const legal = legaleAktionen(s);
      const offen = { sicht: s, phase: s.phase, wurf_nr: s.wurfNr, wuerfel: s.wuerfel, neu: s.neu, grenze: s.grenze,
        ist_starter: s.istStarter, verdeckt_modus: s.verdecktModus, nach_mir: s.nachMir, legal,
        nummer: this.ereignisse.length, resolve };
      if (this.berater) {
        try { offen.optionen = optionen(this.berater, s, a => aktionText(a, s.phase)); }
        catch (e) { offen.optionen_fehler = String(e); }
      }
      this.offen = offen;
      neueEreignisse();
    });
  }
  async starte() {
    try {
      const e = await spieleSpiel(this.strategien, Math.random, this.log);
      this.melde({ typ: "spiel_ende", verlierer: e.verlierer });
    } catch (e) {
      this.melde({ typ: "fehler", text: String(e) });
    }
  }
  sende(a) {
    const o = this.offen;
    if (!o) return "Gerade ist keine Entscheidung offen.";
    let x = a.stopp ? { stopp: true, behalten: [], drehen: 0, verdeckt: false } : { ...a, behalten: [...a.behalten].sort((p, q) => p - q) };
    if (!o.ist_starter && !x.stopp) x.verdeckt = o.verdeckt_modus && o.wurf_nr + 1 === o.grenze;
    if (!o.legal.some(l => gleicheAktion(l, x))) return "Dieser Zug ist so nicht erlaubt. Es muss mindestens ein Würfel neu geworfen werden, und Sechsen drehen geht nur mit Sechsen aus dem letzten Wurf.";
    this.offen = null;
    o.resolve(x);
    return null;
  }
}

let SITZUNG = null;

// ------------------------------------------------------------------ Würfel zeichnen
function wuerfelSVG(v, groesse = 22, art = "") {
  const r = groesse;
  if (v === null || v === "?") {
    return `<svg width="${r}" height="${r}" viewBox="0 0 30 30" aria-label="verdeckt"><rect x="1" y="1" width="28" height="28" rx="6" style="fill:#2b2b2b;stroke:#000;stroke-width:1.2"/>
      <text x="15" y="21" text-anchor="middle" font-size="16" font-weight="700" style="fill:#d8d8d8">?</text></svg>`;
  }
  const p = { 1: [[2, 2]], 2: [[1, 1], [3, 3]], 3: [[1, 1], [2, 2], [3, 3]], 4: [[1, 1], [3, 1], [1, 3], [3, 3]],
              5: [[1, 1], [3, 1], [2, 2], [1, 3], [3, 3]], 6: [[1, 1], [3, 1], [1, 2], [3, 2], [1, 3], [3, 3]] }[v];
  const gehalten = art === "gehalten";
  const pips = p.map(([x, y]) => `<circle cx="${x * 6 + 3}" cy="${y * 6 + 3}" r="${v === 1 ? 3 : 2.2}" style="fill:${v === 1 ? "#b3261e" : "var(--pip)"}"/>`).join("");
  return `<svg width="${r}" height="${r}" viewBox="0 0 30 30" aria-label="${v}"><rect x="1" y="1" width="28" height="28" rx="6"
    style="fill:var(--wuerfel);stroke:${gehalten ? "var(--accent)" : "#00000055"};stroke-width:${gehalten ? 3 : 1.2}"/>${pips}</svg>`;
}
const wuerfelReihe = (liste, groesse, art) => `<span class="mini">${liste.map(v => wuerfelSVG(v, groesse, art)).join("")}</span>`;

// ------------------------------------------------------------------ Einrichtung
function zeichneEinrichtung() {
  const seg = $("anzahl");
  seg.innerHTML = "";
  for (let n = 2; n <= 6; n++) {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = n; b.setAttribute("aria-pressed", String(n === anzahl));
    b.onclick = () => { anzahl = n; merke("anzahl", n); zeichneEinrichtung(); };
    seg.appendChild(b);
  }
  const v = verfuegbar(anzahl);
  const liste = $("gegner-liste");
  liste.innerHTML = "";
  for (let i = 0; i < anzahl - 1; i++) {
    if (!v.bots.includes(gegnerTypen[i])) gegnerTypen[i] = "stammtisch";
    const box = document.createElement("div");
    box.className = "gegner-wahl";
    const opts = Object.keys(BOT_NAMEN).map(k => `<option value="${k}" ${k === gegnerTypen[i] ? "selected" : ""} ${v.bots.includes(k) ? "" : "disabled"}>${BOT_NAMEN[k]}${v.bots.includes(k) ? "" : " (nicht für " + anzahl + " Spieler)"}</option>`).join("");
    box.innerHTML = `<label class="etikett" for="gegner-${i}">Platz ${i + 2} (nach dir)</label><select id="gegner-${i}">${opts}</select>`;
    box.querySelector("select").onchange = e => { gegnerTypen[i] = e.target.value; merke("gegner", JSON.stringify(gegnerTypen)); };
    liste.appendChild(box);
  }
  const ber = $("berater");
  ber.innerHTML = v.berater.length ? v.berater.map(b => `<option value="${b}">${BERATER_NAMEN[b]}</option>`).join("")
                                   : `<option value="">für ${anzahl} Spieler noch nicht berechnet</option>`;
  ber.disabled = !v.berater.length;
  if (v.berater.includes("konter") && gegnerTypen.slice(0, anzahl - 1).every(t => t === "stammtisch")) ber.value = "konter";
}

function starte() {
  const typen = ["mensch", ...gegnerTypen.slice(0, anzahl - 1)];
  const tipps = $("tipps-start").checked;
  const berater = tipps && !$("berater").disabled ? $("berater").value : null;
  if (SITZUNG) SITZUNG.beendet = true;
  SITZUNG = new Sitzung(typen, berater);
  tippsAn = !!berater;
  $("tipps-an").checked = tippsAn;
  neuerZustand(SITZUNG.namen, berater);
  $("einrichtung").hidden = true;
  $("tisch").hidden = false;
  $("protokoll-box").hidden = false;
  SITZUNG.starte();
}

// ------------------------------------------------------------------ Spielzustand aus Ereignissen
let Z = null;
function neuerZustand(namen, berater) {
  Z = { namen, berater, n: namen.length, gespielt: 0, offen: null,
        spieler: namen.map(() => ({ deckel: 0, wuerfe: [], ergebnis: null, haelften: 0, marke: null, vorText: "" })),
        mitte: 13, phase: "", teilnehmer: [], reihe: [], grenze: 3, vm: false, amZug: null,
        protokoll: [], fehler: [], ende: null, auswahl: [], drehen: 0, tippOffen: false, fehlerListe: [] };
  $("ende").hidden = true;
  $("rueckmeldung").innerHTML = "";
  zeichne();
}

function neueEreignisse() {
  if (!Z || !SITZUNG) return;
  const o = SITZUNG.offen;
  if (o && (!Z.offen || Z.offen !== o)) {
    Z.offen = o; Z.drehen = 0; Z.tippOffen = false;
    const vorher = o.wuerfel.length - o.neu.length;
    Z.auswahl = o.wuerfel.map((_, i) => i < vorher);
  }
  if (!o) Z.offen = null;
  spieleAb();
}

function wende(e) {
  const s = Z.spieler;
  switch (e.typ) {
    case "haelfte_start":
      Z.phase = e.name; Z.teilnehmer = e.teilnehmer; Z.mitte = 13;
      e.teilnehmer.forEach(i => { s[i].deckel = 0; });
      Z.protokoll.unshift({ trenner: true, text: `${e.name} beginnt (${e.teilnehmer.map(i => Z.namen[i]).join(", ")})` });
      break;
    case "runde_start":
      Z.reihe = e.reihenfolge; Z.grenze = 3; Z.vm = false; Z.amZug = null;
      s.forEach(x => { x.wuerfe = []; x.ergebnis = null; x.marke = null; x.vorText = ""; });
      break;
    case "wurf":
      Z.amZug = e.spieler;
      s[e.spieler].wuerfe.push({ nr: e.wurf_nr, gehalten: e.gehalten, neu: e.neu, verdeckt: e.verdeckt, text: "" });
      break;
    case "aktion": {
      const w = s[e.spieler].wuerfe;
      if (e.wurf_nr === 0) s[e.spieler].vorText = e.text;
      else if (w.length) w[w.length - 1].text = e.text;
      break;
    }
    case "zug_ende":
      s[e.ergebnis.spieler].ergebnis = e.ergebnis;
      if (e.ergebnis.spieler === Z.reihe[0]) { Z.grenze = e.ergebnis.wuerfe; Z.vm = e.ergebnis.verdeckt; }
      break;
    case "runde_ende": {
      e.ergebnisse.forEach(r => { s[r.spieler].ergebnis = r; });
      s[e.hoch].marke = "hoch"; s[e.tief].marke = "tief";
      Object.entries(e.deckel).forEach(([i, d]) => { s[Number(i)].deckel = d; });
      Z.mitte = e.mitte; Z.amZug = null;
      const hochE = e.ergebnisse.find(r => r.spieler === e.hoch), tiefE = e.ergebnisse.find(r => r.spieler === e.tief);
      const wer = e.tief === 0 ? "Du bekommst" : `${Z.namen[e.tief]} bekommt`;
      Z.protokoll.unshift({ text: `Hoch: ${Z.namen[e.hoch]} (${hochE.wertung}), tief: ${Z.namen[e.tief]} (${tiefE.wertung}). ` +
        (e.schock_aus ? `Schock Aus! ${wer} alle Deckel.` : `${wer} ${e.deckel_bewegt} Deckel.`) });
      break;
    }
    case "haelfte_ende":
      s[e.verlierer].haelften += 1;
      Z.protokoll.unshift({ trenner: true, text: `${Z.namen[e.verlierer]} ${e.verlierer === 0 ? "verlierst" : "verliert"} ${e.name}.` });
      break;
    case "spiel_ende": Z.ende = e; break;
    case "fehler": Z.fehler.push(e.text); break;
  }
}

function pause(e) {
  const f = TEMPO.find(t => t[0] === tempo)[2];
  if (f === 0) return 0;
  const eigen = e.spieler === 0 || (e.ergebnis && e.ergebnis.spieler === 0);
  const basis = { wurf: 650, aktion: 500, zug_ende: 250, runde_ende: 1600, runde_start: 250, haelfte_start: 900, haelfte_ende: 1400 }[e.typ] || 0;
  return (eigen && e.typ !== "runde_ende" ? 120 : basis) * f;
}

let spielt = false;
async function spieleAb() {
  if (spielt) return;
  spielt = true;
  while (Z && SITZUNG && Z.gespielt < SITZUNG.ereignisse.length) {
    const e = SITZUNG.ereignisse[Z.gespielt];
    wende(e);
    Z.gespielt++;
    zeichne();
    const ms = pause(e);
    if (ms) await new Promise(r => setTimeout(r, ms));
  }
  spielt = false;
  zeichne();
}

// ------------------------------------------------------------------ Zeichnen
function zeichne() {
  if (!Z) return;
  $("phase").textContent = Z.phase || "Gleich geht's los";
  $("mitte-zahl").textContent = Z.mitte;
  $("mitte-deckel").innerHTML = Array.from({ length: Z.mitte }, () => `<span class="deckel"></span>`).join("");
  const starter = Z.reihe.length ? Z.namen[Z.reihe[0]] : "";
  const starterFertig = Z.reihe.length && Z.spieler[Z.reihe[0]].ergebnis;
  $("regelzeile").innerHTML = Z.reihe.length
    ? `Es beginnt <b>${starter}</b>. ` + (starterFertig ? `Höchstens <b>${Z.grenze}</b> ${Z.grenze === 1 ? "Wurf" : "Würfe"}${Z.vm ? ", der letzte <b>verdeckt</b>" : ""}.` : "Der Startspieler legt die Wurfzahl fest.")
    : "";

  $("spieler").innerHTML = Z.namen.map((name, i) => {
    const s = Z.spieler[i];
    const imSpiel = Z.teilnehmer.includes(i), aktiv = Z.reihe.includes(i);
    const marken = [];
    if (Z.reihe[0] === i) marken.push(`<span class="marke">beginnt</span>`);
    if (s.marke === "hoch") marken.push(`<span class="marke hoch">hoch</span>`);
    if (s.marke === "tief") marken.push(`<span class="marke tief">tief</span>`);
    if (s.haelften) marken.push(`<span class="marke">${s.haelften}× Hälfte verloren</span>`);
    if (!imSpiel && Z.phase) marken.push(`<span class="marke">nicht im Finale</span>`);
    else if (!aktiv && Z.reihe.length) marken.push(`<span class="marke">raus (keine Deckel)</span>`);
    const wuerfe = s.wuerfe.map(w => `<div class="wurf-zeile"><span class="wurf-nr">${w.nr}.</span>
        ${w.gehalten.length ? wuerfelReihe(w.gehalten, 20, "gehalten") : ""}${wuerfelReihe(w.verdeckt ? Array(3 - w.gehalten.length).fill(null) : w.neu, 20)}
        <span class="wurf-text">${w.text}</span></div>`).join("");
    let erg = "";
    if (s.ergebnis) {
      const e = s.ergebnis;
      erg = e.wertung ? `<div class="ergebnis">${e.verdeckt && e.wuerfel ? wuerfelReihe([...e.wuerfel].sort((a, b) => b - a), 20) + " " : ""}${e.wertung} · ${e.wuerfe} ${e.wuerfe === 1 ? "Wurf" : "Würfe"}${e.verdeckt ? " · war verdeckt" : ""}</div>`
                      : `<div class="ergebnis">verdeckt nach ${e.wuerfe} ${e.wuerfe === 1 ? "Wurf" : "Würfen"}</div>`;
    }
    return `<article class="spieler ${Z.amZug === i ? "dran" : ""} ${(!imSpiel && Z.phase) || (!aktiv && Z.reihe.length) ? "raus" : ""}">
      <div class="spieler-kopf"><span class="spieler-name">${name}</span><span class="zahl-deckel" title="Deckel">${s.deckel}</span></div>
      <div class="stapel-deckel">${Array.from({ length: s.deckel }, () => `<span class="deckel"></span>`).join("")}</div>
      <div class="marken">${marken.join("")}</div>
      <div class="wuerfe">${s.vorText && s.wuerfe.length && s.wuerfe[0].verdeckt ? `<div class="wurf-text">${s.vorText}</div>` : ""}${wuerfe}${erg}</div>
    </article>`;
  }).join("");

  $("protokoll").innerHTML = Z.protokoll.map(p => `<li class="${p.trenner ? "trenner" : ""}">${p.text}</li>`).join("");
  zeichneAktion();
  zeichneEnde();
}

const legalHat = pred => Z.offen.legal.some(pred);
function gleich(a, b, starter) {
  if (a.stopp || b.stopp) return !!a.stopp === !!b.stopp;
  const s = x => [...x].sort().join(",");
  return s(a.behalten) === s(b.behalten) && a.drehen === b.drehen && (!starter || !!a.verdeckt === !!b.verdeckt);
}

function zeichneAktion() {
  const box = $("aktion");
  const o = Z.offen;
  const zeigen = o && Z.gespielt >= o.nummer && !spielt;
  box.hidden = !zeigen;
  if (!zeigen) return;
  const grosse = $("grosse-wuerfel"), drehReihe = $("dreh-reihe"), knoepfe = $("knopf-reihe");
  $("aktion-meldung").textContent = "";
  if (o.phase === "vor_wurf") {
    $("aktion-titel").textContent = "Du beginnst die Runde";
    $("aktion-info").textContent = "Du legst fest, wie oft alle würfeln dürfen. Verdeckt heißt: Niemand sieht den Wurf, auch du nicht.";
    grosse.innerHTML = ""; drehReihe.innerHTML = "";
    knoepfe.innerHTML = `<button class="knopf haupt gross" type="button" id="k-offen">Würfeln</button>
      <button class="knopf gross" type="button" id="k-verdeckt">Verdeckt würfeln</button>`;
    $("k-offen").onclick = () => sende({ stopp: false, behalten: [], drehen: 0, verdeckt: false });
    $("k-verdeckt").onclick = () => sende({ stopp: false, behalten: [], drehen: 0, verdeckt: true });
    zeichneTipp();
    return;
  }
  const vorher = o.wuerfel.length - o.neu.length;
  const rest = o.grenze - o.wurf_nr;
  const erzwungen = !o.ist_starter && o.verdeckt_modus && o.wurf_nr + 1 === o.grenze;
  $("aktion-titel").textContent = `Dein ${o.wurf_nr}. Wurf`;
  $("aktion-info").textContent = o.ist_starter ? `Du beginnst: noch bis zu ${rest} ${rest === 1 ? "Wurf" : "Würfe"}.`
    : `Noch ${rest} ${rest === 1 ? "Wurf" : "Würfe"} erlaubt${erzwungen ? ", der nächste muss verdeckt sein" : ""}. Nach dir: ${o.nach_mir}.`;
  const sechsenNeu = o.wuerfel.map((v, i) => (i >= vorher && v === 6 ? i : -1)).filter(i => i >= 0);
  const verbraucht = Z.drehen ? sechsenNeu.slice(0, Z.drehen + 1) : [];
  grosse.innerHTML = o.wuerfel.map((v, i) => {
    const weg = verbraucht.includes(i), gedreht = weg && verbraucht.indexOf(i) < Z.drehen, an = !weg && Z.auswahl[i];
    const unter = weg ? (gedreht ? "→ wird zur 1" : "zurück in den Becher") : (an ? "liegen lassen" : (i < vorher ? "lag schon" : "neu"));
    return `<button class="wuerfel-knopf" type="button" data-i="${i}" aria-pressed="${an || gedreht}" ${weg ? "disabled" : ""}>
      ${wuerfelSVG(gedreht ? 1 : v, 64, an || gedreht ? "gehalten" : "")}<span class="unter">${unter}</span></button>`;
  }).join("");
  grosse.querySelectorAll(".wuerfel-knopf").forEach(b => b.onclick = () => { const i = Number(b.dataset.i); Z.auswahl[i] = !Z.auswahl[i]; zeichneAktion(); });
  const drehOpt = [1, 2].filter(t => legalHat(a => a.drehen === t));
  drehReihe.innerHTML = drehOpt.length ? `<span class="leise">Sechsen drehen:</span>` + drehOpt.map(t =>
    `<button class="knopf" type="button" data-t="${t}" aria-pressed="${Z.drehen === t}">${t === 1 ? "6-6 → eine 1" : "6-6-6 → zwei 1en"}</button>`).join("") : "";
  drehReihe.querySelectorAll("button").forEach(b => b.onclick = () => { const t = Number(b.dataset.t); Z.drehen = Z.drehen === t ? 0 : t; zeichneAktion(); });
  const weiter = rest > 0;
  knoepfe.innerHTML = `<button class="knopf gross" type="button" id="k-fertig">Fertig (stehen lassen)</button>` +
    (weiter ? `<button class="knopf haupt gross" type="button" id="k-weiter">${erzwungen ? "Würfeln (verdeckt, Pflicht)" : "Würfeln"}</button>` : "") +
    (weiter && o.ist_starter ? `<button class="knopf gross" type="button" id="k-weiter-v">Verdeckt würfeln</button>` : "");
  $("k-fertig").onclick = () => sende({ stopp: true, behalten: [], drehen: 0, verdeckt: false });
  const auswahl = verdeckt => {
    const behalten = o.wuerfel.filter((v, i) => Z.auswahl[i] && !verbraucht.includes(i));
    if (behalten.length + Z.drehen > 2) { $("aktion-meldung").textContent = "Mindestens ein Würfel muss neu geworfen werden. Lass höchstens zwei liegen."; return; }
    sende({ stopp: false, behalten, drehen: Z.drehen, verdeckt });
  };
  if (weiter) $("k-weiter").onclick = () => auswahl(erzwungen);
  if (weiter && o.ist_starter) $("k-weiter-v").onclick = () => auswahl(true);
  zeichneTipp();
}

function zeichneTipp() {
  const box = $("tipp-box");
  const o = Z.offen;
  if (!tippsAn || !o.optionen) { box.innerHTML = o && o.optionen_fehler ? `<div class="tipp leise">Tipp nicht verfügbar.</div>` : ""; return; }
  if (!Z.tippOffen) {
    box.innerHTML = `<button class="knopf" type="button" id="k-tipp">Tipp zeigen</button>`;
    $("k-tipp").onclick = () => { Z.tippOffen = true; zeichneTipp(); };
    return;
  }
  const beste = o.optionen[0].p;
  box.innerHTML = `<div class="tipp"><b>Deine Chance zu verlieren je Möglichkeit</b> (${BERATER_NAMEN[Z.berater]}):<ol>` +
    o.optionen.slice(0, 6).map(x => `<li>${x.text}: ${pct(x.p)}${x.p - beste > 0.0005 ? ` <span class="leise">(+${((x.p - beste) * 100).toFixed(1)} Pkt.)</span>` : " <b>beste</b>"}</li>`).join("") + "</ol></div>";
}

function sende(aktion) {
  const o = Z.offen;
  const fehler = SITZUNG.sende(aktion);
  if (fehler) { $("aktion-meldung").textContent = fehler; return; }
  Z.offen = null;
  if (tippsAn && o.optionen) {
    const gewaehlt = o.optionen.find(x => gleich(x.aktion, aktion, o.ist_starter));
    const beste = o.optionen[0];
    if (gewaehlt) {
      const kosten = gewaehlt.p - beste.p;
      const situation = o.phase === "vor_wurf" ? "Vor dem 1. Wurf" : `Wurf ${o.wurf_nr}: ${[...o.wuerfel].sort((a, b) => b - a).join("-")}`;
      if (kosten > 0.0005) Z.fehlerListe.push({ situation, gewaehlt: gewaehlt.text, beste: beste.text, kosten, phase: Z.phase, stand: Z.spieler.map(s => s.deckel).join(":") });
      $("rueckmeldung").innerHTML = kosten > 0.0005
        ? `<div class="rueckmeldung teuer">Besser wäre gewesen: <b>${beste.text}</b>. Deine Wahl (${gewaehlt.text}) kostet ${(kosten * 100).toFixed(1)} Prozentpunkte Verlustchance (${pct(gewaehlt.p)} statt ${pct(beste.p)}).</div>`
        : `<div class="rueckmeldung">Gute Wahl: ${gewaehlt.text}. Deine Chance zu verlieren: ${pct(gewaehlt.p)}.</div>`;
    }
  }
  zeichne();
}

function zeichneEnde() {
  const box = $("ende");
  if (!Z.ende || spielt || Z.gespielt < SITZUNG.ereignisse.length) { box.hidden = true; return; }
  box.hidden = false;
  const v = Z.ende.verlierer;
  const fehler = [...Z.fehlerListe].sort((a, b) => b.kosten - a.kosten).slice(0, 6);
  box.innerHTML = `<h2>${v === 0 ? "Du hast verloren und zahlst die Runde." : `${Z.namen[v]} hat verloren und zahlt die Runde.`}</h2>` +
    (tippsAn ? (fehler.length ? `<p>Deine teuersten Entscheidungen:</p><div class="tabelle-box"><table><tr><th>Lage</th><th>Deine Wahl</th><th>Besser</th><th>Kosten</th></tr>` +
      fehler.map(f => `<tr><td>${f.phase}, Deckel ${f.stand}<br>${f.situation}</td><td>${f.gewaehlt}</td><td>${f.beste}</td><td>${(f.kosten * 100).toFixed(1)} Pkt.</td></tr>`).join("") + `</table></div>`
      : `<p>Keine einzige teure Entscheidung. Stark gespielt.</p>`) : "") +
    `<div><button class="knopf haupt" type="button" id="k-nochmal">Nochmal</button></div>`;
  $("k-nochmal").onclick = starte;
  if (Z.fehler.length) box.innerHTML += `<p class="meldung">Fehler: ${Z.fehler.join("; ")}</p>`;
}

// ------------------------------------------------------------------ Start
(function () {
  const seg = $("tempo");
  for (const [k, text] of TEMPO) {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = text; b.setAttribute("aria-pressed", String(k === tempo));
    b.onclick = () => { tempo = k; merke("tempo", k); seg.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); };
    seg.appendChild(b);
  }
  const t = $("tipps-an");
  t.checked = tippsAn;
  t.onchange = () => { tippsAn = t.checked; merke("tipps", tippsAn ? "1" : "0"); if (Z) zeichne(); };
  $("neu-knopf").onclick = () => { $("einrichtung").hidden = false; $("einrichtung").scrollIntoView({ behavior: "smooth" }); };
  $("start-knopf").onclick = starte;
  ladeDaten().then(() => {
    $("lade-hinweis").hidden = true;
    $("start-knopf").disabled = false;
    zeichneEinrichtung();
  }).catch(e => { $("lade-hinweis").textContent = "Lösungsdaten konnten nicht geladen werden: " + e.message; });
})();
