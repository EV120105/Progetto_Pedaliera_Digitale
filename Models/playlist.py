class Playlist():
    def __init__(self, nome_playlist:str, proprietario:str, tracce:list =None):
        self._nome_playlist=nome_playlist
        self._proprietario=proprietario
        self._tracce=tracce if tracce is not None else []
        #self.tracce è una lista di percorsi 
        #scelgo di salvarlo così anzitutto perchè evità ridondanza di informazioni rispetto a fare una lista di oggetti 
        #TracciaAudio, inoltre è un vero e proprio id per la traccia avendone una lista sarà poi il controller playlist che richiama
        #il controller traccia e chiede di fare un report delle tracce associate a quei percorsi
    def getNomePlaylist(self):
        return self._nome_playlist
    def getProprietario(self):
        return self._proprietario
    def getTracce(self):
        return self._tracce
    def toDict(self):
        return {
            "nome_playlist": self._nome_playlist,
            "proprietario": self._proprietario,
            "tracce": self._tracce  # Questa è la lista di percorsi (stringhe)
            }
    @classmethod
    def fromDict(cls, dizionario)->"Playlist":
        return cls(
            dizionario["nome_playlist"], dizionario["proprietario"],
            dizionario["tracce"]
        )
    def aggiungiTraccia(self, percorso_input):
        if percorso_input not in self._tracce:
            self._tracce.append(percorso_input)
            return True
        else:
            return False
    def rimuoviTraccia(self, percorso_input):
        if percorso_input in self._tracce:
            self._tracce.remove(percorso_input)
            return True
        else: 
            return False
