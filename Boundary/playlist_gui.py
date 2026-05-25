from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt

class VistaPlaylist(QWidget):
    def __init__(self, controller_playlist, controller_player, on_back_to_catalogo, on_playlist_caricata):
        super().__init__()
        self._controller = controller_playlist
        self._controller_player=controller_player
        self._on_back = on_back_to_catalogo # Funzione per tornare al catalogo
        self._on_playlist_caricata=on_playlist_caricata
        self.playlist_corrente = None # Ricorda quale playlist stiamo guardando
        
        # LAYOUT PRINCIPALE (Diviso a metà: SX e DX)
        layout_principale = QHBoxLayout()
        layout_principale.setContentsMargins(20, 20, 20, 20)
        
        
        # PARTE SINISTRA: La lista delle Playlist

        
        layout_sx = QVBoxLayout()
        
        btn_indietro = QPushButton("⬅ Torna al Catalogo")
        btn_indietro.setStyleSheet("background-color: #555; color: white; padding: 8px; border-radius: 5px;")
        btn_indietro.clicked.connect(self._on_back)
        layout_sx.addWidget(btn_indietro)
        
        titolo_sx = QLabel("Le Mie Playlist")
        titolo_sx.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 15px;")
        layout_sx.addWidget(titolo_sx)
        
        # Il widget lista che mostrerà i nomi delle playlist
        self.lista_playlist = QListWidget()
        self.lista_playlist.setStyleSheet("background-color: #1e1e1e; color: white; font-size: 16px; padding: 5px; border-radius: 5px;")
        self.lista_playlist.itemClicked.connect(self.seleziona_playlist) # Quando clicchi una voce
        layout_sx.addWidget(self.lista_playlist)
        
        # Bottoni per Creare e Eliminare
        layout_btn_sx = QHBoxLayout()
        btn_crea = QPushButton(" Crea Nuova")
        btn_crea.setStyleSheet("background-color: #1DB954; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_crea.clicked.connect(self.crea_playlist)
        
        btn_elimina = QPushButton(" Elimina")
        btn_elimina.setStyleSheet("background-color: #d32f2f; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_elimina.clicked.connect(self.elimina_playlist)
        
        layout_btn_sx.addWidget(btn_crea)
        layout_btn_sx.addWidget(btn_elimina)
        layout_sx.addLayout(layout_btn_sx)

        
        # PARTE DESTRA: Le tracce della playlist


        layout_dx = QVBoxLayout()
        
        self.titolo_dx = QLabel("Seleziona una playlist...")
        self.titolo_dx.setStyleSheet("font-size: 24px; font-weight: bold; color: #1DB954;")
        layout_dx.addWidget(self.titolo_dx)
        self.btn_ascolta_playlist=QPushButton("▶ Ascolta l'intera Playlist")
        self.btn_ascolta_playlist.setStyleSheet("background-color: #1DB954; color: white; padding: 10px; font-weight: bold; border-radius: 5px; font-size: 16px; margin-bottom: 10px;")
        self.btn_ascolta_playlist.clicked.connect(self.suona_tutta_playlist)
        self.btn_ascolta_playlist.hide() #tengo il bottone nascosto fin quando non seleziono una playlist
        layout_dx.addWidget(self.btn_ascolta_playlist)


        # Stessa tabella usata nel catalogo
        self.tabella_tracce = QTableWidget()
        self.tabella_tracce.setColumnCount(4)
        self.tabella_tracce.setHorizontalHeaderLabels(["Titolo", "Artista", "Durata", "Percorso Fisico (ID)"])
        self.tabella_tracce.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabella_tracce.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabella_tracce.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella_tracce.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella_tracce.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; gridline-color: #333; }
            QHeaderView::section { background-color: #2b2b2b; color: white; padding: 5px; font-weight: bold; border: 1px solid #333; }
        """)
        layout_dx.addWidget(self.tabella_tracce)
        
        btn_rimuovi_traccia = QPushButton("Rimuovi Traccia Selezionata dalla Playlist")
        btn_rimuovi_traccia.setStyleSheet("background-color: #ff9800; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_rimuovi_traccia.clicked.connect(self.rimuovi_traccia)
        layout_dx.addWidget(btn_rimuovi_traccia)
        
        # Assemblo i layout (la parte sinistra prende 1/3 dello spazio, la destra 2/3)
        layout_principale.addLayout(layout_sx, 1)
        layout_principale.addLayout(layout_dx, 2)
        
        self.setLayout(layout_principale)

    # ================= LOGICA =================

    def aggiorna_lista_playlist(self):
        #Chiede al controller le playlist dell'utente e popola la tendina sinistra
        self.lista_playlist.clear()
        playlists = self._controller.mostraMiePlaylist()
        
        if isinstance(playlists, str): # Se restituisce un errore 
            return
            
        for p in playlists:
            self.lista_playlist.addItem(p.getNomePlaylist())
            
        # Reset parte destra
        self.titolo_dx.setText("Seleziona una playlist...")
        self.tabella_tracce.setRowCount(0)
        self.playlist_corrente = None

    def crea_playlist(self):
        # QInputDialog apre un comodo popup nativo per chiedere testo all'utente
        nome, ok = QInputDialog.getText(self, "Nuova Playlist", "Inserisci il nome della playlist:")
        if ok and nome.strip():
            esito = self._controller.creaPlaylist(nome.strip())
            if "SUCCESSO" in esito:
                self.aggiorna_lista_playlist()
            else:
                QMessageBox.warning(self, "Errore", esito)

    def elimina_playlist(self):
        item_selezionato = self.lista_playlist.currentItem()
        if not item_selezionato:
            return
            
        nome = item_selezionato.text()
        risposta = QMessageBox.question(self, "Conferma", f"Eliminare la playlist '{nome}'?")
        if risposta == QMessageBox.StandardButton.Yes:
            self._controller.rimuoviPlaylist(nome)
            self.aggiorna_lista_playlist()

    def seleziona_playlist(self, item):
        #Si attiva quando clicchi una playlist a sinistra. Popola la tabella a destra
        nome = item.text()
        self.playlist_corrente = nome
        self.titolo_dx.setText(f" {nome}")
        self.btn_ascolta_playlist.show()
        self.aggiorna_tabella_tracce()

    def aggiorna_tabella_tracce(self):
        if not self.playlist_corrente: return
        
        # Usa il metodo che restituisce gli oggetti TracciaAudio
        tracce = self._controller.reportTracceComplete(self.playlist_corrente)
        
        self.tabella_tracce.setRowCount(len(tracce))
        for row, traccia in enumerate(tracce):
            self.tabella_tracce.setItem(row, 0, QTableWidgetItem(traccia.getTitolo()))
            self.tabella_tracce.setItem(row, 1, QTableWidgetItem(traccia.getArtista()))
            self.tabella_tracce.setItem(row, 2, QTableWidgetItem(str(traccia.getDurata())))
            
            item_percorso = QTableWidgetItem(traccia.getPercorso())
            item_percorso.setForeground(Qt.GlobalColor.gray)
            self.tabella_tracce.setItem(row, 3, item_percorso)

    def rimuovi_traccia(self):
        if not self.playlist_corrente: return
        
        riga_selezionata = self.tabella_tracce.currentRow()
        if riga_selezionata < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima una traccia da rimuovere!")
            return
            
        # Il percorso è sempre l'ID univoco nella colonna 3
        percorso = self.tabella_tracce.item(riga_selezionata, 3).text()
        esito = self._controller.rimuoviBrano(self.playlist_corrente, percorso)
        
        if "SUCCESSO" in esito:
            self.aggiorna_tabella_tracce() # Ricarica i brani aggiornati
        else:
            QMessageBox.warning(self, "Errore", esito)

    def suona_tutta_playlist(self):
        #richiama il controller per svuotare la coda e inserire i brani
        if not self.playlist_corrente:return
        esito=self._controller_player.caricaPlaylistInCoda(self.playlist_corrente)
        if "SUCCESSO" in esito:
            #Chiamo la funzione che dal main mi aggiorna la vista dei brni in coda
            self._controller_player.playIndice(0)
            self._on_playlist_caricata()
            QMessageBox.information(self, "In riproduzione", f"La Playlist {self.playlist_corrente} è stata caricata in coda")
        else:
            QMessageBox.warning(self, "Errore", esito)