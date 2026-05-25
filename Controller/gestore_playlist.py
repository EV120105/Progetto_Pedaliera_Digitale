from Models.playlist import Playlist
from Repos.playlist_repository import PlaylistRepository
from Controller.gestore_traccia_audio import gestore_traccia_audio
from Controller.gestore_utente import GestoreUtente
class GestorePlaylist():
    def __init__(self, playlist_repo: PlaylistRepository, gestore_utente: GestoreUtente, gestore_traccia:gestore_traccia_audio):
        self._playlist_repo=playlist_repo
        self._gestore_utente=gestore_utente
        self._gestore_traccia=gestore_traccia
    def creaPlaylist(self, nome_playlist:str) -> str:
        utente_corrente=self._gestore_utente.getUtenteCorrente()
        if utente_corrente is None:
            return "ERRORE, nessun utente loggato"
        nome_utente=utente_corrente.getNomeUtente()
        if self._playlist_repo.getPlaylist(nome_utente, nome_playlist) is not None:
            return f"ERRORE, hai già una playlist chiamata '{nome_playlist}'"
        nuova_playlist = Playlist(nome_playlist, nome_utente)
        self._playlist_repo.aggiungiPlaylist(nuova_playlist)
        return f"SUCCESSO, playlist '{nome_playlist}' creata"
    def rimuoviPlaylist(self, nome_playlist)->str:
        nome_utente=self._gestore_utente.getUtenteCorrente().getNomeUtente()
        if self._playlist_repo.rimuoviPlaylist(nome_utente, nome_playlist):
            return "SUCCESSO, playlist rimossa"
        else:
            return "ERRORE, playlist indicata inesistente"
    def mostraMiePlaylist(self) -> list :
        utente_corrente=self._gestore_utente.getUtenteCorrente()
        if utente_corrente is None:
            return "ERRORE, devi essere loggato per questa azione"
        nome_utente=utente_corrente.getNomeUtente()
        return self._playlist_repo.getPlaylistPerUtente(nome_utente)
    
    def aggiungiBrano(self, nome_playlist, percorso_brano) -> str :
        nome_utente = self._gestore_utente.getUtenteCorrente().getNomeUtente()
        playlist:Playlist = self._playlist_repo.getPlaylist(nome_utente, nome_playlist)
        if playlist is None:
            return "ERRORE, playlist inesistente"
        #ora verifico che il brano che voglio aggiungere effettivamente esista
        traccia_trovata=self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso_brano)
        if traccia_trovata is None:
            return "ERRORE, il brano che si desidera aggiungere non esiste nel catalogo globale"
        if playlist.aggiungiTraccia(percorso_brano):
            self._playlist_repo.salvaPlaylist()
            return "SUCCESSO, brano aggiunto alla playlist"
        else:
            return "ERRORE, il brano è già dentro la playlist indicata"
        
    def rimuoviBrano(self, nome_playlist, percorso_brano_rimuovere):
        nome_utente=self._gestore_utente.getUtenteCorrente().getNomeUtente()
        playlist:Playlist=self._playlist_repo.getPlaylist(nome_utente, nome_playlist)
        if playlist is None:
            return "ERRORE, playlist non trovata"
        #uso ora il metodo dell'entity già creato
        if playlist.rimuoviTraccia(percorso_brano_rimuovere):
            self._playlist_repo.salvaPlaylist()
            return "SUCCESSO, traccia rimossa"
        else:
            return "ERRORE, il brano indicato non è presente in questa playlist"
        
    def reportTracceComplete(self, nome_playlist: str) -> list:
        nome_utente = self._gestore_utente.getUtenteCorrente().getNomeUtente()
        playlist: Playlist = self._playlist_repo.getPlaylist(nome_utente, nome_playlist)
        if playlist is None:
            return []
        tracce_complete = [] 
        for percorso in playlist.getTracce():
            traccia = self._gestore_traccia._traccia_repo.cercaPerPercorso(percorso)
            if traccia is not None:
                tracce_complete.append(traccia)
        return tracce_complete


        


