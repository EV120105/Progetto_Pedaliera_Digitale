from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSlider, QLabel, QListWidget, QAbstractItemView,
                             QMessageBox, QTableWidget, QSizePolicy, QMenu)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, QTimer

# PARTE RELATIVA ALL'IMPLEMENTAZIONE DEL DRAG AND DROP

class ListaCodaDrop(QListWidget):
    #questa classe deve accettare il drag and drop da catalogo
    def __init__(self, controller_player, on_drop_success):
        super().__init__()
        self._controller=controller_player
        self._on_drop_success=on_drop_success #Richiamerò questa variabile per caricare la lista in coda
        #Devo abilitare due drag and drop uno per ricevere (dall'esterno) e uno per riordinare (interno)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        #Abilito il tasto destro per rimuovere una traccia specifica dalla coda
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mostra_menu_contestuale)

    def dragEnterEvent(self, event):
        #funzione per accettare il trascinamento proveniente da tabella(il catalogo)
        if isinstance(event.source(), QTableWidget) or event.source()==self:
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        sorgente=event.source()
        #Qui dobbiamo distinguere i due casi 
        #--- CASO 1 ---
        #accettiamo il drop esterno
        if isinstance(sorgente, QTableWidget):
            riga=sorgente.currentRow()
            if riga>=0:
                #Estraiamo l'id che serve per le varie funzioni dei controller
                percorso=sorgente.item(riga, 3).text()
                #Aggiungiamo in coda tramite il controller
                self._controller.aggiungiInCoda(percorso)
                self._on_drop_success()#richiamo la variabile per aggiornare la coda
            event.accept()
        #--- CASO 2 ---
        #drag and drop interno per riordinare
        elif sorgente == self:
            riga_partenza=self.currentRow()
            #Calcolo la riga esatta in cui si trova il mouse al rilascio
            posizione_mouse=event.position().toPoint()
            item_sotto_mouse=self.itemAt(posizione_mouse)
            if item_sotto_mouse is None:
                riga_arrivo=self.count()-1
            else:
                riga_arrivo=self.row(item_sotto_mouse)
            if riga_partenza!=riga_arrivo and riga_partenza>=0:
                self._controller.spostaInCoda(riga_partenza, riga_arrivo)
                self._on_drop_success()
            event.accept()
            

    def mostra_menu_contestuale(self, posizione):
        item=self.itemAt(posizione)
        if item is None: return
        riga_selezionata=self.row(item)
        #Creo il menù
        menu=QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; } QMenu::item:selected { background-color: #d32f2f; }")
        azione_elimina=menu.addAction("Rimuovi dalla coda")    
        azione_scelta=menu.exec(QCursor.pos())
        if azione_scelta==azione_elimina:
            #chiamo il controller ed aggiorno la grafica
            esito=self._controller.rimuoviPerIndice(riga_selezionata)
            if "ERRORE" in esito:
                QMessageBox.warning(self,"Attenzione", esito)
            QTimer.singleShot(10, self._on_drop_success) #serve per attendere 10 ms prima della chiusura
            #del menu a comparsa e poi esegue self.on_drop_success altrimenti andrebbero in conflitto
            #creando dei bug visivi


#   --- EFFETTIVA PARTE DEL PLAYER --- 
class VistaPlayer(QWidget):
    def __init__(self, controller_player):
        super().__init__()
        self._controller = controller_player

        # Timer per l'aggiornamento della barra
        self.timerAudio = QTimer()
        self.timerAudio.timeout.connect(self.aggiornaStatoAudio)

        # Il Layout Principale (Verticale) che conterrà tutto
        layoutPrincipale = QVBoxLayout()
        layoutPrincipale.setContentsMargins(15, 20, 15, 20)
        layoutPrincipale.setSpacing(15) # Aggiunge un po' di respiro tra una riga e l'altra!

        # --- 1. SEZIONE TITOLO ---
        self.Titolo = QLabel("Nessun Brano")
        self.Titolo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.Titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutPrincipale.addWidget(self.Titolo)

        # --- 2. SEZIONE BARRA DI AVANZAMENTO ---
        layoutAvanzamento = QHBoxLayout()
        
        self.TempoCorrente = QLabel("0:00")
        self.TempoCorrente.setStyleSheet("color: #aaa;")
        
        self.sliderAvanzamento = QSlider(Qt.Orientation.Horizontal)
        self.sliderAvanzamento.setEnabled(False)
        self.sliderAvanzamento.setStyleSheet("QSlider::handle:horizontal { background: #1DB954; border-radius: 5px; }")
        
        self.TempoTotale = QLabel("0:00")
        self.TempoTotale.setStyleSheet("color: #aaa;")

        layoutAvanzamento.addWidget(self.TempoCorrente)
        layoutAvanzamento.addWidget(self.sliderAvanzamento)
        layoutAvanzamento.addWidget(self.TempoTotale)
        
        layoutPrincipale.addLayout(layoutAvanzamento)

        # --- 3. SEZIONE CONTROLLI CODA (VERSIONE BELLA E BLINDATA) ---
        layoutControlli = QHBoxLayout()

        self.btnShuffle = QPushButton("🔀")
        self.btnStop = QPushButton("⏹")
        self.btnPlayPausa = QPushButton("▶ / ⏸")
        self.btnNext = QPushButton("⏭")
        self.btnRepeat = QPushButton("🔁")

        # Stile speciale per il Play (Cerchio verde blindato)
        self.btnPlayPausa.setFixedSize(50, 50)
        self.btnPlayPausa.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btnPlayPausa.setStyleSheet("background-color: #1DB954; color: white; border-radius: 25px; font-size: 16px; font-weight: bold; margin: 0px; padding: 0px;")
        
        # Stile per le altre icone
        stile_icone = "background-color: transparent; color: white; font-size: 24px; margin: 0px; padding: 0px; border:none; outline:none;"
        
        for btn in [self.btnShuffle, self.btnStop, self.btnNext, self.btnRepeat]:
            btn.setFixedSize(40, 40)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(stile_icone)

        self.btnShuffle.clicked.connect(self.gestisciShuffle)
        self.btnStop.clicked.connect(self.gestisciStop)
        self.btnPlayPausa.clicked.connect(self.gestisciPlayPausa)
        self.btnNext.clicked.connect(self.gestisciNext)
        self.btnRepeat.clicked.connect(self.gestisciRepeat)

        # Centratura con molle
        layoutControlli.addStretch()
        layoutControlli.addWidget(self.btnShuffle)
        layoutControlli.addWidget(self.btnStop)
        layoutControlli.addWidget(self.btnPlayPausa)
        layoutControlli.addWidget(self.btnNext)
        layoutControlli.addWidget(self.btnRepeat)
        layoutControlli.addStretch()

        layoutPrincipale.addLayout(layoutControlli)
        
        # --- 4. SEZIONE VOLUME ---
        layoutVolume = QHBoxLayout()
        etichettaVolume = QLabel("🔊")
        etichettaVolume.setStyleSheet("color: white;")
        
        self.sliderVolume = QSlider(Qt.Orientation.Horizontal)
        self.sliderVolume.setRange(0, 100)
        self.sliderVolume.setValue(int(self._controller._coda.getVolume() * 100))
        self.sliderVolume.valueChanged.connect(self.gestisciVolume)

        layoutVolume.addWidget(etichettaVolume)
        layoutVolume.addWidget(self.sliderVolume)
        
        layoutPrincipale.addLayout(layoutVolume)

        # --- 5. SEZIONE INTESTAZIONE CODA E TASTO SVUOTA ---
        layoutTitoloCoda = QHBoxLayout()
        
        etichettaCoda = QLabel("In Coda:")
        etichettaCoda.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.btnSvuota = QPushButton("🗑 Svuota")
        self.btnSvuota.setStyleSheet("background-color: transparent; color: #d32f2f; font-weight: bold; font-size: 14px;")
        self.btnSvuota.clicked.connect(self.gestisciSvuotaCoda)

        layoutTitoloCoda.addWidget(etichettaCoda)
        layoutTitoloCoda.addStretch()
        layoutTitoloCoda.addWidget(self.btnSvuota)
        
        layoutPrincipale.addLayout(layoutTitoloCoda)

        # --- 6. SEZIONE LISTA CODA ---
        self.listaCoda = ListaCodaDrop(self._controller, self.aggiornaCodaVisiva)
        self.listaCoda.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #333; padding: 5px; font-size: 13px;")
        self.listaCoda.doubleClicked.connect(self.playDaCoda)
        
        layoutPrincipale.addWidget(self.listaCoda)

        # Infine, applichiamo il layout principale alla Vista
        self.setLayout(layoutPrincipale)




# ----  FINE PARTE GRAFICA INIZIO LOGICA DA COLLEGARE AI VARI BOTTONI ---

    def aggiornaCodaVisiva(self):
        #Serve per caricare i nomi dei brani in listaCoda
        self.listaCoda.clear()
        elementi=self._controller.visualizzaCoda()
        for el in elementi:
            self.listaCoda.addItem(el)
        #Aggiorno il titolo del brano corrente
        percorso_corrente=self._controller._coda.getTracciaCorrente()
        if percorso_corrente:
            traccia=self._controller._gestore_traccia._traccia_repo.cercaPerPercorso(percorso_corrente)
            if traccia:
                self.Titolo.setText(f"{traccia.getTitolo()}\ndi {traccia.getArtista()}")
                #Imposto il massimo dello slider 
                self.sliderAvanzamento.setMaximum(int(traccia.getDurata()))
                minuti, secondi = int(traccia.getDurata() // 60), int(traccia.getDurata() % 60)
                self.TempoTotale.setText(f"{minuti}:{secondi:02d}")
        import pygame
        if pygame.mixer.music.get_busy() and not self._controller._in_pausa:
            self.timerAudio.start(500)

    def aggiornaStatoAudio(self):
        #Uso il timer per chiamare questa funzione ogni 500ms, 
        # muove sia lo slider orizzontale e fa partire la traccia successiva
        import pygame
        #1)controllo se la traccia corrente è terminata
        if not pygame.mixer.music.get_busy() and not self._controller._in_pausa:
            #Questo vuol dire che il brano è terminato
            self.gestisciNext()
            return
        #2)aggiorno barra scorrimento
        tempo_ms=pygame.mixer.music.get_pos()
        if tempo_ms>=0:
            tempo_sec=tempo_ms//1000
            self.sliderAvanzamento.setValue(tempo_sec)
            minuti, secondi=tempo_sec//60, tempo_sec%60
            self.TempoCorrente.setText(f"{minuti}:{secondi:02d}")

    def gestisciPlayPausa(self):
        risposta=self._controller.gestisciPlayPausa()
        self.aggiornaCodaVisiva()

        if "RIPRESO" in risposta or "In riproduzione" in risposta:
            self.timerAudio.start(500) #Questo comando fa partire il timer di PyQt ogni mezzo secondo
        else:
            self.timerAudio.stop() #metto in pausa il timer

    def gestisciStop(self):
        self._controller.stop()
        self.timerAudio.stop()
        self.sliderAvanzamento.setValue(0)
        self.TempoCorrente.setText("0:00")
        self.Titolo.setText("Nessun brano")
        self.aggiornaCodaVisiva()

    def gestisciNext(self):
        self._controller.playSuccessiva()
        self.aggiornaCodaVisiva()

    def gestisciShuffle(self):
        self._controller.toggleShuffle()
        #Per distinguere se shuffle è on o meno cambio il colore del bottone da verde(attivo) a grigio
        if self._controller._coda.getShuffle():
            self.btnShuffle.setStyleSheet("background-color: #1DB954; color: white; font-size: 24px; border-radius: 5px; border: none; outline: none; margin: 0px; padding: 0px;")
        else:
            self.btnShuffle.setStyleSheet("background-color: transparent; color: white; font-size: 24px; border: none; outline: none; margin: 0px; padding: 0px;")
        #infine per rimuovere un bug visivo per il quale una volta premuto rimaneva tale e graficamente non cambiava
        #chiamiamo clearFocus
        self.btnShuffle.clearFocus()

    def gestisciRepeat(self):
        #ragionamento identico a shuffle
        self._controller.toggleRepeat()
        if self._controller._coda.getRepeat():
            self.btnRepeat.setStyleSheet("background-color: #1DB954; color: white; font-size: 24px; border-radius: 5px; border: none; outline: none; margin: 0px; padding: 0px;")
        else:
            self.btnRepeat.setStyleSheet("background-color: transparent; color: white; font-size: 24px; border: none; outline: none; margin: 0px; padding: 0px;")
        self.btnRepeat.clearFocus()
        
    def gestisciVolume(self):
        #devo convertire l'intero dello slider in float per farlo accettare dal controller
        valore_float=self.sliderVolume.value()/100.0
        self._controller.impostaVolume(valore_float)

    def playDaCoda(self):
        #devo far si che se l'utente fa doppio click su una canzone in coda riproduce quella
        riga=self.listaCoda.currentRow()
        self._controller.playIndice(riga)
        self.timerAudio.start(500)
        self.aggiornaCodaVisiva()

    def gestisciSvuotaCoda(self):
        self._controller.svuotaCoda()
        self.gestisciStop() # Il tuo metodo stop() furbamente resetta già testi, barra e timer!
    


