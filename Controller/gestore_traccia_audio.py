import os
from tinytag import TinyTag, TinyTagException
from Models.traccia import TracciaAudio
from Repos.traccia_audio_repository import TracciaAudioRepository

class gestore_traccia_audio:
    def __init__(self, traccia_repo: TracciaAudioRepository):
        self._traccia_repo = traccia_repo

    def importaTraccia(self, percorso: str) -> str:
        if not percorso: 
            return "ERRORE: Percorso vuoto o non valido."
            
        if not os.path.exists(percorso):
            return "ERRORE: Nessun file trovato al percorso specificato."

        if self._traccia_repo.cercaPerPercorso(percorso) is not None:
            return "ERRORE: Questa traccia è già presente nel catalogo."

        # 2. Estrazione dati reali con TinyTag
        try:
            tag = TinyTag.get(percorso)
            
            # Se il file audio non ha i tag compilati, usiamo dei valori di fallback (es. il nome del file)
            titolo = tag.title if tag.title else os.path.splitext(os.path.basename(percorso))[0]
            artista = tag.artist if tag.artist else "Sconosciuto"
            durata = round(tag.duration, 2) if tag.duration else 0.0
            
            # L'estensione la prendiamo comunque dal percorso reale
            _, estensione = os.path.splitext(percorso)
            formato_pulito = estensione.replace(".", "").lower()

            # 3. Creazione e salvataggio
            nuova = TracciaAudio(
                formato=formato_pulito, 
                durata=durata, 
                titolo=titolo, 
                artista=artista, 
                percorso=percorso
            )
            
            self._traccia_repo.aggiungiTraccia(nuova)
            return f"SUCCESSO: Traccia '{titolo}' importata correttamente!"
            
        except TinyTagException:
            return "ERRORE: Formato file non supportato o file audio corrotto."
        except Exception as e:
            return f"ERRORE imprevisto durante l'importazione: {str(e)}"

    def mostraCatalogo(self):
        return self._traccia_repo.tutti()

    def rimuoviTraccia(self, percorso: str):
        return self._traccia_repo.rimuoviTraccia(percorso)
        
    def cercaTracciaNomeArtista(self, parola_chiave: str) -> list:
        risultati = []
        for t in self._traccia_repo.tutti():
            titolo = t.getTitolo().lower()
            artista = t.getArtista().lower()
            chiave = parola_chiave.lower()
            if chiave in titolo or chiave in artista:
                risultati.append(t)
        return risultati