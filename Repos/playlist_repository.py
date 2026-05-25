from Models.playlist import Playlist
import json
class PlaylistRepository():
    def __init__(self, path="playlist.json"):
        self._path=path
        self._playlists={}
        self.letturaPlaylist()
        #L'idea è di creare self.playlist come segue: {"proprietario": lista oggetti Playlist associate al proprietario}
        #dunque un dizionario con keys i nome utenti e come values liste di oggetti playlist
    def getPathPlaylistRepo(self):
        return self._path
    def letturaPlaylist(self):
        try:
            with open (self._path, "r", encoding="utf-8") as f:
                dati:list = json.load(f)
                #dati sarà della forma lista cioè come segue  
                # [{proprietario_1, nome_playlist_1, lista_tracce1}...etc]  
                for d in dati:
                    p=Playlist.fromDict(d)
                    #Ora creo la chiave per il dizionario playlists, affinchè sia univoca (siccome più utenti possono avere più playlist)
                    #uso una combinazione di nome utente e titolo playlist
                    chiave=f"{p.getProprietario()}_{p.getNomePlaylist()}"
                    self._playlists[chiave]=p
                #in questa maniera la repo discrimina le playlist a seconda del proprietario
        except (FileNotFoundError, json.JSONDecodeError):
            self._playlists={}
    def salvaPlaylist(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                #preparo la lista per salvarla nel json
                lista_Playlists=[p.toDict() for p in self._playlists.values()]
                json.dump(lista_Playlists, f, indent=4)
        except IOError:
            return "ERRORE durante il salvataggio su disco"
    def aggiungiPlaylist(self, nuova_plylist:Playlist):
        #anche qui ricreo la chiave per la nuova playlist
        chiave=f"{nuova_plylist.getProprietario()}_{nuova_plylist.getNomePlaylist()}"
        self._playlists[chiave]=nuova_plylist
        self.salvaPlaylist()
    def rimuoviPlaylist(self,proprietario,nome_playlist):
        chiave=f"{proprietario}_{nome_playlist}"
        if chiave in self._playlists:
            self._playlists.pop(chiave)
            self.salvaPlaylist()
            return True
        else:
            return False
    def getPlaylistPerUtente(self, proprietario_input)->list:
        #questo metodo restituisce tutte le playlist correnti associate ad un certo utente come lista di oggetti Playlist
        risultato=[]
        for p in self._playlists.values():
            p:Playlist
            if p.getProprietario()==proprietario_input:
                risultato.append(p)
        return risultato
    def getPlaylist(self,proprietario_input, nome_playlist_input):
        #questo metodo invece cerca una singola playlist specifica di un certo utente 
        chiave=f"{proprietario_input}_{nome_playlist_input}"
        return self._playlists.get(chiave)
        #così facendo ritorna la playlist cercata o None se non esiste
    
    