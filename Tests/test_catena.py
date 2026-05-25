import unittest
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.pedali import PedaleDistorsione, PedaleChorus
from Repos.catena_effetti_repository import catena_effetti
from Controller.gestore_catena import CatenaController

class TestCatenaEffetti(unittest.TestCase):

    def setUp(self):
        #Setup dell'ambiente di test
        self.nome_file_test = "test_catena_temp.json"
        self.repo = catena_effetti(storage_path=self.nome_file_test)
        self.controller = CatenaController(self.repo)
        
        # Creiamo un pedale di prova
        self.distorsione = PedaleDistorsione(posizione=0, gain=0.5)

    def tearDown(self):
        #Pulizia dopo ogni test: eliminiamo il file JSON creato
        if os.path.exists(self.nome_file_test):
            os.remove(self.nome_file_test)

    def test_aggiunta_pedale_e_json(self):
        #Verifica che aggiungendo un pedale, venga salvato nel JSON
        self.repo.aggiungi_o_aggiorna(self.distorsione, 0)
        
        # Verifichiamo che esista il file
        self.assertTrue(os.path.exists(self.nome_file_test))
        
        # Leggiamo il file per vedere se i dati sono corretti
        with open(self.nome_file_test, 'r') as f:
            data = json.load(f)
            self.assertEqual(data[0]["tipo"], "Distorsione")
            self.assertEqual(data[0]["parametri"]["gain"], 0.5)

    def test_validazione_controller_successo(self):
        #Test Sequenza Principale: Modifica valida del gain
        self.repo.aggiungi_o_aggiorna(self.distorsione, 0)
        
        # Modifichiamo il gain a 0.8 tramite controller
        self.controller.set_parametro_pedale(0, {"gain": 0.8})
        
        # Verifichiamo che il valore sia cambiato
        self.assertEqual(self.distorsione.parametri["gain"], 0.8)

    def test_validazione_controller_errore(self):
        #Test Sequenza Alternativa: Valore fuori scala (Gain > 1.0)
        self.repo.aggiungi_o_aggiorna(self.distorsione, 0)
        
        # Proviamo a mettere gain 5.0 (il limite è 1.0)
        self.controller.set_parametro_pedale(0, {"gain": 5.0})
        
        # Verifichiamo che il valore sia stato ripristinato a 0.5
        self.assertEqual(self.distorsione.parametri["gain"], 0.5)

    def test_bypass_toggle(self):
        #Verifica il corretto funzionamento del Bypass (Acceso/Spento)
        # Di default è acceso (bypass=False)
        self.assertFalse(self.distorsione.bypass)
        
        # Spegniamo
        self.distorsione.toggle_bypass()
        self.assertTrue(self.distorsione.bypass)
        
        # Riaccendiamo
        self.distorsione.toggle_bypass()
        self.assertFalse(self.distorsione.bypass)

    def test_scambio_pedali(self):
        #Verifica lo swap di posizione tra due pedali nella lista
        chorus = PedaleChorus(posizione=1, rate=1.0)
        self.repo.aggiungi_o_aggiorna(self.distorsione, 0)
        self.repo.aggiungi_o_aggiorna(chorus, 1)
        
        # Swap manuale (come fatto nel main)
        self.repo.pedali_attivi[0], self.repo.pedali_attivi[1] = \
            self.repo.pedali_attivi[1], self.repo.pedali_attivi[0]
            
        self.assertEqual(self.repo.get_pedale(0).tipo, "Chorus")
        self.assertEqual(self.repo.get_pedale(1).tipo, "Distorsione")

if __name__ == "__main__":
    unittest.main()