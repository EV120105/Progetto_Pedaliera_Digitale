import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QVBoxLayout

# Import delle Boundary
from Boundary.utente_gui_boundary import VistaLogin
from Boundary.catalogo_gui import VistaCatalogo
from Boundary.playlist_gui import VistaPlaylist # Assicurati che il file si chiami playlist_gui.py
from Boundary.player_gui import VistaPlayer
from Boundary.dsp_gui import VistaPedaliera

# Import del Backend reale
from Repos.utente_repository import UserRepository
from Repos.traccia_audio_repository import TracciaAudioRepository
from Repos.playlist_repository import PlaylistRepository
from Repos.catena_effetti_repository import catena_effetti
from Repos.preset_repos import PresetRepository

from Controller.gestore_utente import GestoreUtente
from Controller.gestore_traccia_audio import gestore_traccia_audio
from Controller.gestore_playlist import GestorePlaylist
from Controller.gestore_coda_riproduzione import GestorePlayer
from Controller.gestore_catena import CatenaController
from Controller.elaboratore_catena import ElaboratoreCatena
from Controller.preset_controller import PresetController
from Controller.elaborazione_e_rendering_control import ControllerElaborazioneRendering

class DAWApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Master DAW")
        self.setGeometry(100, 100, 1280, 720)
        
        # 1. INIZIALIZZAZIONE COMPLETA DEL BACKEND
        self.repo_utenti = UserRepository()
        self.gestore_utente = GestoreUtente(self.repo_utenti)
        
        self.repo_tracce = TracciaAudioRepository()
        self.gestore_traccia = gestore_traccia_audio(self.repo_tracce)
        
        self.repo_playlist = PlaylistRepository()
        # Il GestorePlaylist ha bisogno di repo, gestore_utente e gestore_traccia
        self.gestore_playlist = GestorePlaylist(self.repo_playlist, self.gestore_utente, self.gestore_traccia)
        
        self.gestore_player = GestorePlayer(self.gestore_traccia, self.gestore_playlist)

        self.repo_catena=catena_effetti()
        self.controller_catena=CatenaController(self.repo_catena)

        self.repo_preset=PresetRepository()
        self.preset_controller=PresetController(self.repo_catena, self.repo_preset)

        self.elaboratore=ElaboratoreCatena(self.repo_catena)

        self.rendering_controller=ControllerElaborazioneRendering(self.repo_tracce)
        
        # 2. AREA PRINCIPALE (Stacked Widget)
        self.area_principale = QStackedWidget()
        
        self.vista_login = VistaLogin(
            controller_utente=self.gestore_utente,
            on_login_success=self.costruisciInterfacciaDaw
        )
        
        self.area_principale.addWidget(self.vista_login) # Indice 0
        self.setCentralWidget(self.area_principale)

    def costruisciInterfacciaDaw(self):
        #Costruisce il Workspace della DAW dopo che il Login ha avuto successo
        
        # Questo conterrà l'intera area di lavoro interna
        pagina_daw_workspace = QWidget()
        layout_globale = QHBoxLayout(pagina_daw_workspace)
        
        # Sotto-stacked widget per scambiare SOLO la parte sinistra (Catalogo / Playlist / Pedaliera)
        self.stack_sinistro = QStackedWidget()
        
        # 1. CREO IL PLAYER FISSO A DESTRA
        self.vista_player_fisso = VistaPlayer(controller_player=self.gestore_player)
        self.vista_player_fisso.setFixedWidth(400) 
        self.vista_player_fisso.setStyleSheet("background-color: #2e2e2e;")
        
        # 2. INIZIALIZZO IL CATALOGO
        # Aggiunto il callback 'on_vai_a_pedaliera' per navigare verso la sezione DSP
        self.vista_catalogo = VistaCatalogo(
            controller_traccia=self.gestore_traccia,
            controller_playlist=self.gestore_playlist,
            on_logout=self.gestisciLogout,
            on_vai_a_playlist=self.vaiAllePlaylist,
            on_vai_a_pedaliera=self.vaiAllaPedaliera # <-- Rotta di navigazione per DSP
        )
        
        # 3. CREO VISTA PLAYLIST
        self.vista_playlist = VistaPlaylist(
            controller_playlist=self.gestore_playlist,
            controller_player=self.gestore_player,
            on_back_to_catalogo=self.vaiAlCatalogo, 
            on_playlist_caricata=self.vista_player_fisso.aggiornaCodaVisiva
        )
        
        # 4. CREO VISTA PEDALIERA DSP (In accordo con tutti i controller passati)
        self.vista_pedaliera = VistaPedaliera(
            catena_controller=self.controller_catena,
            elaboratore_catena=self.elaboratore,
            gestore_traccia=self.gestore_traccia,
            preset_controller=self.preset_controller,
            rendering_controller=self.rendering_controller,
            callback_aggiorna_catalogo=self.aggiornaTabellaDopoExport,
            on_back=self.vaiAlCatalogo
        )
        
        # Assegniamo le diapositive allo stack di sinistra
        self.stack_sinistro.addWidget(self.vista_catalogo)   # Indice 0 dello stack sinistro
        self.stack_sinistro.addWidget(self.vista_playlist)   # Indice 1 dello stack sinistro
        self.stack_sinistro.addWidget(self.vista_pedaliera)  # Indice 2 dello stack sinistro
        
        # Assembliamo la schermata DAW definitiva
        layout_globale.addWidget(self.stack_sinistro)
        layout_globale.addWidget(self.vista_player_fisso)
        
        # Aggiungiamo l'intero blocco DAW allo Stack principale come Indice 1
        self.area_principale.addWidget(pagina_daw_workspace)
        
        # Spostiamo la visualizzazione sul blocco DAW
        self.area_principale.setCurrentIndex(1)
        self.stack_sinistro.setCurrentIndex(0) # Parte mostrando il catalogo

    # --- METODI DI NAVIGAZIONE ---
    def vaiAllePlaylist(self):
        self.vista_playlist.aggiorna_lista_playlist()
        self.vista_player_fisso.show() # <-- RIAPRE IL PLAYER PRINCIPALE
        self.stack_sinistro.setCurrentIndex(1) 
        
    def vaiAlCatalogo(self):
        self.vista_player_fisso.show() # <-- RIAPRE IL PLAYER PRINCIPALE
        self.stack_sinistro.setCurrentIndex(0) 

    def vaiAllaPedaliera(self):
        # 1. Interrompiamo la coda e fermiamo Pygame
        self.gestore_player.svuotaCoda()
        self.vista_player_fisso.gestisciStop()
        
        # 2. NASCONDIAMO IL PLAYER PRINCIPALE 
        self.vista_player_fisso.hide()
        
        # 3. Forziamo il refresh delle tracce e dei preset
        self.vista_pedaliera.aggiornaListaTracce()
        self.vista_pedaliera.aggiornaListaPreset()
        
        # 4. Spostiamo la diapositiva sulla pedaliera
        self.stack_sinistro.setCurrentIndex(2)

    def aggiornaTabellaDopoExport(self):
        #Callback per ricaricare la tabella del catalogo visivo quando viene generato un WAV#
        self.vista_catalogo.aggiorna_tabella_catalogo()
        self.vista_player_fisso.show() # <-- RIAPRE IL PLAYER PRINCIPALE
        self.stack_sinistro.setCurrentIndex(0) 

    def gestisciLogout(self):
        self.gestore_player.stop()
        self.vista_player_fisso.hide() # Nascondiamo il player anche nella schermata di login
        self.area_principale.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    finestra = DAWApp()
    finestra.show()
    sys.exit(app.exec())