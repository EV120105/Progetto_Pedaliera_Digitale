from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
class VistaLogin(QWidget):
    def __init__(self, controller_utente, on_login_success):
        super().__init__()
        #Nota: on_login_success servirà per cambaire pagina a login avvenuto
        self._controller=controller_utente
        self._on_login_success=on_login_success
        #Aggiungo una variabile di stato che si ricorderà se stiamo effettuando il login o se stiamo registrando
        self.modalita_registrazione=False
        #INIZIO A CREARE L'INTERFACCIA
        #LAYOUT PRINCIPALE (serve solo per centrare)
        layout_principale=QVBoxLayout()
        layout_principale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        


        #CREO LA "CARTA" DEL LOGIN
        self.contenitore_form=QWidget()
        self.contenitore_form.setFixedWidth(350) #lo faccio perchè altrimenti si allarga insieme alla finestra
        #creando un brutto effetto visivo
        #metto alcune impostazioni grafiche
        self.contenitore_form.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #2b2b2b;
                color: white;
                margin-bottom: 10px;
                font-size: 14px;
            }
            QPushButton {
                padding: 12px;
                background-color: #1DB954; /* Verde Spotify */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1ed760; /* Verde più chiaro quando passi col mouse */
            }
        """)

        #TUTTO QUELLO CHE FA PARTE DELLA CARTA LOGIN
        layout_form=QVBoxLayout()

        self.titolo=QLabel("Audio Master")
        self.titolo.setStyleSheet("font-size: 28px; font-weight: bold; color: white;  margin-bottom: 20px; background: transparent;")
        self.titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input_username=QLineEdit()
        self.input_username.setPlaceholderText("Username")

        self.input_password=QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password) #serve per oscurare la password scritta

        #Campi per la registrazione che restano nascosti
        self.input_email=QLineEdit()
        self.input_email.setPlaceholderText("Email")
        self.input_email.hide()

        self.combo_livello=QComboBox() #il menu a tendina
        self.combo_livello.addItems(["Principiante", "Intermedio", "Avanzato"])
        self.combo_livello.hide()

        self.bottone_azione=QPushButton("Accedi")
        self.bottone_azione.clicked.connect(self.gestisciAzione)

        #Ora assemblo la carta con i widget creati sopra
        layout_form.addWidget(self.titolo)
        layout_form.addWidget(self.input_username)
        layout_form.addWidget(self.input_password)
        layout_form.addWidget(self.input_email)
        layout_form.addWidget(self.combo_livello)
        layout_form.addWidget(self.bottone_azione)
        self.contenitore_form.setLayout(layout_form)
        #Metto la carta creata dentro il layout principale
        layout_principale.addWidget(self.contenitore_form)
        self.setLayout(layout_principale)

    def gestisciAzione(self):
        #Questo metodo sarà collegato al click del bottone accedi e gestirà sia il login che la registrazione
        username=self.input_username.text()
        password=self.input_password.text()
        #Controllo i campi inseriti
        if not username or not password:
            QMessageBox.warning(self, "Attenzione", "Inserisci sia Username che Password")
            return
        if not self.modalita_registrazione:
            esito=self._controller.loginUtente(username, password)
            #Controllo la risposta del controller
            if esito== "Login avvenuto con successo":
                QMessageBox.information(self, "Successo", f"Bentornato,{username}!")
                self._on_login_success() #chiamando questo dico al main di cambiare pagina
            elif esito=="La password inserita è errata":
                QMessageBox.critical(self, "Errore", "La password inserita è errata")
                self.input_password.clear()
            elif esito=="Errore, Utente inesistente, Creazione nuovo Utente":
                QMessageBox.information(self, "Benvenuto", "L'utente non esiste. Completa i dati per creare il tuo account")
                self.modalita_registrazione=True
                self.titolo.setText("Registrazione")
                self.bottone_azione.setText("Registrati")
                #ora mostro i campi prima nascosti
                self.input_email.show()
                self.combo_livello.show()
        else:
            #Fase dell'effettiva registrazione
            email=self.input_email.text()
            livello=self.combo_livello.currentText()
            #chiamo il metodo del controller
            esito_reg=self._controller.registraUtente(username, password, email, livello)
            if esito_reg=="ERRORE_MAIL":
                QMessageBox.warning(self, "Errore", "L'email deve contenere '@' e '.' ")
            elif esito_reg=="ERRORE_LIVELLO":
                QMessageBox.warning(self, "Errore", "Livello non valido")
            elif esito_reg=="Creazione nuovo Utente avvenuta con successo":
                QMessageBox.information(self, "Successo", f"Account creato! Benvenuto {username}.")
                self._on_login_success()#Mi sposto al catalogo





