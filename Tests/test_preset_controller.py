import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock
from Controller.preset_controller import PresetController
from Models.pedali import PedaleDistorsione

class TestPresetController(unittest.TestCase):
    def setUp(self):
        self.mock_catena_repo = MagicMock()
        self.mock_preset_repo = MagicMock()
        self.controller = PresetController(self.mock_catena_repo, self.mock_preset_repo)

    def test_salva_attuale_come_preset(self):
        #Arrange: creiamo un pedale finto nella catena
        pedale = PedaleDistorsione(posizione=0, gain=1.5)
        self.mock_catena_repo.get_tutti_i_pedali.return_value = [pedale]

        #Act   
        self.controller.salva_attuale_come_preset("RockPreset")

        # Assert
        self.assertTrue(self.mock_preset_repo.crea_preset.called)
        
        # Recuperiamo gli argomenti passati alla chiamata
        args, kwargs = self.mock_preset_repo.crea_preset.call_args
        nome_salvato = args[0]
        dati_salvati = args[1]
        
        self.assertEqual(nome_salvato, "RockPreset")
        self.assertEqual(dati_salvati[0]["tipo"], "Distorsione")
        self.assertEqual(dati_salvati[0]["parametri"]["gain"], 1.5)

    def test_carica_preset_successo(self):
        # Arrange: dati finti che simulano il JSON dei preset
        dati_preset = [{
            "tipo": "Distorsione",
            "posizione": 0,
            "parametri": {"gain": 2.5},
            "bypass": False
        }]
        self.mock_preset_repo.get_preset.return_value = dati_preset

        # Act
        risultato = self.controller.carica_preset("RockPreset")

        # Assert: Il messaggio nel Controller ora include il nome del preset
        messaggio_atteso = "EsitoSuccesso: Preset 'RockPreset' caricato correttamente."
        self.assertEqual(risultato, messaggio_atteso)
        
        # Verifichiamo che la factory abbia creato il pedale e lo abbia aggiunto alla catena
        self.assertTrue(self.mock_catena_repo.aggiungi_o_aggiorna.called)
        
        pedale_creato = self.mock_catena_repo.aggiungi_o_aggiorna.call_args[0][0]
        self.assertEqual(pedale_creato.tipo, "Distorsione")
        self.assertEqual(pedale_creato.parametri["gain"], 2.5)

if __name__ == "__main__":
    unittest.main()