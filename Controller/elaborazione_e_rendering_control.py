import os
from Models.traccia import TracciaAudio

class ControllerElaborazioneRendering:
    def __init__(self, repository_tracce):
        
        #Il controller ha bisogno della repository per salvare 
        #i metadati della nuova traccia creata.
        
        self.repo = repository_tracce

    def esegui_rendering_esportazione(self, percorso_sorgente, catena_pedali):

        #UC6: Gestisce l'intero flusso di processing offline e persistenza fisica.
        
        # 1. RECUPERO TRACCIA (DA REPOSITORY)
        traccia_orig = self.repo.cercaPerPercorso(percorso_sorgente)
        if not traccia_orig:
            return "Errore: Traccia originale non trovata."

        # 2. ELABORAZIONE DSP OFFLINE
        # Prendiamo i campioni (array di float) dalla traccia
        campioni = traccia_orig.getCampioni()
        
        # Applichiamo la catena di effetti sequenzialmente
        segnale_elaborato = campioni
        for pedale in sorted(catena_pedali, key=lambda p: p.posizione):
            if not pedale.bypass:
                # La logica matematica risiede nel Model del pedale
                segnale_elaborato = pedale.applica_effetto(segnale_elaborato)

        # 3. PERSISTENZA FISICA (FILE SYSTEM)
        # Generiamo il nuovo percorso per il file .wav
        nome_file, ext = os.path.splitext(percorso_sorgente)
        percorso_export = f"{nome_file}_elaborato{ext}"

        try:
            # Simulazione della scrittura binaria su disco
            self._scrivi_file_wav(percorso_export, segnale_elaborato)
        except IOError:
            # Ramo alternativo del diagramma: Errore I/O
            return "Errore I/O: Impossibile scrivere il file su disco."

        # 4. CREAZIONE ISTANZA E AGGIORNAMENTO REPOSITORY
        # Creiamo l'oggetto TracciaAudio che rappresenta il risultato
        nuova_traccia = TracciaAudio(
            formato=traccia_orig.getFormato(),
            durata=traccia_orig.getDurata(),
            titolo=f"{traccia_orig.getTitolo()} (Processed)",
            artista=traccia_orig.getArtista(),
            percorso=percorso_export
        )
        nuova_traccia.setCampioni(segnale_elaborato)
        
        # Salvataggio nel catalogo JSON tramite la repository
        self.repo.aggiungiTraccia(nuova_traccia)

        return "EsitoSuccesso: Rendering e Esportazione completati."

    def _scrivi_file_wav(self, percorso, dati):
        #Metodo privato che simula l'interazione con il File System dell'OS.
        print(f"[File System] Scrittura di {len(dati)} campioni in corso...")
        # Qui andrebbe l'effettiva scrittura binaria (es. libreria wave o scipy)