from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFileDialog, QMessageBox, QLineEdit, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

class VistaCatalogo(QWidget):
    # Aggiornato l'__init__ per ricevere il controller playlist e la funzione di navigazione
    def __init__(self, controller_traccia, controller_playlist, on_logout, on_vai_a_playlist, on_vai_a_pedaliera):
        super().__init__()
        
        self._controller = controller_traccia
        self._controller_playlist = controller_playlist
        self._on_logout = on_logout
        self._on_vai_a_playlist = on_vai_a_playlist # Callback verso il Main
        self.on_vai_a_pedaliera=on_vai_a_pedaliera
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # INTESTAZIONE
        layout_header = QHBoxLayout()
        titolo = QLabel("Libreria Audio")
        titolo.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        
        # BOTTONE PER ANDARE ALLE PLAYLIST
        bottone_playlist = QPushButton(" Le Mie Playlist")
        bottone_playlist.setStyleSheet("background-color: #1DB954; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold; margin-right: 10px;")
        bottone_playlist.clicked.connect(self._on_vai_a_playlist)
        
        bottone_logout = QPushButton("Logout")
        bottone_logout.setStyleSheet("background-color: #d32f2f; color: white; padding: 5px 15px; border-radius: 5px;")
        bottone_logout.clicked.connect(self.gestisci_logout)

        bottonePedali = QPushButton("Effetti DSP")
        bottonePedali.setStyleSheet("background-color: #f39c12; color: white; padding: 10px;")
        bottonePedali.clicked.connect(self.on_vai_a_pedaliera)
        
        layout_header.addWidget(titolo)
        layout_header.addStretch()
        layout_header.addWidget(bottone_playlist) # Inserito nell'header
        layout_header.addWidget(bottonePedali)
        layout_header.addWidget(bottone_logout)
        layout.addLayout(layout_header)

        # BARRA STRUMENTI 
        layout_tools = QHBoxLayout()
        self.input_ricerca = QLineEdit()
        self.input_ricerca.setPlaceholderText("🔍 Cerca per titolo o artista...")
        self.input_ricerca.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 5px; background-color: #2b2b2b; color: white;")
        self.input_ricerca.textChanged.connect(self.esegui_ricerca)

        bottone_importa = QPushButton(" Importa Traccia")
        bottone_importa.setStyleSheet("background-color: #333; color: white; padding: 8px 15px; border-radius: 5px;")
        bottone_importa.clicked.connect(self.importa_file)

        layout_tools.addWidget(self.input_ricerca)
        layout_tools.addWidget(bottone_importa)
        layout.addLayout(layout_tools)

        # TABELLA
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["Titolo", "Artista", "Durata", "Percorso Fisico (ID)"])
        self.tabella.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabella.customContextMenuRequested.connect(self.mostra_menu_contestuale)

        self.tabella.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabella.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabella.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella.setDragEnabled(True)
        self.tabella.setStyleSheet("QTableWidget { background-color: #1e1e1e; color: white; }")
        
        layout.addWidget(self.tabella)
        self.setLayout(layout)
        self.aggiorna_tabella()

    def mostra_menu_contestuale(self, posizione):
        #Menu a comparsa con il tasto destro del mouse per gestire eliminazione e aggiunta a playlist
        item = self.tabella.itemAt(posizione)
        if item is None: return
            
        riga_selezionata = item.row()
        percorso_id = self.tabella.item(riga_selezionata, 3).text()
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2b2b2b; color: white; }")
        
        # Sottomenu dinamico per inserire il brano nelle playlist esistenti
        sottomenu_playlist = menu.addMenu(" Aggiungi a Playlist")
        
        # Chiediamo al backend quali playlist possiede l'utente in questo momento
        mie_playlist = self._controller_playlist.mostraMiePlaylist()
        
        # Popoliamo il sottomenu con i nomi delle playlist reali
        if mie_playlist and not isinstance(mie_playlist, str):
            for playlist in mie_playlist:
                nome_p = playlist.getNomePlaylist()
                azione = sottomenu_playlist.addAction(f"📄 {nome_p}")
                # Colleghiamo l'azione usando una funzione lambda per ricordarsi i parametri corretti
                #Nota importante:se avessi messo azione.triggered.connect(self.aggiungi_a_playlist_reale(nome, percorso)) 
                # PyQt la avrebbe eseguita all'istante prima ancora che noi effettivamente clicchiamo sul bottone
                #Per prevenire questo usiamo una funziona provissoria lambda che mi permette di non dover chiamare con le 
                #parentesi self.aggiungi_a_playlist_reale, così il bottone QUANDO PREMUTO esegue la lambda.
                #Tuttavia si presenta anche il problema del ciclo for, infatti lambda non tiene traccia di nome_p ma salva solo
                # un puntatore alla variabile temporanea nome_p. Se non creassimo delle variabili np e pid interne a lambda tutte le playlist
                #seppur mostrando nomi diversi, punterebbero al medesimo nome in memoria (l'ultimo letto dal ciclo for)
                #Così nella variabile temporanea np, pid vengono salvati SUBITO i valori letti dal ciclo for che poi sono passati immediatamente
                # a aggiungi_a_playlist_reale
                azione.triggered.connect(lambda checked, np=nome_p, pid=percorso_id: self.aggiungi_a_playlist_reale(np, pid))
        else:
            azione_vuota = sottomenu_playlist.addAction("Nessuna playlist creata")
            azione_vuota.setEnabled(False)

        menu.addSeparator()
        azione_elimina = menu.addAction(" Elimina dal Catalogo")
        
        azione_scelta = menu.exec(QCursor.pos())
        
        if azione_scelta == azione_elimina:
            self.elimina_traccia_selezionata(riga_selezionata)

    def aggiungi_a_playlist_reale(self, nome_playlist, percorso_brano):
        #Chiama il controller playlist per accoppiare il brano
        esito = self._controller_playlist.aggiungiBrano(nome_playlist, percorso_brano)
        if "SUCCESSO" in esito:
            QMessageBox.information(self, "Aggiunto", esito)
        else:
            QMessageBox.warning(self, "Avviso", esito)

    def elimina_traccia_selezionata(self, riga):
        percorso_id = self.tabella.item(riga, 3).text()
        item_titolo = self.tabella.item(riga, 0).text()
        risposta = QMessageBox.question(self, "Conferma", f"Eliminare '{item_titolo}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if risposta == QMessageBox.StandardButton.Yes:
            if self._controller.rimuoviTraccia(percorso_id):
                QMessageBox.information(self, "Eliminato", "Traccia rimossa!")
                self.aggiorna_tabella()

    def importa_file(self):
        percorso_file, _ = QFileDialog.getOpenFileName(self, "Seleziona Traccia Audio", "", "File Audio (*.mp3 *.wav)")
        if percorso_file:
            esito = self._controller.importaTraccia(percorso_file)
            if esito.startswith("SUCCESSO"):
                self.aggiorna_tabella()

    def esegui_ricerca(self):
        testo = self.input_ricerca.text()
        if testo == "": self.aggiorna_tabella()
        else: self.popola_tabella(self._controller.cercaTracciaNomeArtista(testo))

    def aggiorna_tabella(self):
        self.popola_tabella(self._controller.mostraCatalogo())

    def popola_tabella(self, lista_tracce):
        self.tabella.setRowCount(len(lista_tracce))
        for row, traccia in enumerate(lista_tracce):
            self.tabella.setItem(row, 0, QTableWidgetItem(traccia.getTitolo()))
            self.tabella.setItem(row, 1, QTableWidgetItem(traccia.getArtista()))
            minuti, secondi = int(traccia.getDurata() // 60), int(traccia.getDurata() % 60)
            self.tabella.setItem(row, 2, QTableWidgetItem(f"{minuti}:{secondi:02d}"))
            item_p = QTableWidgetItem(traccia.getPercorso())
            item_p.setForeground(Qt.GlobalColor.gray)
            self.tabella.setItem(row, 3, item_p)

    def gestisci_logout(self): self._on_logout()