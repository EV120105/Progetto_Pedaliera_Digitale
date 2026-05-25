from Models.utente import UtenteAutenticato
import json
class UserRepository:
    def __init__(self, path = "utenti.json"):
        self._utenti={} 
        self._path=path 
        self.letturaUtenti()
    def tutti(self) -> list:
        return list(self._utenti.values())
    def letturaUtenti(self):
        try:
            with open (self._path, "r", encoding="utf-8") as f:
                dati:list=json.load(f)
                #Siccome il mio file utenti.json è una lista di dizionari del tipo 
                #[{"nome_utente_1":val, "password":val}, etc...]
                #Anche dati sarà di tipo lista
                #Mi restituisce in definitiva i dizionari di utenti.json
                #A questo punto possiamo scorrere il dizionario di ogni utente e chiamare il fromDict
                #Per aggiornare self.utenti che è un dizionario di oggeti UtenteAutenticato, usiamo la dictionary comprehension
                self._utenti={d["nome_utente"]:UtenteAutenticato.fromDict(d) for d in dati} 
                #cioè scorrendo ogni d (dizionario) in dati creo varie istanze di UtenteAutenticato di nome
                #d["nome_utente"] così che alla fine avrò il dizionario utenti del tipo
                #self.utenti{nome_utente1, nome_utente_2} dove ciascun elemento è una istanza di UtenteAutenticato
                return self._utenti    
        except  FileNotFoundError:
            self._utenti={}
            return self._utenti
    def salvaUtenti(self):
        try:
            with open (self._path, "w", encoding="utf-8") as f:
                #Creiamo una lista di dizionari con la list comprehension
                #Sta volta prendiamo ogni u in self.utenti.values (valori del dict self.utenti che sono appunto oggetti UtenteAutenticato)
                #e li passiamo a toDict già definita nell'entity
                lista_utenti=[u.toDict() for u in self._utenti.values()]
                #A questo punto scriviamo la lista di dizionari lista_utenti sul file aggiornandolo
                json.dump(lista_utenti, f, indent=4)
        except IOError:
            return "Errore durante il salvataggio file"
    def trovaNome(self, nome_utente:str) -> "UtenteAutenticato":
            return self._utenti.get(nome_utente)
    def aggiungiUtente(self, nuovo_utente:"UtenteAutenticato"):
         self._utenti[nuovo_utente.getNomeUtente()]=nuovo_utente
         #Aggiorniamo la lista in memoria
         self.salvaUtenti()

        