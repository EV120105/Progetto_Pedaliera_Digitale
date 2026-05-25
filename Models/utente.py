from abc import ABC, abstractmethod
class Utente(ABC):
    def __init__(self, nome_utente:str):
        self._nome_utente=nome_utente
    @abstractmethod
    def isAutenticato(self)->bool:
        #Questo è un metodo astratto, non ha corpo (pass).
        #Obbliga tutte le classi figlie a implementare questo metodo,
        #altrimenti Python darà errore.
        pass
class UtenteAutenticato(Utente): 
    def __init__(self, nome_utente, hash_password:str, email:str, livello: str):
        super().__init__(nome_utente)
        self._hash_password=hash_password
        self._email=email
        self._livello=livello
    #Ora definiamo i vari getter degli attributi    
    def getNomeUtente(self)->str:
        return self._nome_utente
    def getHashPassword(self)->str:
        return self._hash_password
    def getEmail(self)->str:
        return self._email
    def getLivello(self)->str:
        return self._livello
    def isAutenticato(self) -> bool:
        return True
    #Infine i metodi to dict e from dict per interagire con le repo
    def toDict(self):
        return {
            "nome_utente":self._nome_utente,
            "hash_password":self._hash_password,
            "email":self._email,
            "livello":self._livello
        }
    @classmethod
    def fromDict(cls, dati: dict) -> "UtenteAutenticato":
        return cls(dati["nome_utente"], dati["hash_password"], dati["email"], dati["livello"])
    #Mettiamo anche il dunder method __str__ per far capire cosa vuol dire printare un utente
    def __str__(self) -> str:
        return f"{self._nome_utente} ({self._livello}) - {self._email}"

        