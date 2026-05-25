import os
import json
from Controller.gestore_playlist import GestorePlaylist

class ConsolePlaylist:
    def __init__(self, gestore_playlist: GestorePlaylist):
        self._gestore = gestore_playlist
        # Definiamo il percorso del database delle tracce per la selezione automatica
        self.percorso_json_tracce = "tracce.json"

    def _seleziona_percorso_da_json(self) -> str:
        """Metodo di supporto per mostrare le canzoni esistenti e recuperare il percorso."""
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
            return percorso
        except ValueError:
            print("[ERRORE]: Inserisci un numero intero valido.")
            return ""

    def avvia(self):
        while True:
            print("\n" + "═"*40)
            print("       GESTIONE MIE PLAYLIST")
            print("═"*40)
            print("1. Crea nuova Playlist")
            print("2. Elenco mie Playlist")
            print("3. Gestisci Playlist (Aggiungi/Rimuovi/Vedi)")
            print("4. Rimuovi una Playlist")
            print("0. Torna al menu principale")
            
            scelta = input("\nScegli un'opzione: ")
            
            if scelta == "1":
                self._schermata_crea()
            elif scelta == "2":
                self._schermata_mostra()
            elif scelta == "3":
                self._schermata_gestione_dettaglio()
            elif scelta == "4":
                self._schermata_rimuovi()
            elif scelta == "0":
                break
            else:
                print("Scelta non valida.")

    def _schermata_crea(self):
        print("\n--- NUOVA PLAYLIST ---")
        nome = input("Inserisci il nome della playlist: ").strip()  # Corretto con .strip()
        if nome:
            print(f">>> Esito: {self._gestore.creaPlaylist(nome)}")
        else:
            print("Nome non valido.")

    def _schermata_mostra(self):
        print("\n--- LE TUE PLAYLIST ---")
        liste = self._gestore.mostraMiePlaylist()
        
        if isinstance(liste, str): 
            print(f">>> {liste}")
        elif not liste:
            print("Non hai ancora creato nessuna playlist.")
        else:
            for p in liste:
                print(f"• {p.getNomePlaylist()} [{len(p.getTracce())} brani]")

    def _schermata_rimuovi(self):
        print("\n--- RIMOZIONE PLAYLIST ---")
        playlist_da_rimuovere = input("\nScrivere il nome esatto della playlist da rimuovere (o 'annulla'): ").strip()  # Corretto con .strip()
        if playlist_da_rimuovere.lower() == 'annulla':
            return
        esito = self._gestore.rimuoviPlaylist(playlist_da_rimuovere)
        print(f"\n>>> {esito}")

    def _schermata_gestione_dettaglio(self):
        nome_p = input("\nInserisci il nome esatto della playlist da gestire: ").strip()  # Corretto con .strip()
        
        # CONTROLLO DI ESISTENZA: recuperiamo le playlist dell'utente loggato
        mie_playlist = self._gestore.mostraMiePlaylist()
        if isinstance(mie_playlist, str):
            print(f">>> {mie_playlist}")
            return
            
        # Verifichiamo se esiste una playlist con il nome fornito
        playlist_esiste = any(p.getNomePlaylist() == nome_p for p in mie_playlist)
        
        if not playlist_esiste:
            print("ERRORE: Playlist inesistente.")
            return  # Interrompe il metodo e torna al menu delle playlist senza entrare nel ciclo
            
        # Se esiste, allora avvia il ciclo di gestione dettagliata
        while True:
            print(f"\n---   PLAYLIST: {nome_p} ---")
            print("1.  Visualizza brani contenuti")
            print("2.  Aggiungi brano (da catalogo)")
            print("3.  Rimuovi brano")
            print("0.  Indietro")
            
            op = input("Scegli un'operazione: ")
            if op == "1":
                tracce = self._gestore.reportTracceComplete(nome_p)
                if not tracce:
                    print("Playlist vuota.")  # Avendo già verificato l'esistenza, se è vuota è solo vuota
                else:
                    print("\nBrani contenuti:")
                    for i, t in enumerate(tracce, 1):
                        print(f"{i}. {t}")
            elif op == "2":
                # AGGIORNATO: Selezione del brano tramite elenco numerato da JSON invece della stringa manuale
                path = self._seleziona_percorso_da_json()
                if path:
                    print(f"\n>>> Esito: {self._gestore.aggiungiBrano(nome_p, path)}")
            elif op == "3":
                # AGGIORNATO: Selezione del brano tramite elenco numerato da JSON invece della stringa manuale
                path = self._seleziona_percorso_da_json()
                if path:
                    print(f"\n>>> Esito: {self._gestore.rimuoviBrano(nome_p, path)}")
            elif op == "0":
                break
            else:
                print("Opzione non valida.")