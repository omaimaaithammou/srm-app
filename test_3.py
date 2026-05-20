import sys
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, 
                             QScrollArea, QGridLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class FinalSRMInventory(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SRM Inventory Management System v2.0')
        self.resize(800, 900)
        self.setMinimumSize(600, 700)
        
        # CSS التصميم العصري باستعمال
        self.setStyleSheet("""
            QWidget { background-color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            QScrollArea { border: none; background-color: transparent; }
            QFrame#MainCard { background-color: white; border-radius: 15px; border: 1px solid #e2e8f0; }
            QLabel { color: #334155; font-weight: 600; font-size: 13px; }
            QLineEdit, QComboBox { 
                border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 10px; 
                background-color: #f8fafc; font-size: 14px; color: #1e293b;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3b82f6; background-color: white; }
            QPushButton#SaveBtn { 
                background-color: #2563eb; color: white; border-radius: 8px; 
                padding: 15px; font-size: 16px; font-weight: bold; margin-top: 10px;
            }
            QPushButton#SaveBtn:hover { background-color: #1d4ed8; }
            QLabel#Title { font-size: 28px; color: #0f172a; font-weight: 800; }
        """)

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        card.setObjectName("MainCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        # Header
        title = QLabel("SRM Inventory Management")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Saisie technique des équipements informatiques")
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        # Form Grid (12 Fields)
        grid = QGridLayout()
        grid.setSpacing(20)

        self.inputs = {}

        # 1. Site (ComboBox)
        grid.addWidget(QLabel("Site (Localisation)"), 0, 0)
        self.site_combo = QComboBox()
        self.site_combo.addItems([
            'DP Taroudant', 'BE-ASP TAROUDANT', 'BE-AS TALIOUINE', 
            'BE-AS AOULOUZ', 'BE-AS OULAD BERHIL', 'BO-TAROUDANT', 
            'BO-AIT IAZZA', 'BO-TALIOUINE'
        ])
        grid.addWidget(self.site_combo, 1, 0)
        self.inputs['site'] = self.site_combo

        # باقي الحقول (LineEdits)
        other_fields = [
            ("Code Bureau", "code_bureau", 0, 1),
            ("Nom Agent", "nom_agent", 2, 0),
            ("Prénom Agent", "prenom_agent", 2, 1),
            ("Matricule", "matricule", 4, 0),
            ("Type Matériel", "type_materiel", 4, 1),
            ("Marque", "marque", 6, 0),
            ("Modèle", "modele", 6, 1),
            ("N° Inventaire", "numero_inventaire", 8, 0),
            ("N° Série", "numero_serie", 8, 1),
            ("Année Fabrication", "annee_fabrication", 10, 0),
            ("Système d'Exploitation", "systeme_exploitation", 10, 1)
        ]

        for label, db_name, r, c in other_fields:
            grid.addWidget(QLabel(label), r, c)
            edit = QLineEdit()
            edit.setPlaceholderText(f"Entrer {label}...")
            grid.addWidget(edit, r+1, c)
            self.inputs[db_name] = edit

        card_layout.addLayout(grid)

        # Save Button
        btn_save = QPushButton("Enregistrer l'équipement")
        btn_save.setObjectName("SaveBtn")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.save_data)
        card_layout.addWidget(btn_save)

        main_layout.addWidget(card)
        layout.addWidget(scroll)

    def save_data(self):
        # جمع البيانات من الواجهة
        final_data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                final_data[key] = widget.currentText()
            else:
                final_data[key] = widget.text().strip()

        # التحقق من الحقول الإجبارية
        if not final_data['nom_agent'] or not final_data['numero_serie']:
            QMessageBox.warning(self, "Attention", "Le Nom de l'agent et le N° de Série sont obligatoires !")
            return

        try:
            # MySQL الاتصال بقاعدة بيانات
            db = mysql.connector.connect(
                host="localhost", user="root", password="", database="srm_inventory"
            )
            cursor = db.cursor()
            
            # SQL استعلام
            columns = ", ".join(final_data.keys())
            placeholders = ", ".join(["%s"] * len(final_data))
            sql = f"INSERT INTO materiel ({columns}) VALUES ({placeholders})"
            
            cursor.execute(sql, list(final_data.values()))
            db.commit()
            
            QMessageBox.information(self, "Succès", "Données enregistrées avec succès dans la base SRM !")
            
            # مسح الحقول بعد الحفظ
            for key, widget in self.inputs.items():
                if isinstance(widget, QLineEdit): widget.clear()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erreur Base de données", f"Problème de connexion : {err}")
        finally:
            if 'db' in locals() and db.is_connected():
                db.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FinalSRMInventory()
    window.show()
    sys.exit(app.exec_())