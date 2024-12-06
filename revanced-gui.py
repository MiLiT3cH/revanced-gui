import sys
import os
import shutil
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, Qt

if getattr(sys, 'frozen', False):  # Se l'app è eseguita come eseguibile
    app_path = sys._MEIPASS  # Ottieni il percorso temporaneo
else:
    app_path = os.path.dirname(os.path.abspath(__file__))  # Se in modalità di sviluppo

jdk_path = os.path.join(app_path, 'JDK')
ico_path = os.path.join(app_path, 'other')

class ReVancedGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReVanced Patcher GUI")
        self.setGeometry(100, 100, 900, 600)
        self.default_patch_path = "./patches.rvp"
        self.temp_input_file = "input.apk"  # Nome temporaneo per evitare problemi con spazi
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon(os.path.join(app_path, 'other', 'icona.ico')))
        # Apply dark background to the entire application
        self.setStyleSheet("background-color: #121212; color: #ffffff;")
        
        # Main layout
        self.main_layout = QVBoxLayout()

        # Input and output file sections
        self.file_layout = QHBoxLayout()
        self.apk_input_card = self.create_file_selector("APK Input", "apk_input")
        self.apk_output_card = self.create_file_selector("Output APK", "apk_output")
        self.file_layout.addWidget(self.apk_input_card)
        self.file_layout.addWidget(self.apk_output_card)

        # Patch file section (aligned with download/update tools)
        self.patch_file_card = self.create_file_selector("Patch File", "patch_file", default=self.default_patch_path, small=False)
        self.download_update_card = self.create_download_update_card()
        patch_layout = QHBoxLayout()
        patch_layout.addWidget(self.patch_file_card)
        patch_layout.addWidget(self.download_update_card)

        # Log output area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            "background-color: #1f1f1f; color: #e8e8e8; padding: 10px; border-radius: 8px; font-size: 12px;"
        )
        self.log_output.setFont(QFont("Courier New", 10))

        # Run and clear log buttons
        self.run_btn = QPushButton("Run")
        self.run_btn.setStyleSheet(
            "background-color: #6200ea; color: #ffffff; font-size: 14px; border-radius: 12px;"
        )
        self.run_btn.clicked.connect(self.run_command)

        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.setStyleSheet(
            "background-color: #3700b3; color: #ffffff; font-size: 14px; border-radius: 12px;"
        )
        self.clear_log_btn.clicked.connect(self.clear_log)

        # Assemble buttons layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_btn)
        button_layout.addWidget(self.clear_log_btn)

        # Add all components to main layout
        self.main_layout.addLayout(self.file_layout)
        self.main_layout.addLayout(patch_layout)
        self.main_layout.addWidget(QLabel("Output:"))
        self.main_layout.addWidget(self.log_output)
        self.main_layout.addLayout(button_layout)

        # Set final container
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def create_file_selector(self, title, name, default="", small=False):
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("color: #ffffff; margin-bottom: 4px;")
        line_edit = QLineEdit(default)
        line_edit.setPlaceholderText("Seleziona il file...")
        line_edit.setObjectName(name)
        btn = QPushButton("Select File")
        btn.setStyleSheet("background-color: #6200ea; color: #ffffff; border-radius: 8px;")
        btn.clicked.connect(lambda: self.select_file(line_edit))
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(btn)
        
        # Reduce the size if "small" is True
        frame = QFrame()
        frame.setLayout(layout)
        if small:
            frame.setStyleSheet(
                "background-color: #1f1f1f; border-radius: 8px; padding: 5px; max-width: 300px;"
            )
        else:
            frame.setStyleSheet(
                "background-color: #1f1f1f; border-radius: 8px; padding: 10px;"
            )
        return frame

    def create_download_update_card(self):
        layout = QVBoxLayout()
        label = QLabel("Scarica o Aggiorna")
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("color: #ffffff; margin-bottom: 4px;")
        
        # Buttons for downloading patches and CLI
        patch_btn = QPushButton("Update Patches")
        patch_btn.setStyleSheet("background-color: #03DAC6; color: #000000; border-radius: 8px;")
        patch_btn.clicked.connect(lambda: self.download_and_rename_patch())

        cli_btn = QPushButton("Update CLI")
        cli_btn.setStyleSheet("background-color: #03DAC6; color: #000000; border-radius: 8px;")
        cli_btn.clicked.connect(lambda: self.download_and_rename_cli())

        layout.addWidget(label)
        layout.addWidget(patch_btn)
        layout.addWidget(cli_btn)

        frame = QFrame()
        frame.setLayout(layout)
        frame.setStyleSheet("background-color: #1f1f1f; border-radius: 8px; padding: 10px; max-width: 300px;")
        return frame

    def download_and_rename_patch(self):
        try:
            # Get the latest release page
            response = requests.get("https://github.com/ReVanced/revanced-patches/releases/latest", allow_redirects=False)
            if response.status_code == 302:
                # Extract the version number and download the file
                release_url = response.headers['Location']
                version = release_url.split("/")[-1]  # e.g., v5.0.0
                download_url = release_url.replace("/tag/", "/download/") + f"/patches-{version[1:]}.rvp"
                
                # Download the file
                self.download_and_rename_patch2(download_url, ".rvp", "patches.rvp")
            else:
                self.log_output.append("Impossibile scaricare le patch")
        except Exception as e:
            self.log_output.append(f"Impossibile scaricare le patch: {e}")
            
    def download_and_rename_patch2(self, base_url, extension, new_name):
        try:
            response = requests.get(base_url, stream=True)
            response.raise_for_status()
    
            # Ottieni la dimensione totale del file per calcolare la percentuale
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # Verifica se il file esiste già e rimuovilo se necessario
            if os.path.exists(new_name):
                os.remove(new_name)
    
            file_name = f"temp{extension}"
            last_logged_percentage = -1  # Inizializza una variabile per monitorare l'ultima percentuale loggata
    
            with open(file_name, "wb") as f:
                # Carica i dati a blocchi
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filtra i blocchi vuoti
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # Calcola la percentuale
                        percent = (downloaded_size / total_size) * 100
                        # Calcola la lunghezza della barra (la barra avrà una lunghezza di 40 caratteri)
                        bar_length = 40
                        filled_length = int(percent // (100 / bar_length))
                        bar = "▓" * filled_length + "░" * (bar_length - filled_length)
                        # Mostra il progresso in una sola riga
                        self.log_output.clear()  # Pulisce il log precedente
                        self.log_output.append(f"Download Patch in corso... [{bar}] {int(percent)}%")  # Aggiorna il log con la barra di progresso
                        self.log_output.ensureCursorVisible()  # Forza la visibilità del cursore
                        self.log_output.repaint()  # Forza l'aggiornamento dell'interfaccia grafica
    
            # Rinomina il file dopo il download
            os.rename(file_name, new_name)
            self.log_output.append(f"\n{new_name} Download completato con successo")
        except Exception as e:
            self.log_output.append(f"Errore durante il download del cli {new_name}: {e}")        
            
    def download_and_rename_cli(self):
        try:
            # Get the latest release page
            response = requests.get("https://github.com/ReVanced/revanced-cli/releases/latest", allow_redirects=False)
            if response.status_code == 302:
                # Extract the version number and download the file
                release_url = response.headers['Location']
                version = release_url.split("/")[-1]  # e.g., v5.0.0
                download_url = release_url.replace("/tag/", "/download/") + f"/revanced-cli-{version[1:]}-all.jar"
                
                # Download the file
                self.download_and_rename_cli2(download_url, ".jar", "revanced-cli.jar")
            else:
                self.log_output.append("Errore durante il download del cli.")
        except Exception as e:
            self.log_output.append(f"Errore durante il download del cli: {e}")
    
    def download_and_rename_cli2(self, base_url, extension, new_name):
        try:
            response = requests.get(base_url, stream=True)
            response.raise_for_status()
    
            # Ottieni la dimensione totale del file per calcolare la percentuale
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # Verifica se il file esiste già e rimuovilo se necessario
            if os.path.exists(new_name):
                os.remove(new_name)
    
            file_name = f"temp{extension}"
            last_logged_percentage = -1  # Inizializza una variabile per monitorare l'ultima percentuale loggata
    
            with open(file_name, "wb") as f:
                # Carica i dati a blocchi
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filtra i blocchi vuoti
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # Calcola la percentuale
                        percent = (downloaded_size / total_size) * 100
                        # Calcola la lunghezza della barra (la barra avrà una lunghezza di 40 caratteri)
                        bar_length = 40
                        filled_length = int(percent // (100 / bar_length))
                        bar = "▓" * filled_length + "░" * (bar_length - filled_length)
                        # Mostra il progresso in una sola riga
                        self.log_output.clear()  # Pulisce il log precedente
                        self.log_output.append(f"Download Revanced-cli in corso... [{bar}] {int(percent)}%")  # Aggiorna il log con la barra di progresso
                        self.log_output.ensureCursorVisible()  # Forza la visibilità del cursore
                        self.log_output.repaint()  # Forza l'aggiornamento dell'interfaccia grafica
    
            # Rinomina il file dopo il download
            os.rename(file_name, new_name)
            self.log_output.append(f"\n{new_name} Download completato con successo")
        except Exception as e:
            self.log_output.append(f"Errore durante il download {new_name}: {e}")
            
    def select_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            line_edit.setText(file_path)
            
    def clear_log(self):
        self.log_output.clear()

    def run_command(self):
        apk_input = self.findChild(QLineEdit, "apk_input").text()
        apk_output = self.findChild(QLineEdit, "apk_output").text()
        patch_file = self.findChild(QLineEdit, "patch_file").text()

        if not apk_output.endswith(".apk"):
            apk_output += ".apk"

        if not os.path.isfile(apk_input) or not os.path.isfile(patch_file):
            self.log_output.append("Error: Nessun file selezionato.")
            return

        if " " in apk_input:
            shutil.copy(apk_input, self.temp_input_file)
            apk_input = self.temp_input_file

        command = [
            "JDK\\bin\\java.exe", "-jar", "-Xmx512m",
            ".\\revanced-cli.jar", "patch",
            "-p", patch_file,
            apk_input, "-o", apk_output
        ]

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.update_log)
        self.process.finished.connect(self.cleanup_temp_file)
        self.process.start(" ".join(command))

    def update_log(self):
        output = self.process.readAll().data().decode()
        self.log_output.append(output)
        self.log_output.ensureCursorVisible()

    def cleanup_temp_file(self):
        if os.path.exists(self.temp_input_file):
            os.remove(self.temp_input_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReVancedGUI()
    window.show()
    sys.exit(app.exec_())
