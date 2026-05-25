import json
import os
from Models.pedali import PedaleDistorsione, PedaleChorus, PedaleDelay

class catena_effetti:
    def __init__(self, storage_path="catena_data.json"):
        self.storage_path = storage_path
        # Precondizione UC5: Oggetto CATENAEFFETTI istanziato
        self.pedali_attivi = [None] * 3

    def aggiungi_o_aggiorna(self, pedale, posizione):
        if 0 <= posizione < len(self.pedali_attivi):
            self.pedali_attivi[posizione] = pedale
            self.save_to_json() 
            return True
        return False

    def rimuovi(self, posizione):
        #Postcondizione: Istanza di PEDALE rimossa
        if 0 <= posizione < len(self.pedali_attivi):
            self.pedali_attivi[posizione] = None
            self.save_to_json()
            return True
        return False

    def get_pedale(self, posizione):
        if 0 <= posizione < len(self.pedali_attivi):
            return self.pedali_attivi[posizione]
        return None

    def save_to_json(self):
        #Sincronizzazione stato su file
        data = []
        for p in self.pedali_attivi:
            if p:
                data.append({
                    "tipo": p.tipo,
                    "posizione": p.posizione,
                    "parametri": p.parametri,
                    "bypass": p.bypass
                })
            else:
                data.append(None)
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self):
        if not os.path.exists(self.storage_path): return
        with open(self.storage_path, "r") as f:
            # Logica di ricostruzione istanze (Factory)
            pass
    def get_tutti_i_pedali(self):
        #Restituisce la lista completa dei pedali (compresi i None)
        return self.pedali_attivi