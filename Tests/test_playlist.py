# Tests/test_playlist.py
import unittest
from Models.playlist import Playlist

class TestPlaylistEntity(unittest.TestCase):
    def setUp(self):
        #Metodo eseguito prima di ogni singolo test per preparare i dati
        self.playlist_test = Playlist(nome_playlist="SuperHits", proprietario="Edoardo")

    def test_costruttore_e_getter(self):
        #Verifica che l'oggetto sia istanziato correttamente con i valori giusti
        self.assertEqual(self.playlist_test.getNomePlaylist(), "SuperHits")
        self.assertEqual(self.playlist_test.getProprietario(), "Edoardo")
        self.assertEqual(len(self.playlist_test.getTracce()), 0) # All'inizio deve essere vuota

    def test_aggiungi_traccia_successo_e_duplicato(self):
        #Verifica l'inserimento di tracce e il blocco dei duplicati
        path = "C:/musica/brano1.wav"
        
        # Primo inserimento -> deve riuscire (True)
        self.assertTrue(self.playlist_test.aggiungiTraccia(path))
        self.assertIn(path, self.playlist_test.getTracce())
        self.assertEqual(len(self.playlist_test.getTracce()), 1)
        
        # Secondo inserimento dello STESSO percorso -> deve fallire (False)
        self.assertFalse(self.playlist_test.aggiungiTraccia(path))
        self.assertEqual(len(self.playlist_test.getTracce()), 1) # La dimensione non deve cambiare

    def test_rimuovi_traccia(self):
        #Verifica la corretta cancellazione di un percorso esistente
        path = "C:/musica/brano_da_cancellare.wav"
        self.playlist_test.aggiungiTraccia(path)
        
        # Rimozione di un brano esistente -> True
        self.assertTrue(self.playlist_test.rimuoviTraccia(path))
        self.assertNotIn(path, self.playlist_test.getTracce())
        
        # Rimozione di un brano NON esistente -> False
        self.assertFalse(self.playlist_test.rimuoviTraccia("percorso_inventato.wav"))

    def test_serializzazione_dizionari(self):
        #Verifica che i metodi toDict e fromDict preservino l'integrità dei dati
        self.playlist_test.aggiungiTraccia("path/1.wav")
        self.playlist_test.aggiungiTraccia("path/2.wav")
        
        # Trasformazione in dizionario
        dizionario_generato = self.playlist_test.toDict()
        self.assertEqual(dizionario_generato["nome_playlist"], "SuperHits")
        self.assertEqual(dizionario_generato["proprietario"], "Edoardo")
        
        # Ricostruzione dall'oggetto partendo dal dizionario
        playlist_ricostruita = Playlist.fromDict(dizionario_generato)
        self.assertEqual(playlist_ricostruita.getNomePlaylist(), "SuperHits")
        self.assertEqual(playlist_ricostruita.getProprietario(), "Edoardo")
        self.assertEqual(len(playlist_ricostruita.getTracce()), 2)
        self.assertIn("path/1.wav", playlist_ricostruita.getTracce())

if __name__ == '__main__':
    unittest.main()