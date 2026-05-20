import sys
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class ModernInventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # إعدادات النافذة
        self.setWindowTitle('SRM Inventory Management')
        self.setFixedSize(450, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
            }
            QFrame#MainFrame {
                background-color: white;
                border-radius: 15px;
            }
            QLabel {
                color: #2f3640;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLineEdit {
                border: 2px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QLabel#Logo {
                font-size: 24px;
                color: #3498db;
                margin-bottom: 20px;
            }
        """)

        # الليوت الرئيسي
        main_layout = QVBoxLayout()
        
        # إطار داخلي (Card Style)
        container = QFrame()
        container.setObjectName("MainFrame")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)

        # لوغو وهمي (نصي)
        logo = QLabel("📦 SRM INVENTORY")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(logo)

        # الحقول (Inputs)
        self.inputs = {}
        fields = [
            ("Nom Agent", "nom_agent"),
            ("Prénom", "prenom_agent"),
            ("Matricule", "matricule"),
            ("Site", "site"),
            ("Type Matériel", "type_materiel")
        ]

        for label_text, db_name in fields:
            lbl = QLabel(label_text)
            edit = QLineEdit()
            edit.setPlaceholderText(f"Entrer {label_text.lower()}...")
            container_layout.addWidget(lbl)
            container_layout.addWidget(edit)
            self.inputs[db_name] = edit

        # زر الإرسال
        btn_submit = QPushButton("Enregistrer les données")
        btn_submit.setCursor(Qt.PointingHandCursor)
        btn_submit.clicked.connect(self.save_data)
        container_layout.addWidget(btn_submit)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def save_data(self):
        # جمع البيانات من الحقول
        data = {k: v.text() for k, v in self.inputs.items()}
        
        if not data['nom_agent'] or not data['matricule']:
            QMessageBox.warning(self, "خطأ", "المرجو ملء الحقول الأساسية!")
            return

        try:
            # الاتصال بـ MySQL
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="srm_inventory"
            )
            cursor = conn.cursor()
            
            sql = """INSERT INTO materiel (nom_agent, prenom_agent, matricule, site, type_materiel) 
                     VALUES (%s, %s, %s, %s, %s)"""
            values = (data['nom_agent'], data['prenom_agent'], data['matricule'], data['site'], data['type_materiel'])
            
            cursor.execute(sql, values)
            conn.commit()
            
            QMessageBox.information(self, "نجاح", "تم حفظ البيانات بنجاح!")
            
            # مسح الحقول بعد الحفظ
            for edit in self.inputs.values():
                edit.clear()
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ModernInventoryApp()
    ex.show()
    sys.exit(app.exec_())