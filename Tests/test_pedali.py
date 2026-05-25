import os
import sys
import unittest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Models.pedali import PedaleDistorsione, PedaleDelay, PedaleChorus 

class TestPedali(unittest.TestCase):

    def setUp(self):
        # Fase 1 - Arrange
        self.distorsione = PedaleDistorsione(posizione=1, gain=2.0)
        self.delay = PedaleDelay(posizione=2, tempo=500)
        self.chorus = PedaleChorus(posizione=3)
        
        # Segnale di test (campioni tra -1.0 e 1.0)
        self.segnale_iniziale = [0.1, 0.5, -0.3, 0.0]

    def test_toggle_bypass(self):
        self.assertFalse(self.distorsione.bypass)
        self.distorsione.toggle_bypass()
        self.assertTrue(self.distorsione.bypass)

    def test_imposta_parametri(self):
        nuovi_parametri = {"gain": 3.0}
        self.distorsione.imposta_parametri(nuovi_parametri)
        self.assertEqual(self.distorsione.parametri["gain"], 3.0)

    def test_distorsione_applica_effetto_reale(self):
        # Nel nostro pedali.py la formula è: s * (gain * 10) con clipping a 1.0
        # Quindi 0.1 * (2.0 * 10) = 2.0 -> Clip a 1.0
        risultato = self.distorsione.applica_effetto(self.segnale_iniziale)
        
        self.assertIsInstance(risultato, list)
        # Verifichiamo il clipping: 0.1 * 20 = 2.0, deve essere tagliato a 1.0
        self.assertEqual(risultato[0], 1.0) 
        self.assertEqual(risultato[1], 1.0) # Anche 0.5 * 20 viene clippato a 1.0

    def test_delay_applica_effetto_reale(self):
        # Il codice DSP di PedaleDelay aggiunge una coda per l'eco
        # basata su 44100Hz. Calcoliamo la lunghezza attesa esatta:
        tempo_ms = self.delay.parametri.get("tempo", 500.0)
        ritardo_campioni = int((tempo_ms / 1000.0) * 44100)
        lunghezza_attesa = len(self.segnale_iniziale) + (ritardo_campioni * 4)
        
        risultato = self.delay.applica_effetto(self.segnale_iniziale)
        
        # Verifichiamo che la lunghezza dell'array generato corrisponda alla matematica del pedale
        self.assertEqual(len(risultato), lunghezza_attesa)
        
        # Verifichiamo che i primi 4 campioni siano identici all'originale (il suono "Dry" prima dell'eco)
        self.assertEqual(risultato[0:len(self.segnale_iniziale)], self.segnale_iniziale)

    def test_bypass_restituisce_originale(self):
        self.distorsione.toggle_bypass() # Attiviamo il bypass
        risultato = self.distorsione.applica_effetto(self.segnale_iniziale)
        # In bypass il segnale deve essere identico
        self.assertEqual(risultato, self.segnale_iniziale)

if __name__ == "__main__":
    unittest.main()