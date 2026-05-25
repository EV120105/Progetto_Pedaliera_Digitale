import os
import pygame
from Models.coda_riproduzione import CodaRiproduzione
from Models.traccia import TracciaAudio
from Controller.gestore_traccia_audio import gestore_traccia_audio
from Controller.gestore_playlist import GestorePlaylist

class GestorePlayer:
    def __init__(self, gestore_traccia:gestore_traccia_audio, gestore_playlist:GestorePlaylist):
        #il controller dovrà avere una propria variabile booleana per ricordarsi se è in pausa
        self._in_pausa:bool=False
        self._coda=CodaRiproduzione()
        self._gestore_traccia=gestore_traccia
        self._gestore_playlist=gestore_playlist
        #I comandi successivi servono per inizializzare il motore audio hardware
        #come libreria usiamo pygame -ce(community edition) che essendo più moderna
        #risolve alcuni bug/errori di compatibilità
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self._coda.getVolume())
    
    def aggiungiInCoda(self, percorso:str) -> str:
        traccia=self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso)
        if not traccia: return "ERRORE, traccia non trovata nel catalogo"
        self._coda.aggiungiTraccia(percorso)
        return "SUCCESSO, traccia aggiunta in fondo alla coda"
    
    def inserisciInCoda(self, percorso:str, posizione:int) -> str:
        traccia=self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso)
        if not traccia: return "ERRORE, traccia non trovata nel catalogo"
        #Controllo che indice inserito sia corretto
        posizione_reale=max(0, min(posizione, len(self._coda.getTracce())))
        self._coda.inserisciTraccia(percorso, posizione_reale)
        return f"SUCCESSO, traccia inserita in posizione {posizione_reale}"
    
    def spostaInCoda(self, indice_partenza:int, indice_arrivo:int)->str:
        self._coda.spostaTracciaInCoda(indice_partenza, indice_arrivo)
        return f"Traccia spostata dalla posizione {indice_partenza} alla {indice_arrivo}"

    def caricaPlaylistInCoda(self, nome_playlist:str)->str:
        tracce_playlist=self._gestore_playlist.reportTracceComplete(nome_playlist)
        if not tracce_playlist: return "ERRORE, la playlist è vuota o inesistente"

        self._coda.svuota()
        for traccia in tracce_playlist:
            traccia:TracciaAudio
            self._coda.aggiungiTraccia(traccia.getPercorso())
        return f"SUCCESSO: {len(tracce_playlist)} brani caricati dalla playlist {nome_playlist} "
    
    def visualizzaCoda(self) -> list:
        #Restituisco una lista di stringhe che poi la boundary interpreterà come tracce audio
        risultato=[]
        for i, percorso in enumerate(self._coda.getTracce()):
            traccia=self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso)
            if traccia:
                #Facciamo si che visualizzando la coda la canzone attualmente
                #in riproduzione venga flaggata
                flag_riproduzione="In riproduzione" if i == self._coda.getIndiceCorrente() else " "
                risultato.append(f"{traccia.getTitolo()} - {traccia.getArtista()}")
        return risultato
    
    def svuotaCoda(self) -> str:
        self._coda.svuota()
        self.stop() #Interrompo la traccia corrente
        return "Coda svuotata e riproduzione fermata"
    
    def rimuoviPerIndice(self, indice:int) -> str:
        tracce=self._coda.getTracce()
        if 0<=indice<len(tracce):
            #Memorizzo quello che sto ascoltando in questo istante
            indice_attuale=self._coda.getIndiceCorrente()
            era_in_riproduzione=(indice==indice_attuale)
            #Rimozione traccia dalla coda
            self._coda.rimuoviTracciaIndice(indice)
            #se ho eliminato proprio la canzone che stavo ascoltando:
            if era_in_riproduzione:
                if len(self._coda.getTracce())==0:
                    self.stop()
                else:
                    self.play()
            return f"Brano rimosso dalla posizione {indice}"
        return "ERRORE, indice non valido"
        
    def toggleShuffle(self) -> str:
        self._coda.toggleShuffle()
        stato="ATTIVO" if self._coda.getShuffle() else "DISATTIVO"
        return f"Shuffle impostato su: {stato}"
    
    def toggleRepeat(self):
        self._coda.toggleRepeat()
        stato="ATTIVO" if self._coda.getRepeat() else "DISATTIVO"
        return f"Repeat impostato su: {stato}"
    #SEZIONE COMANDI DEL PLAYER HARDWARE   
    def play(self) -> str:
        percorso = self._coda.getTracciaCorrente()
        if not percorso or not os.path.exists(percorso):
            return "ERRORE: Coda vuota o file non trovato."
        try:
            pygame.mixer.music.load(percorso)
            pygame.mixer.music.play()
            return f"In riproduzione: {self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso).getTitolo()}"
        except pygame.error as e:
            return f"ERRORE audio: Formato non supportato ({e})"
    
    def playIndice(self, indice:int):
        if 0 <= indice < len(self._coda.getTracce()):
            self.stop()
            self._coda.setIndiceCorrente(indice)
            return self.play()
        return "ERRORE, indice non valido"
    
    def gestisciPlayPausa(self) -> str:
        if self._in_pausa:
            pygame.mixer.music.unpause()
            self._in_pausa=False
            return "Player RIPRESO"
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self._in_pausa=True
            return "Player IN PAUSA"
        else:
            #se non sta suonando e non è in pausa parte da zero
            self._in_pausa=False
            return self.play()
        
    def stop(self)->str:
        pygame.mixer.music.stop()
        self._in_pausa=False #lo metto false perchè resetto lo stato della pausa
        return "Riproduzione FERMATA"
    
    def playSuccessiva(self)->str:
        self.stop()
        if self._coda.calcolaSuccessiva():
            return self.play()
        return "Coda terminata"
    
    def impostaVolume(self, vol_input:float) ->str:
        self._coda.setVolume(vol_input)
        pygame.mixer.music.set_volume(self._coda.getVolume())
        return f"Volume: {int(self._coda.getVolume()*100)}%"



