import sys
import os

# Configurazione del path per importare i moduli dalle altre cartelle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Repos.utente_repository import UserRepository
from Repos.traccia_audio_repository import TracciaAudioRepository
from Controller.gestore_utente import GestoreUtente
from Controller.gestore_traccia_audio import gestore_traccia_audio
from Boundary.utente_boundary import ConsoleUtente
from Boundary.traccia_boundary import ConsoleCatalogo
from Controller.gestore_coda_riproduzione import GestorePlayer
from Boundary.player_boundary import ConsolePlayer

# --- NUOVI IMPORT PER PLAYLIST ---
from Repos.playlist_repository import PlaylistRepository
from Controller.gestore_playlist import GestorePlaylist
from Boundary.playlist_boundary import ConsolePlaylist

from Models.pedali import PedaleDistorsione, PedaleChorus, PedaleDelay
from Repos.catena_effetti_repository import catena_effetti

# AGGIORNATO: Importazione del nuovo modulo e classe elaboratore
from Controller.elaboratore_catena import ElaboratoreCatena
from Boundary.terminale_effetti_boundary import TerminaleEffettiBoundary  # Importiamo la boundary appena creata

# --- CONTROLLER E REPOSITORY PER I PRESET  ---
from Repos.preset_repos import PresetRepository
from Controller.preset_controller import PresetController

def main():
    # 1. Inizializzazione Repository
    repo_utenti = UserRepository(path="utenti.json")
    repo_tracce = TracciaAudioRepository(path="tracce.json")
    repo_playlist = PlaylistRepository(path="playlist.json")
    
    nome_file = "catena_effetti_attuale.json" 
    repo_effetti = catena_effetti(storage_path=nome_file)
    
    # Inizializzazione repository preset (gestisce presets_archivio.json)
    repo_preset = PresetRepository(path="presets_archivio.json")
    
    # 2. Inizializzazione Controller
    gestore_utente = GestoreUtente(utente_repo=repo_utenti)
    gestore_tracce = gestore_traccia_audio(traccia_repo=repo_tracce)
    gestore_playlist = GestorePlaylist(playlist_repo=repo_playlist, gestore_utente=gestore_utente, gestore_traccia=gestore_tracce)
    gestore_player= GestorePlayer(gestore_tracce, gestore_playlist)
    
    # AGGIORNATO: Inizializzazione del nuovo controller dsp
    controller_effetti = ElaboratoreCatena(repo_effetti)
    
    # Inizializzazione controller preset
    controller_preset = PresetController(catena_repo=repo_effetti, preset_repo=repo_preset)

    # 3. Inizializzazione Boundary
    console_utente = ConsoleUtente(gestore_utente=gestore_utente)
    console_catalogo = ConsoleCatalogo(gestore_traccia=gestore_tracce)
    console_playlist = ConsolePlaylist(gestore_playlist=gestore_playlist)
    console_player=ConsolePlayer(gestore_player)
    
    # AGGIORNATO: Passaggio corretto del parametro percorso_json_tracce
    interfaccia_effetti = TerminaleEffettiBoundary(controller_effetti, repo_effetti, controller_preset, percorso_json_tracce="tracce.json")

    # CARICAMENTO OBBLIGATORIO DATI
    if os.path.exists(nome_file):
        repo_effetti.load_from_json()
    
    # Inizializzazione di backup se il file è vuoto o corrotto
    if all(p is None for p in repo_effetti.pedali_attivi[:3]):
        print("Inizializzazione nuovi pedali...")
        repo_effetti.aggiungi_o_aggiorna(PedaleDistorsione(0, gain=0.9), 0)
        repo_effetti.aggiungi_o_aggiorna(PedaleChorus(1, rate=3.0, depth=0.4), 1)
        repo_effetti.aggiungi_o_aggiorna(PedaleDelay(2, tempo=89.0), 2)

    # LOGIN
    if not console_utente.autenticazioneIniziale():
        print("Uscita...")
        return

    # MENU PRINCIPALE
    while True:
        utente = gestore_utente.getUtenteCorrente()
        print(f"\n--- MENU PRINCIPALE (Utente: {utente.getNomeUtente()}) ---")
        print("1. Catalogo Globale")
        print("2. Mie Playlist")
        print("3. Lettore Audio")
        print("4. Gestione Pedali ed Effetti")
        print("0. Logout")
        
        scelta = input("\nCosa vuoi fare? ").strip()
        
        if scelta == "1":
            console_catalogo.selectMenu()
        elif scelta == "2":
            console_playlist.avvia()  # Aggiunta la chiamata al menu playlist
        elif scelta == "3":
            console_player.avvia()
        elif scelta == "4":
            # Forza la sincronizzazione leggendo dal file prima di mostrare la lista
            repo_preset.carica_archivio()
            preset_salvati = list(repo_preset._presets.keys())
            
            print("\n" + "-"*40)
            if preset_salvati:
                print("PRESET ARCHIVIATI DISPONIBILI:")
                for nome in preset_salvati:
                    print(f" - {nome}")
            else:
                print("Nessun preset presente in archivio.")
            print("-"*40)
            
            interfaccia_effetti.mostra_interfaccia()
        elif scelta == "0":
            break
        else:
            print("Opzione non valida.")

if __name__ == "__main__":
    main()