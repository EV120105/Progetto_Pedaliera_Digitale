import os
import json
from Controller.gestore_coda_riproduzione import GestorePlayer

class ConsolePlayer:
    def __init__(self, gestore_player: GestorePlayer):
        self._gestore = gestore_player
        # Definiamo il percorso del database delle tracce per la selezione automatica
        self.percorso_json_tracce = "tracce.json"

    def _seleziona_percorso_da_json(self) -> str:
        #Metodo di supporto per mostrare le canzoni esistenti e recuperare il percorso.
        if not os.path.exists(self.percorso_json_tracce):
            print(f"[ERRORE]: File '{self.percorso_json_tracce}' non trovato.")
            return ""
        
        try:
            with open(self.percorso_json_tracce, 'r', encoding='utf-8') as f:
                tracce = json.load(f)
        except Exception as e:
            print(f"[ERRORE]: Impossibile leggere il catalogo tracce: {e}")
            return ""

        if not tracce:
            print("[AVVISO]: Nessuna traccia disponibile nel database.")
            return ""

        print("\n--- SELEZIONA UNA TRACCIA DAL CATALOGO ---")
        for idx, traccia in enumerate(tracce, start=1):
            durata_min = f"{int(traccia['durata'] // 60)}m {int(traccia['durata'] % 60)}s"
            print(f" [{idx}] {traccia.get('titolo')} (Artista: {traccia.get('artista')} | Durata: {durata_min})")
        print("-" * 50)

        scelta = input("Scegli il numero del brano (o 'c' per annullare): ").strip()
        if scelta.lower() == 'c':
            return ""

        try:
            scelta_idx = int(scelta) - 1
            if scelta_idx < 0 or scelta_idx >= len(tracce):
                print("[ERRORE]: Selezione non valida.")
                return ""
            
            percorso = tracce[scelta_idx].get("percorso")
            if not os.path.exists(percorso):
                print(f"[ERRORE]: Il file fisico non esiste sul PC al percorso indicato:\n{percorso}")
                return ""
            return percorso
        except ValueError:
            print("[ERRORE]: Inserisci un numero intero valido.")
            return ""

    def avvia(self):
        while True:
            print("\n" + "="*50)
            print("                 LETTORE AUDIO")
            print("="*50)
            print(" [CONTROLLI]")
            print("  1. Play / Pausa")
            print("  2. Prossima Traccia")
            print("  3. Stop")
            print("  4. Regola Volume")
            print("\n [CODA DI RIPRODUZIONE]")
            print("  5. Aggiungi brano in fondo alla coda")
            print("  6. Inserisci brano in posizione specifica")
            print("  7. Carica intera Playlist")
            print("  8. Visualizza Coda")
            print("  9. Rimuovi brano per indice")
            print(" 10. Svuota intera coda")
            print("\n [OPZIONI DI RIPRODUZIONE]")
            print(" 11. Attiva/Disattiva Shuffle")
            print(" 12. Attiva/Disattiva Repeat")
            print(" 13. Riproduci brano da un indice specifico")
            print(" 14. Sposta un brano nella coda")
            print("\n  0. Torna al menu principale (L'audio continuera')")
            print("="*50)
            
            scelta = input("\nScegli un'opzione: ").strip()
            
            if scelta == "1":
                print(self._gestore.gestisciPlayPausa())

            elif scelta == "2":
                print(self._gestore.playSuccessiva())
                
            elif scelta == "3":
                print(self._gestore.stop())
                
            elif scelta == "4":
                try:
                    vol = float(input("Inserisci volume (da 0.0 a 1.0, es. 0.5): "))
                    print(self._gestore.impostaVolume(vol))
                except ValueError:
                    print("Valore non valido. Usa i decimali col punto.")
                    
            elif scelta == "5":
                # AGGIORNATO: Selezione del brano tramite elenco numerato da JSON invece della stringa manuale
                path = self._seleziona_percorso_da_json()
                if path:
                    print(self._gestore.aggiungiInCoda(path))
                
            elif scelta == "6":
                # AGGIORNATO: Selezione del brano tramite elenco numerato da JSON invece della stringa manuale
                path = self._seleziona_percorso_da_json()
                if path:
                    try:
                        pos = int(input("Inserisci la posizione in cui inserirlo (es. 0, 1...): "))
                        print(self._gestore.inserisciInCoda(path, pos))
                    except ValueError:
                        print("Inserisci un numero intero per la posizione.")
                    
            elif scelta == "7":
                nome_p = input("Inserisci il nome della Playlist da caricare: ").strip()
                print(self._gestore.caricaPlaylistInCoda(nome_p))
                
            elif scelta == "8":
                print("\n--- CODA ATTUALE ---")
                coda = self._gestore.visualizzaCoda()
                if not coda:
                    print("La coda e' vuota.")
                else:
                    for brano in coda:
                        print(brano)
                        
            elif scelta == "9":
                try:
                    idx = int(input("Inserisci l'indice del brano da rimuovere: "))
                    print(self._gestore.rimuoviPerIndice(idx))
                except ValueError:
                    print("Inserisci un numero intero valido.")
                    
            elif scelta == "10":
                conferma = input("Sei sicuro di voler svuotare la coda e fermare la musica? (s/n): ")
                if conferma.lower() == 's':
                    print(self._gestore.svuotaCoda())
                    
            elif scelta == "11":
                print(self._gestore.toggleShuffle())
                
            elif scelta == "12":
                print(self._gestore.toggleRepeat())

            elif scelta == "13":
                try:
                    idx = int(input("Inserisci l'indice del brano da ascoltare: "))
                    print(self._gestore.playIndice(idx))
                except ValueError:
                    print("Inserisci un numero intero valido.")
                    
            elif scelta == "14":
                try:
                    vecchio = int(input("Inserisci l'indice attuale del brano da spostare: "))
                    nuovo = int(input("Inserisci il nuovo indice di destinazione: "))
                    print(self._gestore.spostaInCoda(vecchio, nuovo))
                except ValueError:
                    print("Inserisci numeri interi validi.")    
                
            elif scelta == "0":
                break
                
            else:
                print("Scelta non valida.")