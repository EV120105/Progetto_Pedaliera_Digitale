from Repos.catena_effetti_repository import catena_effetti

class CatenaController:
    def __init__(self, repository: catena_effetti):
        self.repo = repository

    def set_parametro_pedale(self, posizione, nuovi_parametri):
        #Sequenza Principale UC5: regola un parametro.
        #Sequenza Alternativa: Valori Fuori Scala.
    
        pedale = self.repo.get_pedale(posizione)
        
        if pedale is None:
            print("Errore: Posizione Vuota") # Segue diagramma UC5
            return

        # Backup per ripristino in caso di errore (Sequenza Alternativa)
        vecchio_stato = pedale.parametri.copy()

        try:
            # Validazione logica DSP
            for k, v in nuovi_parametri.items():
                if k == "gain" and not (0 <= v <= 1):
                    raise ValueError("Gain fuori scala (0-1)")
            
            # Aggiornamento variabili stato interne
            pedale.imposta_parametri(nuovi_parametri)
            self.repo.save_to_json() # Esito: Catena DSP aggiornata
            print("Sistema: Parametri validati e salvati.")

        except ValueError as e:
            # Ripristino ultimo stato valido
            pedale.parametri = vecchio_stato
            print(f"Alert: {e}. Stato ripristinato.")