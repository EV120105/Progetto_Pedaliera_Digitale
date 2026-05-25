class TracciaAudio:
    def __init__(self, formato: str, durata: float, titolo: str, artista: str, percorso: str):
        self._formato = formato
        self._durata = durata
        self._titolo = titolo
        self._artista = artista
        self._percorso = percorso
        # AGGIUNTA FONDAMENTALE PER UC6:
        self._campioni = [] # Qui caricheremo i dati audio reali (array di float)

    def toDict(self) -> dict:
        """
        Converte l'oggetto in un dizionario per la persistenza JSON.
        """
        return {
            "titolo": self._titolo,
            "artista": self._artista,
            "durata": self._durata,
            "percorso": self._percorso,
            "formato": self._formato
        }

    # Getter standard
    def getFormato(self): return self._formato
    def getDurata(self): return self._durata
    def getTitolo(self): return self._titolo
    def getArtista(self): return self._artista
    def getPercorso(self): return self._percorso

    # Metodi per l'elaborazione DSP (UC6)
    def getCampioni(self):
        """Restituisce l'array dei campioni audio"""
        return self._campioni

    def setCampioni(self, nuovi_campioni: list):
        """Imposta l'array dei campioni audio elaborati"""
        self._campioni = nuovi_campioni

    @classmethod
    def fromDict(cls, dati: dict) -> "TracciaAudio":
        """Metodo Factory per ricostruire l'oggetto da un dizionario JSON"""
        return cls(
            formato=dati["formato"], 
            durata=dati["durata"], 
            titolo=dati["titolo"],
            artista=dati["artista"], 
            percorso=dati["percorso"]
        )
    def __str__(self):
        return f"{self.getTitolo()} di {self.getArtista()} [{self.getDurata()}] ({self.getFormato()})\n    Percorso: {self.getPercorso()}"