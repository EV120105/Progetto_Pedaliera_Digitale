import json
from Models.traccia import TracciaAudio

class TracciaAudioRepository:
    def __init__(self, path="tracce.json"):
        self._path = path
        self._tracce = {}
        #self._tracce è un dizionario di oggetti TracciaAudio in cui la chiave è il percorso
        self.letturaTracce()

    def letturaTracce(self):
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                #il json è invece una lista di dizionari che contengono i metadati delle tracce audio
                dati: list = json.load(f)
                self._tracce = {d["percorso"]: TracciaAudio.fromDict(d) for d in dati}
                # CHIAVE = percorso della traccia in quanto due tracce seppur diverse possono presentare
                #lo stesso nome pertanto come identificativo useremo il percorso
        except (FileNotFoundError, json.JSONDecodeError):
            self._tracce = {}

    def getPathTracceRepo(self):
        return self._path

    def salvaTracce(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                lista_tracce = [t.toDict() for t in self._tracce.values()]
                json.dump(lista_tracce, f, indent=4)
        except IOError:
            return "Errore durante il salvataggio nel disco"
    # Ricerca esatta usando la chiave del dizionario (Veloce)
    def cercaPerPercorso(self, percorso_input: str) -> "TracciaAudio":
        return self._tracce.get(percorso_input)
    def aggiungiTraccia(self, nuova_traccia: TracciaAudio):
        # Aggiungiamo usando il percorso come chiave univoca
        self._tracce[nuova_traccia.getPercorso()] = nuova_traccia
        self.salvaTracce()

    def rimuoviTraccia(self, percorso_input: str) -> bool:
        if percorso_input in self._tracce:
            self._tracce.pop(percorso_input)
            self.salvaTracce()
            return True
        return False

    def tutti(self) -> list:
        return list(self._tracce.values())

        
          







    
    
    

        

    

        