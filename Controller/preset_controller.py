from Models.pedali import PedaleDistorsione, PedaleChorus, PedaleDelay

class PresetController:
    def __init__(self, catena_repo, preset_repo):
        self.catena_repo = catena_repo # Gestisce catena_effetti_attuale.json
        self.preset_repo = preset_repo # Gestisce presets_archivio.json

    def salva_attuale_come_preset(self, nome_preset):
        # Recupera la lista degli oggetti pedale (inclusi i None)
        pedali_vivi = self.catena_repo.get_tutti_i_pedali()
        
        dati_preset = []
        for p in pedali_vivi:
            if p:
                dati_preset.append(p.to_dict())
            else:
                dati_preset.append(None)
        
        self.preset_repo.crea_preset(nome_preset, dati_preset)
        print(f"Sistema: Preset '{nome_preset}' salvato con successo.")

    def carica_preset(self, nome_preset):
        dati_salvati = self.preset_repo.get_preset(nome_preset)
        if not dati_salvati:
            return f"Errore: Preset '{nome_preset}' inesistente"

        # 1. Reset della catena attuale
        self.catena_repo.pedali_attivi = [None, None, None] 
        
        # 2. Ricostruzione oggetti tramite Factory
        for i, d in enumerate(dati_salvati):
            if d is not None:
                try:
                    nuovo_p = self._factory_pedale(d) 
                    # Usiamo l'indice del ciclo per la posizione se d["posizione"] fallisce
                    pos = d.get("posizione", i)
                    self.catena_repo.aggiungi_o_aggiorna(nuovo_p, pos)
                except Exception as e:
                    print(f"Avviso: Errore nel caricamento dello slot {i}: {e}")
            else:
                self.catena_repo.rimuovi(i)
        
        self.catena_repo.save_to_json()
        return f"EsitoSuccesso: Preset '{nome_preset}' caricato correttamente."

    def _factory_pedale(self, d):
        if d is None: return None
        
        tipo = d.get("tipo")
        pos = d.get("posizione", 0)
        par = d.get("parametri", {})
        
        if tipo == "Distorsione":
            p = PedaleDistorsione(pos, gain=par.get("gain", 1.0))
        elif tipo == "Chorus":
            # Riallineato ai parametri del modello (rate e depth)
            p = PedaleChorus(pos, 
                             rate=par.get("rate", 1.5), 
                             depth=par.get("depth", 0.5))
        elif tipo == "Delay":
            # Corretto: usiamo 'tempo' per coincidere con Models/pedali.py
            p = PedaleDelay(pos, 
                            tempo=par.get("tempo", 500), 
                            feedback=par.get("feedback", 0.4))
        else:
            print(f"Avviso: Tipo {tipo} non riconosciuto.")
            return None

        # Ripristina lo stato del Bypass
        p.bypass = d.get("bypass", False)
        return p