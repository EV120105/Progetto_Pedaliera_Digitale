import random
class CodaRiproduzione():
    def __init__(self):
        #inizializzo i valori di default che avrà il player una volta avviato
        self._volume=0.5 # (potrà assumere valori tra 0.0 ed 1.0)
        self._indice_corrente=0
        self._shuffle=False
        self._repeat=False
        #self.tracce sarà una lista di stringhe (i percorsi) che consento una ricerca più rapida per id
        #ovviamente poi con l'interfaccia grafica l'utente non dovrà mai lavorare con i percorsi
        #in quanto selezionanado una traccia si attiverà il metodo getPercorso di tracciaudio
        #e al player o in generale dove serve sarà passato questo 
        self._tracce=[] #inizializzo la lista vuota di tracce in coda
    def aggiungiTraccia(self, percorso):
        #questa è solo per inserire tracce a fine coda
        self._tracce.append(percorso)
        #non gestisco casi in cui il percorso sia già presente in tracce siccome questo sarà il player audio
        #ed è assolutamente possibile che l'utente voglia rinserire la stessa traccia in posizioni diverse
    def inserisciTraccia(self, percorso, posizione):
        #inserisce una traccia in una data posizione
        self._tracce.insert(posizione, percorso)
        #se inserisco un brano prima di quello che sto ascoltando l'indice di quello che sto ascoltando scivola in avanti di un posto
        if posizione <= self._indice_corrente:
            self._indice_corrente += 1
      
    def rimuoviTracciaIndice(self, indice):
        if 0<= indice < len(self._tracce):
            self._tracce.pop(indice)
            #Così facendo elimino per posizione e non per percorso visto che il medesimo percorso
            #potrebbe ripresentarsi nella lista causerebbe problemmi
            if indice < self._indice_corrente:
                #se cancello un brano prima di quello corrente che ascolto
                #l'indice corrente slitta indietro di uno
                self._indice_corrente -= 1
            elif self._indice_corrente >= len(self._tracce):
                #se cancello l'ultimo brano in coda e sforo i limiti
                self._indice_corrente= max(0, len(self._tracce)-1)
    def spostaTracciaInCoda(self, vecchio_indice, nuovo_indice):
        #questo metodo consente di spostare una traccia in coda in una posizione diversa aggiustando gli indici
        if 0 <= vecchio_indice < len(self._tracce) and 0 <= nuovo_indice < len(self._tracce):
            traccia=self._tracce.pop(vecchio_indice) #pop non solo rimuove ma mi ritorna anche quello che stava in quell'indice
            self._tracce.insert(nuovo_indice, traccia)
            #Ora vediamo la logica di come si spostano gli indici
            if self._indice_corrente==vecchio_indice:
                self._indice_corrente=nuovo_indice
            elif vecchio_indice < self._indice_corrente <= nuovo_indice:
                self._indice_corrente -= 1
            elif nuovo_indice <= self._indice_corrente < vecchio_indice:
                self._indice_corrente += 1

    def svuota(self):
        self._tracce=[]
        self._indice_corrente=0
    def calcolaSuccessiva(self):
        if not self._tracce:
            return None
        
        if self._shuffle:
            self._indice_corrente=random.randint(0, len(self._tracce)-1)
        elif self._repeat:
            #non facciamo nulla l'indice deve rimanere tale e quale lo stesso
            pass
        else:
            self._indice_corrente += 1
            #se sono ad esempio in una lista di dieci tracce e indice corrente è 9
            #vuol dire che sto ascoltando l'ultima traccia a questo punto se scorro di uno andrei out of bound per la lista
            #allora quando indice_corrente diventa >= di len(tracce) lo riporto a zero (ascolto di nuovo la prima canzone in coda)
            if self._indice_corrente>=len(self._tracce):
                self._indice_corrente=0
        return self.getTracciaCorrente()
    
    #Definisco ora i vari getters/setters
    def getIndiceCorrente(self):
        return self._indice_corrente
    def getTracciaCorrente(self):
        if not self._tracce: return None
        return self._tracce[self._indice_corrente]
    def getVolume(self):
        return self._volume
    def getTracce(self):
        #A differenza di getTracciaCorrente, questo restituisce tutte le tracce in coda
        return self._tracce
    def getShuffle(self):
        return self._shuffle
    def getRepeat(self):
        return self._repeat
    
    
    def toggleShuffle(self):
        self._shuffle = not self._shuffle
    def toggleRepeat(self):
        self._repeat = not self._repeat
    def setVolume(self, vol_input:float):
        self._volume=max(0.0, min(1.0, vol_input))
    def setIndiceCorrente(self, indice:int):
        if 0 <= indice < len(self._tracce):
            self._indice_corrente = indice
