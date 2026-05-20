import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QGridLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRM Inventory Manager")
        self.setGeometry(200, 100, 700, 500)
        self.setStyleSheet("background-color: #eef2f3;")

        self.initUI()
        self.connect_db()

    # ---------------------- DATABASE CONNECTION ----------------------
    def connect_db(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="srm_inventory"
            )
            self.cursor = self.db.cursor()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Connection failed:\n{str(e)}")

    # ---------------------- UI DESIGN ----------------------
    def initUI(self):
        layout = QGridLayout()

        title = QLabel("SRM INVENTORY MANAGER")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title, 0, 0, 1, 2)

        labels = [
            "Site:", "Code Bureau:", "Nom Agent:", "Prénom:", "Matricule:",
            "Type Matériel:", "Marque:", "Modèle:", "Numéro Inventaire:",
            "Numéro Série:", "Année Fabrication:", "Système d'Exploitation:",
            "Windows Activé:", "Mémoire Vive (RAM):"
        ]

        self.inputs = {}

        # Combo boxes
        self.inputs["Site"] = QComboBox()
        self.inputs["Site"].addItems(["BO-IGHERM", "BO-OULED TEIMA"])

        self.inputs["Type Matériel"] = QComboBox()
        self.inputs["Type Matériel"].addItems(["PC", "Écran", "Scanner", "Imprimante"])

        self.inputs["Windows Activé"] = QComboBox()
        self.inputs["Windows Activé"].addItems(["Oui", "Non"])

        row = 1

        for label in labels:
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 11))

            if label in ["Site:", "Type Matériel:", "Windows Activé:"]:
                inp = self.inputs[label[:-1]]
            else:
                inp = QLineEdit()
                self.inputs[label[:-1]] = inp

            layout.addWidget(lbl, row, 0)
            layout.addWidget(inp, row, 1)
            row += 1

        # SAVE BUTTON
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        save_btn.clicked.connect(self.save_data)

        layout.addWidget(save_btn, row, 0, 1, 2)

        self.setLayout(layout)

    # ---------------------- SAVE DATA ----------------------
    def save_data(self):
        try:
            query = """
                INSERT INTO materiel (
                    site, code_bureau, nom_agent, prenom_agent, matricule,
                    type_materiel, marque, modele, num_inventaire,
                    num_serie, annee_fabrication, systeme_exploitation,
                    windows_active, ram
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            data = (
                self.inputs["Site"].currentText(),
                self.inputs["Code Bureau"].text(),
                self.inputs["Nom Agent"].text(),
                self.inputs["Prénom"].text(),
                self.inputs["Matricule"].text(),
                self.inputs["Type Matériel"].currentText(),
                self.inputs["Marque"].text(),
                self.inputs["Modèle"].text(),
                self.inputs["Numéro Inventaire"].text(),
                self.inputs["Numéro Série"].text(),
                self.inputs["Année Fabrication"].text(),
                self.inputs["Système d'Exploitation"].text(),
                self.inputs["Windows Activé"].currentText(),
                self.inputs["Mémoire Vive (RAM)"].text()
            )

            self.cursor.execute(query, data)
            self.db.commit()

            QMessageBox.information(self, "Succès", "Données enregistrées avec succès!")

            for key in self.inputs:
                if isinstance(self.inputs[key], QLineEdit):
                    self.inputs[key].clear()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer:\n{str(e)}")


# ---------------------- MAIN ----------------------
app = QApplication(sys.argv)
window = InventoryApp()
window.show()
sys.exit(app.exec_())