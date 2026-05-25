import os
import tempfile
import pygame
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QSlider, QGroupBox, QLineEdit,
                             QFileDialog, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from Models.pedali import PedaleDistorsione, PedaleChorus, PedaleDelay

class VistaPedaliera(QWidget):
    def __init__(self, catena_controller, elaboratore_catena, gestore_traccia, preset_controller, rendering_controller, callback_aggiorna_catalogo, on_back):
        super().__init__()
        self._controller=catena_controller
        self._elaboratore=elaboratore_catena
        self._gestore_traccia=gestore_traccia
        self._preset_controller=preset_controller
        self._rendering_controller = rendering_controller
        self._callback_aggiorna_catalogo = callback_aggiorna_catalogo
        self._on_back = on_back
        self.percorso_traccia_selezionata=None
        self.file_preview_temp=None
        self.initUI()

    def initUI(self):
        layoutPrincipale=QVBoxLayout()
        layoutPrincipale.setSpacing(15)
        
        #--- TORNO INDIETRO AL CATALOGO ---
        layoutTop = QHBoxLayout()
        self.btnIndietro = QPushButton("Torna al Catalogo")
        self.btnIndietro.setStyleSheet("background-color: #34495e; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btnIndietro.clicked.connect(self._on_back)
        layoutTop.addWidget(self.btnIndietro)
        layoutTop.addStretch() 
        layoutPrincipale.addLayout(layoutTop)
           
        #--- SEZIONE PRESET ---
        gruppoPreset=QGroupBox("Gestione Preset (Salva/Carica)")
        gruppoPreset.setStyleSheet("color: white; font-weight: bold; border: 1px solid #555;")
        layoutPreset=QHBoxLayout()
            
        self.comboPreset=QComboBox()
        self.comboPreset.setStyleSheet("background-color: #3b3b3b; color: white; padding: 5px;")
        self.aggiornaListaPreset()

        btnCaricaPreset=QPushButton("Carica Preset")
        btnCaricaPreset.setStyleSheet("background-color: #34495e; color: white; padding: 5px 15px;")
        btnCaricaPreset.clicked.connect(self.caricaPresetSelezionato)

        btnSalvaPreset=QPushButton("Salva Attuale")
        btnSalvaPreset.setStyleSheet("background-color: #9b59b6; color: white; padding: 5px 15px;")
        btnSalvaPreset.clicked.connect(self.salvaPresetAttuale)

        layoutPreset.addWidget(QLabel("Preset Disponibili:"))
        layoutPreset.addWidget(self.comboPreset)
        layoutPreset.addWidget(btnCaricaPreset)
        layoutPreset.addWidget(btnSalvaPreset)
        gruppoPreset.setLayout(layoutPreset)
        layoutPrincipale.addWidget(gruppoPreset)

        #---SEZIONE SELEZIONE TRACCIA---
        gruppoTraccia=QGroupBox("1. Seleziona Traccia da Elaborare")
        gruppoTraccia.setStyleSheet("color:white; font-weight:bold;")
        layoutTraccia=QHBoxLayout()
        self.comboTracce=QComboBox()
        self.comboTracce.setStyleSheet("background-color: #3b3b3b; color: white; padding: 5px;")
        self.aggiornaListaTracce()
        self.comboTracce.currentIndexChanged.connect(self.selezionaTraccia)

        layoutTraccia.addWidget(self.comboTracce)
        gruppoTraccia.setLayout(layoutTraccia)
        layoutPrincipale.addWidget(gruppoTraccia)

        #--- SEZIONE PEDALI ---
        self.layoutPedali=QHBoxLayout()
            
        self.gruppoDist=self.creaPedaleUI("Distorsione", [
           

            {"nome": "Gain", "chiave": "gain", "min": 0, "max": 100, "default": 50, "div": 100, "unita": ""}])
        self.layoutPedali.addWidget(self.gruppoDist["box"])


        self.gruppoChorus=self.creaPedaleUI("Chorus", [
            {"nome": "Rate", "chiave": "rate", "min": 1, "max": 100, "default": 15, "div": 10, "unita": " Hz"},
            {"nome": "Depth", "chiave": "depth", "min": 0, "max": 100, "default": 40, "div": 100, "unita": ""}])
        self.layoutPedali.addWidget(self.gruppoChorus["box"])
        
        self.gruppoDelay = self.creaPedaleUI("Delay", [
            {"nome": "Tempo", "chiave": "tempo", "min": 10, "max": 2000, "default": 500, "div": 1, "unita": " ms"},
            {"nome": "Feedback", "chiave": "feedback", "min": 0, "max": 100, "default": 40, "div": 100, "unita": ""}])
        self.layoutPedali.addWidget(self.gruppoDelay["box"])

        layoutPrincipale.addLayout(self.layoutPedali)

        #--- SEZIONE AZIONI ---
        layoutAzioni=QHBoxLayout()

        self.btnPreview=QPushButton("▶ Ascolta Preview")
        self.btnPreview.setStyleSheet("background-color: #f39c12; color: white; padding: 15px; font-weight: bold; border-radius: 5px;")
        self.btnPreview.clicked.connect(self.suonaPreview)
        
        self.btnStop = QPushButton("⏹ Stop")
        self.btnStop.setStyleSheet("background-color: #e74c3c; color: white; padding: 15px; font-weight: bold; border-radius: 5px;")
        self.btnStop.clicked.connect(self.stopAudio)

        self.btnEsporta = QPushButton("💾 ESPORTA TRACCIA")
        self.btnEsporta.setStyleSheet("background-color: #1DB954; color: white; padding: 15px; font-weight: bold; border-radius: 5px;")
        self.btnEsporta.clicked.connect(self.esportaTraccia)

        layoutAzioni.addWidget(self.btnPreview)
        layoutAzioni.addWidget(self.btnStop)
        layoutAzioni.addWidget(self.btnEsporta)
        
        layoutPrincipale.addLayout(layoutAzioni)
        self.setLayout(layoutPrincipale)
        
    def creaPedaleUI(self, nome, parametri_config):
        box=QGroupBox(nome)
        box.setStyleSheet("color: white; border: 1px solid #555; margin-top: 10px;")
        layout=QVBoxLayout()

        #Sezione per la posizione dei pedali
        layoutSposta=QHBoxLayout()
        btnSx=QPushButton("◀")
        btnDx=QPushButton("▶")
        btnSx.setStyleSheet("background-color: #34495e; color: white;")
        btnDx.setStyleSheet("background-color: #34495e; color: white;")

        layoutSposta.addWidget(btnSx)
        layoutSposta.addStretch()
        layoutSposta.addWidget(btnDx)
        layout.addLayout(layoutSposta)

        btnSx.clicked.connect(lambda: self.spostaPedale(box, -1))
        btnDx.clicked.connect(lambda: self.spostaPedale(box, 1))
        #Fine sezione per la posizione

        btnAttiva=QPushButton(f"Attiva {nome}")
        btnAttiva.setCheckable(True)
        btnAttiva.setStyleSheet("QPushButton { background-color: #3b3b3b; color: white; padding: 8px;} QPushButton:checked { background-color: #1DB954; }")
        layout.addWidget(btnAttiva)

        dizionario_sliders = {}
        for config in parametri_config:
            chiave = config["chiave"]
            nome_disp = config["nome"]
            d = config["div"]
            u = config["unita"]
            
            lbl = QLabel(f"{nome_disp}: {config['default']/d}{u}")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(config["min"], config["max"])
            slider.setValue(config["default"])
            
            slider.valueChanged.connect(lambda val, l=lbl, n=nome_disp, div=d, un=u: l.setText(f"{n}: {val/div}{un}"))
            
            layout.addWidget(lbl)
            layout.addWidget(slider)
            dizionario_sliders[chiave] = slider

        box.setLayout(layout)
        return {"box": box, "btnAttiva": btnAttiva, "sliders": dizionario_sliders}
    
    def spostaPedale(self, box_widget, direzione):
        indice_attuale=self.layoutPedali.indexOf(box_widget)
        nuovo_indice=indice_attuale+direzione
        if 0<= nuovo_indice < self.layoutPedali.count():
            self.layoutPedali.removeWidget(box_widget)
            self.layoutPedali.insertWidget(nuovo_indice, box_widget)
            self.applicaConfigurazioneCatena()

    def aggiornaListaPreset(self):
        self.comboPreset.clear()
        chiavi_preset=self._preset_controller.preset_repo._presets.keys()
        if not chiavi_preset:
            self.comboPreset.addItem("Nessun Preset salvato")
        else:
            for nome in chiavi_preset:
                self.comboPreset.addItem(nome)

    def caricaPresetSelezionato(self):
        nome_preset=self.comboPreset.currentText()
        if nome_preset=="Nessun preset salvato" or not nome_preset: return
        
        esito=self._preset_controller.carica_preset(nome_preset)
        if "Errore" in esito:
            QMessageBox.warning(self, "Errore", esito)
            return

        # Riordino visivo dei pedali
        ordine = []
        for p in self._controller.repo.pedali_attivi:
            if p: ordine.append(p.tipo)
        for tipo in ["Distorsione", "Chorus", "Delay"]:
            if tipo not in ordine: ordine.append(tipo) # Quelli spenti vanno in fondo
            
        mappa = {"Distorsione": self.gruppoDist["box"], "Chorus": self.gruppoChorus["box"], "Delay": self.gruppoDelay["box"]}
        for tipo in ordine:
            box = mappa[tipo]
            self.layoutPedali.removeWidget(box)
            self.layoutPedali.addWidget(box)

        # Carico i valori cercando per tipo
        p_dist = next((p for p in self._controller.repo.pedali_attivi if p and p.tipo == "Distorsione"), None)
        self.gruppoDist["btnAttiva"].setChecked(p_dist is not None)
        if p_dist: self.gruppoDist["sliders"]["gain"].setValue(int(p_dist.parametri.get("gain", 0.5)*100))
        
        p_chor = next((p for p in self._controller.repo.pedali_attivi if p and p.tipo == "Chorus"), None)
        self.gruppoChorus["btnAttiva"].setChecked(p_chor is not None)
        if p_chor:
            self.gruppoChorus["sliders"]["rate"].setValue(int(p_chor.parametri.get("rate", 1.5) * 10))
            self.gruppoChorus["sliders"]["depth"].setValue(int(p_chor.parametri.get("depth", 0.4) * 100))
            
        p_del = next((p for p in self._controller.repo.pedali_attivi if p and p.tipo == "Delay"), None)
        self.gruppoDelay["btnAttiva"].setChecked(p_del is not None)
        if p_del:
            self.gruppoDelay["sliders"]["tempo"].setValue(int(p_del.parametri.get("tempo", 500)))
            self.gruppoDelay["sliders"]["feedback"].setValue(int(p_del.parametri.get("feedback", 0.4) * 100))
            
        QMessageBox.information(self, "Preset Caricato", f"Il preset '{nome_preset}' è applicato!")
    
    def salvaPresetAttuale(self):
        nome_preset, ok=QInputDialog.getText(self, "Salva Preset", "Inserisci il nome del preset:")
        if ok and nome_preset.strip():
            self.applicaConfigurazioneCatena()
            self._preset_controller.salva_attuale_come_preset(nome_preset.strip())
            QMessageBox.information(self, "Successo", f"Preset '{nome_preset}' salvato correttamente")
    
    def aggiornaListaTracce(self):
        self.comboTracce.clear()
        self.comboTracce.addItem("--Seleziona una Traccia--", None)
        tracce=self._gestore_traccia._traccia_repo.tutti()
        for t in tracce:
            self.comboTracce.addItem(f"{t.getTitolo()} - {t.getArtista()}", t.getPercorso())
    
    def selezionaTraccia(self):
        self.percorso_traccia_selezionata=self.comboTracce.currentData()

    def applicaConfigurazioneCatena(self):
        self._controller.repo.pedali_attivi = [None, None, None] # Resetta backend
        
        for pos in range(self.layoutPedali.count()):
            widget_corrente = self.layoutPedali.itemAt(pos).widget()

            if widget_corrente == self.gruppoDist["box"]:
                if self.gruppoDist["btnAttiva"].isChecked():
                    gain_f = self.gruppoDist["sliders"]["gain"].value() / 100.0
                    self._controller.repo.aggiungi_o_aggiorna(PedaleDistorsione(pos, gain=gain_f), pos)

            elif widget_corrente == self.gruppoChorus["box"]:
                if self.gruppoChorus["btnAttiva"].isChecked():
                    rate_f = self.gruppoChorus["sliders"]["rate"].value() / 10.0
                    depth_f = self.gruppoChorus["sliders"]["depth"].value() / 100.0
                    self._controller.repo.aggiungi_o_aggiorna(PedaleChorus(pos, rate=rate_f, depth=depth_f), pos)

            elif widget_corrente == self.gruppoDelay["box"]:
                if self.gruppoDelay["btnAttiva"].isChecked():
                    tempo_i = self.gruppoDelay["sliders"]["tempo"].value()
                    feedback_f = self.gruppoDelay["sliders"]["feedback"].value() / 100.0
                    self._controller.repo.aggiungi_o_aggiorna(PedaleDelay(pos, tempo=tempo_i, feedback=feedback_f), pos)

    def stopAudio(self):
        import pygame # Assicuriamoci che sia importato
        pygame.mixer.music.stop()
        
        # IL FIX MAGICO: Forziamo Pygame a rilascia window file lock!
        if hasattr(pygame.mixer.music, 'unload'):
            pygame.mixer.music.unload()
            
        self.btnPreview.setText("▶ Ascolta Preview")

    def suonaPreview(self):
        if not self.percorso_traccia_selezionata:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima una traccia!")
            return
            
        # 1. Fermiamo e scolleghiamo l'audio precedente PRIMA di sovrascrivere il file!
        self.stopAudio()
        
        self.applicaConfigurazioneCatena()
        
        temp_dir = tempfile.gettempdir()
        self.file_preview_temp = os.path.join(temp_dir, "preview_dsp_temp.wav")
        
        esito = self._elaboratore.applica_dsp_catena(self.percorso_traccia_selezionata, self.file_preview_temp)
        
        if "ERRORE" in esito:
            QMessageBox.critical(self, "Errore DSP", esito)
            return
            
        try:
            import pygame
            pygame.mixer.music.load(self.file_preview_temp)
            pygame.mixer.music.play()
            self.btnPreview.setText("Ascoltando...")
        except Exception as e:
            QMessageBox.critical(self, "Errore Audio", f"Impossibile riproduzione preview: {e}")

    def esportaTraccia(self):
        if not self.percorso_traccia_selezionata:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima una traccia")
            return
        self.stopAudio()
        self.applicaConfigurazioneCatena()

        nome_file, ext=os.path.splitext(self.percorso_traccia_selezionata)
        percorso_export=f"{nome_file}_elaborato{ext}"
        #Esportazione file reale
        esito_fisico=self._elaboratore.applica_dsp_catena(self.percorso_traccia_selezionata, percorso_export)
        if "ERRORE" in esito_fisico:
            QMessageBox.critical(self, "Errore di Scrittura", esito_fisico)
            return
        pedali_attivi=[p for p in self._controller.repo.pedali_attivi if p is not None]
        esito_db=self._rendering_controller.esegui_rendering_esportazione(self.percorso_traccia_selezionata, pedali_attivi)
        if "Errore" in esito_db:
            QMessageBox.critical(self, "Errore Database", esito_db)
        else:
            QMessageBox.information(self, "Esportazione Completata", 
                                    f"Traccia elaborata con successo\n\nSalvata fisicamente e registrata in libreria:\n{percorso_export}")
            self._callback_aggiorna_catalogo

        















