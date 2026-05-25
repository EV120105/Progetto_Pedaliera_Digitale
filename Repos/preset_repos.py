import json
import os

class PresetRepository:
    def __init__(self, path="presets_archivio.json"):
        self._path = path
        # Uso il nome '_presets' perché il PresetController cerca questo
        self._presets = {} 
        self.carica_archivio()

    def carica_archivio(self):
        #Carica i preset esistenti all'avvio per non sovrascriverli
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding='utf-8') as f:
                    dati = json.load(f)
                    if isinstance(dati, dict):
                        self._presets = dati
                    print(f" Archivio caricato: {len(self._presets)} preset trovati.")
            except (json.JSONDecodeError, IOError):
                print(" Errore lettura archivio o file vuoto. Inizializzo nuovo dizionario.")
                self._presets = {}

    # RINOMINATO DA aggiungi_preset A crea_preset PER COMPATIBILITÀ CON IL CONTROLLER
    def crea_preset(self, nome, dati_catena):
        #Aggiunge o aggiorna un preset nell'archivio
        # Aggiorniamo il dizionario in memoria
        self._presets[nome] = dati_catena
        # Scriviamo tutto su disco
        self.salva_archivio()

    def salva_archivio(self):
        #Sincronizza il dizionario interno con il file JSON
        try:
            with open(self._path, "w", encoding='utf-8') as f:
                json.dump(self._presets, f, indent=4)
            print(f" File '{self._path}' aggiornato correttamente.")
        except IOError as e:
            print(f" Errore critico durante il salvataggio: {e}")

    def get_preset(self, nome):
        #Recupera i dati di un preset specifico"""
        return self._presets.get(nome)