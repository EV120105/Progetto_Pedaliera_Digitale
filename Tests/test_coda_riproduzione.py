import unittest
from unittest.mock import patch

# Assicurati di importare la classe dal percorso corretto del tuo progetto
from Models.coda_riproduzione import CodaRiproduzione 

class TestCodaRiproduzione(unittest.TestCase):

    def setUp(self):
        # Setup globale eseguito automaticamente prima di OGNI singolo test
        # Ci garantisce di partire sempre con una coda standard pre-popolata
        self.coda = CodaRiproduzione()
        self.coda.aggiungiTraccia("t1")
        self.coda.aggiungiTraccia("t2")
        self.coda.aggiungiTraccia("t3")

    def testInizializzazioneDefault(self):
        # Verifico i valori di default creando un'istanza pulita isolata
        coda_vuota = CodaRiproduzione()
        self.assertEqual(coda_vuota.getVolume(), 0.5)
        self.assertEqual(coda_vuota.getIndiceCorrente(), 0)
        self.assertFalse(coda_vuota.getShuffle())
        self.assertFalse(coda_vuota.getRepeat())
        self.assertEqual(coda_vuota.getTracce(), [])
        self.assertIsNone(coda_vuota.getTracciaCorrente())

    def testAggiungiTraccia(self):
        # self.coda ha gia t1, t2, t3 grazie al setup globale
        self.coda.aggiungiTraccia("t4")
        self.assertEqual(self.coda.getTracce(), ["t1", "t2", "t3", "t4"])

    def testInserisciTracciaModificaIndice(self):
        # Ascoltiamo "t2" (indice 1)
        self.coda.setIndiceCorrente(1)
        
        # Inseriamo prima della traccia che stiamo ascoltando
        self.coda.inserisciTraccia("t_nuova", 0)
        
        self.assertEqual(self.coda.getTracce(), ["t_nuova", "t1", "t2", "t3"])
        # L'indice deve slittare in avanti per puntare ancora a "t2"
        self.assertEqual(self.coda.getIndiceCorrente(), 2)

    def testRimuoviTracciaModificaIndice(self):
        # Ascoltiamo "t3" (indice 2)
        self.coda.setIndiceCorrente(2)
        
        # Rimuoviamo "t1" (indice 0)
        self.coda.rimuoviTracciaIndice(0)
        
        self.assertEqual(self.coda.getTracce(), ["t2", "t3"])
        # L'indice scala indietro a 1 per mantenere l'ascolto su "t3"
        self.assertEqual(self.coda.getIndiceCorrente(), 1)

    def testSpostaTracciaInCoda(self):
        # Ascoltiamo "t2" (indice 1)
        self.coda.setIndiceCorrente(1)
        
        # Spostiamo "t3" (indice 2) prima di "t2" (indice 0)
        self.coda.spostaTracciaInCoda(2, 0)
        
        self.assertEqual(self.coda.getTracce(), ["t3", "t1", "t2"])
        # L'indice di "t2" e diventato 2
        self.assertEqual(self.coda.getIndiceCorrente(), 2)

    def testSvuota(self):
        self.coda.setIndiceCorrente(2)
        self.coda.svuota()
        self.assertEqual(self.coda.getTracce(), [])
        self.assertEqual(self.coda.getIndiceCorrente(), 0)

    def testCalcolaSuccessivaLineare(self):
        # Testiamo il passaggio alla successiva partendo da "t2" (indice 1)
        self.coda.setIndiceCorrente(1)
        
        self.assertEqual(self.coda.calcolaSuccessiva(), "t3")
        self.assertEqual(self.coda.getIndiceCorrente(), 2)
        
        # Essendo arrivati in fondo (indice 2), la successiva deve tornare a "t1" (indice 0)
        self.assertEqual(self.coda.calcolaSuccessiva(), "t1")
        self.assertEqual(self.coda.getIndiceCorrente(), 0)

    def testCalcolaSuccessivaRepeat(self):
        self.coda.setIndiceCorrente(1)
        self.coda.toggleRepeat()
        
        # Non deve cambiare traccia o indice
        self.assertEqual(self.coda.calcolaSuccessiva(), "t2")
        self.assertEqual(self.coda.getIndiceCorrente(), 1)

    @patch('random.randint')
    def testCalcolaSuccessivaShuffle(self, mock_randint):
        self.coda.toggleShuffle()
        
        # Forziamo random a restituire 2 (cioe "t3")
        mock_randint.return_value = 2
        
        self.assertEqual(self.coda.calcolaSuccessiva(), "t3")
        self.assertEqual(self.coda.getIndiceCorrente(), 2)

    def testSetVolume(self):
        self.coda.setVolume(1.5)
        self.assertEqual(self.coda.getVolume(), 1.0)
        
        self.coda.setVolume(-0.5)
        self.assertEqual(self.coda.getVolume(), 0.0)
        
        self.coda.setVolume(0.7)
        self.assertEqual(self.coda.getVolume(), 0.7)

    def testToggleShuffleRepeat(self):
        self.coda.toggleShuffle()
        self.assertTrue(self.coda.getShuffle())
        
        self.coda.toggleRepeat()
        self.assertTrue(self.coda.getRepeat())

    def testSetIndiceCorrente(self):
        # Valore valido
        self.coda.setIndiceCorrente(1)
        self.assertEqual(self.coda.getIndiceCorrente(), 1)
        self.assertEqual(self.coda.getTracciaCorrente(), "t2")
        
        # Valore oltre limite (non deve aggiornare l'indice)
        self.coda.setIndiceCorrente(10)
        self.assertEqual(self.coda.getIndiceCorrente(), 1)
        
        # Valore negativo (non deve aggiornare l'indice)
        self.coda.setIndiceCorrente(-5)
        self.assertEqual(self.coda.getIndiceCorrente(), 1)

    def testTuttiIGetters(self):
        # Modifichiamo lo stato del setup globale per verificare i getters
        self.coda.setVolume(0.75)
        self.coda.toggleRepeat()
        
        self.assertEqual(self.coda.getVolume(), 0.75)
        self.assertEqual(self.coda.getIndiceCorrente(), 0)
        self.assertEqual(self.coda.getTracciaCorrente(), "t1")
        self.assertEqual(self.coda.getTracce(), ["t1", "t2", "t3"])
        self.assertTrue(self.coda.getRepeat())
        self.assertFalse(self.coda.getShuffle())

if __name__ == '__main__':
    unittest.main()