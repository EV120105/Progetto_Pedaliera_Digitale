import hashlib
from Repos.utente_repository import UserRepository
from Models.utente import UtenteAutenticato
class GestoreUtente:
    def __init__(self, utente_repo: UserRepository):
        self._utente_repo=utente_repo
        #Non devo chiamare letturaUtenti, questo avviene già in automatico quando istanzio utente_repo
        self._utente_corrente=None
        #Come utente_corrente metto None perchè all'avvio non ci sarà
        # subito un Utente_Autenticato
    def verificaHashPassword(self, password_in_chiaro_input, password_hash_salvata)->bool:
            if password_hash_salvata==hashlib.sha256(password_in_chiaro_input.encode()).hexdigest():
                return True
            else:
                return False
    def verificaUtente(self, nome_utente:str)-> bool :
        utente=self._utente_repo.trovaNome(nome_utente)
        if utente is not None:
            return True
        else:
            return False
    def registraUtente(self, nome, password_in_chiaro, email, livello):
        # Validazione del formato dati
        if "@" not in email or "." not in email:
            return "ERRORE_EMAIL"
        if livello not in ["Principiante", "Intermedio", "Avanzato"]: # Validazione livelli
            return "ERRORE_LIVELLO"
        hash_password=hashlib.sha256(password_in_chiaro.encode()).hexdigest()
        nuovo_utente=UtenteAutenticato(nome, hash_password, email, livello)
        self._utente_repo.aggiungiUtente(nuovo_utente)
        self._utente_corrente=nuovo_utente
        return "Creazione nuovo Utente avvenuta con successo"
    def loginUtente (self, nome, password_in_chiaro_input):
        utente_trovato=self._utente_repo.trovaNome(nome)
        if self.verificaUtente(nome) is False:
            #A questo punto il sistema entrerà nella funzione di registrazione richiedendo i dati integrativi
            #quali email e livello
            return "Errore, Utente inesistente, Creazione nuovo Utente"
        #Arrivati qui vuol dire che il nome inserito esiste
        #Allora non ci resta che confrontare hash delle password 
        elif self.verificaHashPassword(password_in_chiaro_input, utente_trovato.getHashPassword()):
            self._utente_corrente=utente_trovato 
            return "Login avvenuto con successo"
        else:
            return "La password inserita è errata"
    def mostraListaUtenti(self):
        return self._utente_repo.tutti()
    def getUtenteCorrente(self):
        return self._utente_corrente