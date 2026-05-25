import os
import json

class TerminaleEffettiBoundary:
    def __init__(self, controller, repo, preset_controller, percorso_json_tracce="tracce.json"):
        self.controller = controller
        self.repo = repo
        self.preset_controller = preset_controller  
        self.percorso_json_tracce = percorso_json_tracce  

    def mostra_interfaccia(self):
        """Ciclo principale dell'interfaccia utente (CLI)."""
        while True:
            print("\n" + "="*75)
            print("TERMINALE EFFETTI")
            print("="*75)
            
            # Mostra lo stato attuale dei pedali
            for i in range(3):
                p = self.repo.get_pedale(i)
                if p:
                    stato = " [ON] " if not p.bypass else "[BYPASS]"
                    print(f"Slot [{i}] | {stato} | {p.tipo:<12} | {p.parametri}")
                else:
                    print(f"Slot [{i}] | -- VUOTO --")

            print("-" * 75)
            print("COMANDI: [0, 1, 2] Modifica | 's' Scambia | 'save' Salva | 'load' Carica | 'apply' Applica a File | 'q' Esci")
            azione = input("Scegli: ").strip().lower()

            if azione == 'q': 
                break

            if azione == 's':
                self._gestisci_scambio()
                continue

            if azione == 'save':
                self._seleziona_salva_preset()
                continue

            if azione == 'load':
                self._seleziona_carica_preset()
                continue

            if azione == 'apply':
                self._gestisci_applicazione_audio()
                continue

            if azione in ['0', '1', '2']:
                self._gestisci_modifica_pedale(int(azione))

    def _carica_tracce_dal_json(self) -> list:
        """Legge il file JSON delle tracce e restituisce una lista di dizionari."""
        if not os.path.exists(self.percorso_json_tracce):
            print(f"[ERRORE]: Archivio tracce '{self.percorso_json_tracce}' non trovato.")
            return []
        try:
            with open(self.percorso_json_tracce, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRORE]: Impossibile leggere il file delle tracce: {e}")
            return []

    def _salva_tracce_nel_json(self, lista_tracce: list):
        """Salva la lista aggiornata delle tracce nel file JSON."""
        try:
            with open(self.percorso_json_tracce, 'w', encoding='utf-8') as f:
                json.dump(lista_tracce, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRORE]: Impossibile aggiornare l'archivio tracce.json: {e}")

    def _gestisci_applicazione_audio(self):
        """Mostra l'elenco delle tracce disponibili nel JSON, chiede il nuovo nome e invia il percorso al controller."""
        tracce = self._carica_tracce_dal_json()
        if not tracce:
            print("[AVVISO]: Nessuna traccia disponibile nel database.")
            return

        print("\n" + "-"*30 + " TRACCE DISPONIBILI " + "-"*30)
        for idx, traccia in enumerate(tracce, start=1):
            durata_min = f"{int(traccia['durata'] // 60)}m {int(traccia['durata'] % 60)}s"
            print(f"[{idx}] Titolo : {traccia.get('titolo')}")
            print(f"    Artista: {traccia.get('artista')} | Durata: {durata_min} | Formato: {traccia.get('formato')}")
            print(f"    Percorso: {traccia.get('percorso')}")
            print("-" * 80)

        scelta = input("Scegli il numero della traccia da elaborare (o 'c' per annullare): ").strip()
        if scelta.lower() == 'c':
            return

        try:
            scelta_idx = int(scelta) - 1
            # CORRETTO: Eliminato 'choix_idx :=' per evitare NameError
            if scelta_idx < 0 or scelta_idx >= len(tracce):
                print("[ERRORE]: Selezione non valida.")
                return
            
            traccia_selezionata = tracce[scelta_idx]
            percorso_originale = traccia_selezionata.get("percorso")
        except ValueError:
            print("[ERRORE]: Inserisci un numero valido.")
            return

        if not os.path.exists(percorso_originale):
            print(f"[ERRORE]: Il file fisico non esiste sul PC al percorso indicato:\n{percorso_originale}")
            return

        # Richiesta del nuovo nome del file
        nuovo_nome = input("Inserisci il nome per il nuovo file elaborato (senza .wav): ").strip()
        if not nuovo_nome:
            print("[ERRORE]: Il nome del file non può essere vuoto.")
            return

        # Generazione del percorso nella stessa cartella del file originario
        cartella_originale = os.path.dirname(os.path.normpath(percorso_originale))
        percorso_uscita_personalizzato = os.path.join(cartella_originale, f"{nuovo_nome}.wav")

        # Controllo preventivo dell'esistenza del file
        if os.path.exists(percorso_uscita_personalizzato):
            print("errore nome gia esistente")
            return

        print(f"\n[Sistema]: Avvio elaborazione DSP per: {traccia_selezionata.get('titolo')}.wav")
        
        # Chiamata al metodo DSP dell'oggetto ElaboratoreCatena passandogli anche il percorso d'uscita
        esito = self.controller.applica_dsp_catena(percorso_originale, percorso_uscita_personalizzato)
        print(f"\n[CONFERMA]: {esito}")

        # Se l'elaborazione è andata a buon fine, salviamo la nuova traccia in tracce.json
        if "ERRORE" not in esito:
            nuova_traccia = {
                "titolo": nuovo_nome,
                "artista": traccia_selezionata.get("artista", "Sconosciuto"),
                "durata": traccia_selezionata.get("durata", 0.0),
                "percorso": percorso_uscita_personalizzato,
                "formato": "wav"
            }
            tracce.append(nuova_traccia)
            self._salva_tracce_nel_json(tracce)

    def _seleziona_salva_preset(self):
        """Implementa la sequenza [Salva Preset]"""
        pedali_vivi = self.repo.get_tutti_i_pedali()
        if all(p is None for p in pedali_vivi):
            print("[ERRORE]: Impossibile salvare. La catena effetti è vuota!")
            return

        nome = input("Inserisci il nome per il nuovo preset: ").strip()
        if not nome:
            print("Nome non valido.")
            return

        try:
            self.preset_controller.salva_attuale_come_preset(nome)
            print("[CONFERMA]: Salvataggio preset avvenuto con successo!")
        except IOError:
            print("[ERRORE]: Errore I/O del disco durante il salvataggio.")

    def _seleziona_carica_preset(self):
        """Implementa la sequenza [Carica Preset] mostrando prima quelli esistenti"""
        try:
            self.preset_controller.preset_repo.carica_archivio()
            preset_salvati = list(self.preset_controller.preset_repo._presets.keys())
            
            print("\nPreset attualmente disponibili in archivio:")
            if preset_salvati:
                print(f" -> {', '.join(preset_salvati)}")
            else:
                print(" -> Nessun preset salvato nell'archivio JSON.")
        except Exception:
            print(" -> Impossibile recuperare i preset dall'archivio.")

        nome = input("\nInserisci il nome del preset da caricare: ").strip()
        if not nome:
            print("Nome non valido.")
            return

        esito = self.preset_controller.carica_preset(nome)

        if esito.startswith("Errore:"):
            print(f"[ERRORE]: Preset non trovato. {esito}")
        else:
            print(f"[CONFERMA]: {esito}")

    def _gestisci_scambio(self):
        """Gestisce l'input utente per lo scambio di posizione dei pedali."""
        try:
            idx1 = int(input("Indice primo pedale (0-2): "))
            idx2 = int(input("Indice secondo pedale (0-2): "))
            
            self.repo.pedali_attivi[idx1], self.repo.pedali_attivi[idx2] = self.repo.pedali_attivi[idx2], self.repo.pedali_attivi[idx1]
            for i, p in enumerate(self.repo.pedali_attivi):
                if p: 
                    p.posizione = i
            self.repo.save_to_json()
            print("Scambio salvato nel JSON.")
        except Exception: 
            print(" Errore indici.")

    def _gestisci_modifica_pedale(self, idx):
        """Gestisce l'input utente per modificare lo stato o i parametri di un pedale."""
        pedale = self.repo.get_pedale(idx)
        if not pedale: 
            return

        print(f"\n{pedale.tipo} -> 'on', 'off' o nome parametro {list(pedale.parametri.keys())}")
        scelta = input("> ").strip().lower()

        if scelta == 'on':
            pedale.bypass = False
            self.repo.save_to_json()
        elif scelta == 'off':
            pedale.bypass = True
            self.repo.save_to_json()
        # CORRETTO: Rimosso 'choix in' che causava crash immediato
        elif scelta in pedale.parametri:
            try:
                val = float(input(f"Valore per {scelta}: "))
                self.controller.set_parametro_pedale(idx, {scelta: val})
            except ValueError: 
                print("Solo numeri!")
        else:
            print(f"'{scelta}' non valido.")