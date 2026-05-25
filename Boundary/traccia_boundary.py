from Controller.gestore_traccia_audio import gestore_traccia_audio
from Models.traccia import TracciaAudio

class ConsoleCatalogo():
    def __init__(self, gestore_traccia: gestore_traccia_audio):
        self.gestore_traccia = gestore_traccia

    def selectMenu(self):
        while True:
            print("\n" + "=" * 30)
            print("       GESTIONE TRACCE")
            print("=" * 30)
            print("1. Importa nuova traccia")
            print("2. Mostra tutte le tracce")
            print("3. Rimuovi traccia")
            print("4. Cerca una traccia")
            print("0. Torna al menu principale")
            scelta = input("\nScegli un'opzione: ")
            if scelta == "1":
                self.schermataImporta()
            elif scelta == "2":
                self.schermataMostra()
            elif scelta == "3":
                self.schermataRimuovi()
            elif scelta == "4":
                self.schermataCerca()
            elif scelta=="0":
                break
            else:
                print("Scelta non valida")

    def schermataImporta(self):
        print("\n---IMPORTA BRANO---")
        percorso = input("Inserisci percorso assoluto della traccia(\n non includere le virgolette se presenti): ")
        risultato = self.gestore_traccia.importaTraccia(percorso)
        print(f"\n>>> ESITO: {risultato}")

    def schermataMostra(self):
        print("---CATALOGO AUDIO---")
        lista_tracce = self.gestore_traccia.mostraCatalogo()
        if not lista_tracce:
            print("Il catalogo è vuoto")
        else:
            for t in lista_tracce:
                print(f"- {t}\n")

    def schermataRimuovi(self):
        print ("---RIMUOVI BRANO---")
        percorso_da_eliminare = input("Inserire il percorso della traccia (o 'annulla'): ")
        if percorso_da_eliminare.lower() == 'annulla':
            return 
        if self.gestore_traccia.rimuoviTraccia(percorso_da_eliminare):
            print(">>> BRANO RIMOSSO CON SUCCESSO ")
        else: 
            print("ERRORE: nessun brano trovato")
    def schermataCerca(self):
        print("\n--- CERCA BRANO ---")
        parola = input("Inserisci un pezzo del titolo o dell'artista da cercare: ")
        risultati = self.gestore_traccia.cercaTracciaNomeArtista(parola)
        if not risultati:
            print(">>> Nessun brano trovato con questa chiave di ricerca.")
        else:
            print(f"\n>>> Trovati {len(risultati)} brani:")
            for t in risultati:
                print(f"  - {t}")