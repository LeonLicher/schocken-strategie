"""Spielt über die HTTP-Schnittstelle ein komplettes Spiel (Mensch wählt immer die erste erlaubte Aktion)."""

import json
import os
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from schocken.web import server


class TestWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.url = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def anfrage(self, pfad, daten=None):
        req = urllib.request.Request(self.url + pfad, data=json.dumps(daten).encode() if daten is not None else None,
                                     method="POST" if daten is not None else "GET")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def spiele_durch(self, spieler, berater):
        code, d = self.anfrage("/api/start", {"spieler": spieler, "tipps": True, "berater": berater})
        self.assertEqual(code, 200, d)
        ab, typen, ende = 0, set(), None
        frist = time.time() + 120
        while time.time() < frist:
            _, z = self.anfrage(f"/api/zustand?ab={ab}")
            self.assertIsNone(z["fehler"])
            for e in z["ereignisse"]:
                typen.add(e["typ"])
                if e["typ"] == "spiel_ende":
                    ende = e
            ab = z["anzahl"]
            if ende:
                break
            o = z["offen"]
            if o:
                if berater:
                    self.assertTrue(o.get("optionen"), o.get("optionen_fehler"))
                code, d = self.anfrage("/api/aktion", o["legal"][-1])
                self.assertEqual(code, 200, d)
        self.assertIsNotNone(ende, "Spiel nicht beendet")
        self.assertTrue({"haelfte_start", "runde_start", "wurf", "aktion", "zug_ende", "runde_ende"} <= typen)

    def test_zu_zweit_gegen_optimal_mit_tipps(self):
        self.spiele_durch(["mensch", "optimal"], "optimal")

    def test_zu_dritt_gegen_stammtisch(self):
        self.spiele_durch(["mensch", "stammtisch", "faustregel"], None)

    def test_unerlaubter_zug(self):
        self.anfrage("/api/start", {"spieler": ["mensch", "stammtisch"], "tipps": False})
        for _ in range(100):
            _, z = self.anfrage("/api/zustand?ab=0")
            if z["offen"] and z["offen"]["phase"] == "nach_wurf":
                code, d = self.anfrage("/api/aktion", {"stopp": False, "behalten": z["offen"]["wuerfel"], "drehen": 0})
                self.assertEqual(code, 400)
                self.assertIn("nicht erlaubt", d["fehler"])
                return
            if z["offen"]:
                self.anfrage("/api/aktion", z["offen"]["legal"][0])
            time.sleep(0.02)
        self.fail("keine Wurf-Entscheidung erreicht")


if __name__ == "__main__":
    unittest.main()
