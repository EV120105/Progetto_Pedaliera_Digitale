import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.utente import UtenteAutenticato

class TestUtente(unittest.TestCase):

    def setUp(self):
        #Arrange: Eseguito in automatico prima di ogni test
        self.utente = UtenteAutenticato("Edoardo", "hash_segreto", "edoardo@email.com", "Avanzato")

    def test_getNomeUtente(self):
        self.assertEqual(self.utente.getNomeUtente(), "Edoardo")

    def test_getLivello(self):
        self.assertEqual(self.utente.getLivello(), "Avanzato")
        
    def test_isAutenticato(self):
        # Visto che eredita dalla classe astratta Utente, verifichiamo il polimorfismo
        self.assertTrue(self.utente.isAutenticato())

    def test_toDict(self):
        d = self.utente.toDict()
        self.assertEqual(d["nome_utente"], "Edoardo")
        self.assertEqual(d["hash_password"], "hash_segreto")
        self.assertEqual(d["email"], "edoardo@email.com")

    def test_fromDict(self):
        d = {
            "nome_utente": "Mario", 
            "hash_password": "new_hash", 
            "email": "mario@email.com", 
            "livello": "Principiante"
        }
        nuovo_utente = UtenteAutenticato.fromDict(d)
        self.assertEqual(nuovo_utente.getNomeUtente(), "Mario")
        self.assertEqual(nuovo_utente.getEmail(), "mario@email.com")

if __name__ == "__main__":
    unittest.main()