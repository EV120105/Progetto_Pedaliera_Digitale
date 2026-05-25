from Controller.gestore_utente import GestoreUtente

class ConsoleUtente:
    def __init__(self, gestore_utente: GestoreUtente):
        self._gestore = gestore_utente

    def autenticazioneIniziale(self):
        """Metodo principale che fa partire il loop della console"""
        while self._gestore.getUtenteCorrente() is None:
            print("\n" + "="*30)
            print("   SISTEMA PEDALIERA DIGITALE")
            print("="*30)
            print("1. Login")
            print("2. Registrazione")
            print("3. Mostra tutti gli utenti (Debug)")
            print("0. Esci")
            
            scelta = input("\nScegli un'opzione: ")
            
            if scelta == "1":
                self._schermata_login()
            elif scelta == "2":
                self._schermata_registrazione()
            elif scelta == "3":
                self._schermata_lista_utenti()
            elif scelta == "0":
                print("Chiusura del programma...")
                break
            else:
                print("Scelta non valida. Riprova.")
            if self._gestore.getUtenteCorrente():
                print(f"\nAutenticazione riuscita! Benvenuto {self._gestore.getUtenteCorrente().getNomeUtente()}")
                return True

    def _schermata_login(self):
        print("\n--- LOGIN ---")
        nome = input("Username: ")
        password = input("Password: ")
        
        risultato = self._gestore.loginUtente(nome, password)
        print(f"\n>>> ESITO: {risultato}")
        
        # Se c'è l'errore specifico che hai impostato, guidiamo l'utente
        if risultato == "Errore, Utente inesistente, Creazione nuovo Utente":
            print("Vuoi procedere alla registrazione? (s/n)")
            scelta = input().lower()
            if scelta == 's':
                self._schermata_registrazione(nome_preimpostato=nome)

    def _schermata_registrazione(self, nome_preimpostato=None):
        print("\n--- REGISTRAZIONE ---")
        
        if nome_preimpostato:
            nome = nome_preimpostato
            print(f"Username: {nome}")
        else:
            nome = input("Username: ")
            
        password = input("Password: ")
        email = input("Email: ")
        print("Livelli disponibili: Principiante, Intermedio, Avanzato")
        livello = input("Livello: ")
        
        risultato = self._gestore.registraUtente(nome, password, email, livello)
        print(f"\n>>> ESITO: {risultato}")

    def _schermata_lista_utenti(self):
        print("\n--- LISTA UTENTI REGISTRATI ---")
        utenti = self._gestore.mostraListaUtenti()
        if not utenti:
            print("Nessun utente registrato.")
        else:
            for u in utenti:
                # Usa il metodo __str__ che hai definito nell'Entity!
                print(f"- {u}")