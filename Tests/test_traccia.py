import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.traccia import TracciaAudio
class TestTracciaAudio(unittest.TestCase):
    def setUp(self):
        #Preparo una traccia "finta" per il test
        self.traccia=TracciaAudio(".mp3", 215.5, "Stairway to Heaven", "Led Zeppelin", "C:/musica/stairway.mp3")
    def testGetters(self):
        self.assertEqual(self.traccia.getFormato(), ".mp3")
        self.assertEqual(self.traccia.getDurata(), 215.5)
        self.assertEqual(self.traccia.getTitolo(), "Stairway to Heaven")
        self.assertEqual(self.traccia.getArtista(), "Led Zeppelin")
        self.assertEqual(self.traccia.getPercorso(), "C:/musica/stairway.mp3")
    def test_toDict(self):
        d=self.traccia.toDict()
        self.assertEqual(d["formato"], ".mp3")
        self.assertEqual(d["durata"], 215.5)
        self.assertEqual(d["titolo"], "Stairway to Heaven")
        self.assertEqual(d["artista"], "Led Zeppelin")
        self.assertEqual(d["percorso"], "C:/musica/stairway.mp3")
    def test_fromDict(self):
        #Prepariamo un dizionario finto (come se arrivasse dal JSON)
        dati_json = {
            "formato":".wav",
            "durata":120.0, 
            "titolo":"Suono Pioggia",
            "artista":"Sconosciuto",
            "percorso":"C:/effetti/pioggia.wav"
        }
        t=self.traccia.fromDict(dati_json)
        #Ora eseguiamo il test 
        self.assertEqual(t.getFormato(), ".wav")
        self.assertEqual(t.getDurata(), 120.0)
        self.assertEqual(t.getTitolo(), "Suono Pioggia")
        self.assertEqual(t.getArtista(), "Sconosciuto")
        self.assertEqual(t.getPercorso(), "C:/effetti/pioggia.wav")

if __name__ == "__main__":
    unittest.main()