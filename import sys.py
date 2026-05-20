import sys
import os
import json
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
                             QMessageBox, QComboBox, QRadioButton, QInputDialog,
                             QGraphicsDropShadowEffect, QLineEdit, QDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice

SETTINGS_FILE = "settings.json"

# ==========================================
# 1. النافذة المخصصة الجديدة لإدخال البيانات دفعة واحدة
# ==========================================
class AddSiteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un Site")
        self.setMinimumWidth(400)
        self.setStyleSheet("background-color: #f8fafc;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # عنوان النافذة الداخلي
        title = QLabel("Saisir les informations du site")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #1a2a3a; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # النموذج (Form)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # حقول الإدخال مع ستايل متناسق
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Ex: DP Taroudant")
        self.input_nom.setFixedHeight(38)
        self.input_nom.setStyleSheet("QLineEdit { padding-left: 10px; border: 1px solid #cbd5e1; border-radius: 6px; background-color: white; }")
        
        self.combo_type = QComboBox()
        self.combo_type.addItems(["DP", "BE-ASP", "BE-AS", "DFS"])
        self.combo_type.setFixedHeight(38)
        self.combo_type.setStyleSheet("QComboBox { padding-left: 10px; border: 1px solid #cbd5e1; border-radius: 6px; background-color: white; }")
        
        self.input_ville = QLineEdit()
        self.input_ville.setPlaceholderText("Ex: Taroudant")
        self.input_ville.setFixedHeight(38)
        self.input_ville.setStyleSheet("QLineEdit { padding-left: 10px; border: 1px solid #cbd5e1; border-radius: 6px; background-color: white; }")
        
        form_layout.addRow("Nom du Site :", self.input_nom)
        form_layout.addRow("Type du Site :", self.combo_type)
        form_layout.addRow("Ville :", self.input_ville)
        layout.addLayout(form_layout)
        
        # الأزرار
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_ok = QPushButton("Enregistrer")
        self.btn_ok.setFixedHeight(38)
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_ok.setStyleSheet("QPushButton { background-color: #10ac84; color: white; border-radius: 6px; border: none; }"
                                  "QPushButton:hover { background-color: #0f9b75; }")
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_cancel.setStyleSheet("QPushButton { background-color: #94a3b8; color: white; border-radius: 6px; border: none; }"
                                      "QPushButton:hover { background-color: #64748b; }")
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_data(self):
        return {
            "nom": self.input_nom.text().strip(),
            "type": self.combo_type.currentText(),
            "ville": self.input_ville.text().strip()
        }

# ==========================================
# 2. كلاس التطبيق الرئيسي (المحدث)
# ==========================================
class SRMStockManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRM SM - GESTION DE STOCK v3.0")
        self.resize(1400, 880)
        
        # Connexion à la Base de Données
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bd_managemant"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erreur de Connexion", 
                                 f"Impossible de se connecter à MySQL.\n"
                                 f"Veuillez vérifier que le serveur MySQL est activé sur XAMPP !\n\nDétails: {err}")
            sys.exit()

        self.initUI()
        self.load_saved_settings()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content()

        # Connexion des boutons
        self.btn_kpi.clicked.connect(lambda: self.display_page(0))
        self.btn_sites.clicked.connect(lambda: self.display_page(1))
        self.btn_bureaux.clicked.connect(lambda: self.display_page(2))
        self.btn_agents.clicked.connect(lambda: self.display_page(3))
        self.btn_materiel.clicked.connect(lambda: self.display_page(4))
        self.btn_settings.clicked.connect(lambda: self.display_page(5))
        self.btn_logout.clicked.connect(self.handle_logout)

        self.pages.setCurrentIndex(0)
        self.update_kpi_values()

    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(310)
        sidebar.setStyleSheet("background-color: #1a2a3a; border-right: 1px solid #e1e8ed;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 25, 15, 20)
        
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        logo_path = "images.jpg"
        if os.path.exists(logo_path):
            original_pixmap = QPixmap(logo_path)
            scaled_pixmap = original_pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image = scaled_pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
            for x in range(image.width()):
                for y in range(image.height()):
                    color = image.pixelColor(x, y)
                    if color.red() > 240 and color.green() > 240 and color.blue() > 240:
                        color.setAlpha(0)
                        image.setPixelColor(x, y, color)
            self.logo_label.setPixmap(QPixmap.fromImage(image))
        else:
            self.logo_label.setText("🏢")
            self.logo_label.setStyleSheet("font-size: 35px; color: white;")
            
        logo_text = QLabel("SRM SM\nSOUSS-MASSA")
        logo_text.setFont(QFont("Segoe UI", 13, QFont.Bold))
        logo_text.setStyleSheet("color: #ffb142;")
        logo_text.setAlignment(Qt.AlignCenter)
        
        logo_layout.addWidget(self.logo_label)
        logo_layout.addWidget(logo_text)
        layout.addWidget(logo_container)
        
        separator = QFrame()
        separator.setStyleSheet("background-color: #ffb142; max-height: 2px; margin-top: 10px; margin-bottom: 20px;")
        layout.addWidget(separator)

        title = QLabel("TABLEAU DE BORD")
        title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        title.setStyleSheet("color: #a4b0be; letter-spacing: 1px; padding-left: 10px; margin-bottom: 10px;")
        layout.addWidget(title)

        self.btn_kpi = self.create_nav_btn("📊  Tableau de Bord")
        self.btn_sites = self.create_nav_btn("📍  Gestion des Sites")
        self.btn_bureaux = self.create_nav_btn("🏢  Gestion des Bureaux")
        self.btn_agents = self.create_nav_btn("👥  Gestion des Agents")
        self.btn_materiel = self.create_nav_btn("💻  Type de Matériel")
        self.btn_settings = self.create_nav_btn("⚙️  Paramètres App")
        self.btn_logout = self.create_nav_btn("🚪  Déconnexion")

        layout.addWidget(self.btn_kpi)
        layout.addWidget(self.btn_sites)
        layout.addWidget(self.btn_bureaux)
        layout.addWidget(self.btn_agents)
        layout.addWidget(self.btn_materiel)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_logout)
        
        layout.addStretch()
        self.main_layout.addWidget(sidebar)

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; color: #FFFFFF; text-align: left; padding-left: 15px; border-radius: 5px; }
            QPushButton:hover { background-color: #10ac84; color: white; padding-left: 25px; }
        """)
        return btn

    def setup_content(self):
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background-color: #f4f6f9;")
        
        self.table_sites = self.create_table()
        self.table_bureaux = self.create_table()
        self.table_agents = self.create_table()
        self.table_materiel = self.create_table()

        self.pages.addWidget(self.create_kpi_page())
        self.pages.addWidget(self.create_page_layout("GESTION DES SITES", self.table_sites, self.add_site, self.export_site))
        self.pages.addWidget(self.create_page_layout("GESTION DES BUREAUX", self.table_bureaux, self.add_bureau, self.export_bureau))
        self.pages.addWidget(self.create_page_layout("GESTION DES AGENTS", self.table_agents, self.add_agent, self.export_agent))
        self.pages.addWidget(self.create_page_layout("TYPES DE MATÉRIEL", self.table_materiel, self.add_materiel, self.export_materiel))
        self.pages.addWidget(self.create_settings_page())

        self.main_layout.addWidget(self.pages)

    def create_table(self):
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setFont(QFont("Segoe UI", 10))
        table.horizontalHeader().setFont(QFont("Segoe UI", 10, QFont.Bold))
        table.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #e1e8ed; border: 1px solid #e1e8ed; border-radius: 8px; }
            QHeaderView::section { background-color: #10ac84; color: white; padding: 10px; border: none; }
        """)
        return table

    def create_page_layout(self, title_text, table_obj, add_callback, export_callback):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 30)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel(title_text)
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_title.setStyleSheet("color: #1a2a3a;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        btn_add = QPushButton("➕ Ajouter")
        btn_add.setFixedSize(110, 36)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_add.setStyleSheet("QPushButton { background-color: #10ac84; color: white; border-radius: 6px; border: none; }"
                              "QPushButton:hover { background-color: #0f9b75; }")
        btn_add.clicked.connect(add_callback)
        header_layout.addWidget(btn_add)

        btn_export = QPushButton("📥 Exporter")
        btn_export.setFixedSize(110, 36)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_export.setStyleSheet("QPushButton { background-color: #2e86de; color: white; border-radius: 6px; border: none; }"
                               "QPushButton:hover { background-color: #1b6ca8; }")
        btn_export.clicked.connect(export_callback)
        header_layout.addWidget(btn_export)
        
        layout.addLayout(header_layout)
        layout.addWidget(table_obj)
        return page

    def create_kpi_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        title = QLabel("Tableau de Bord Overview")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1a2a3a;")
        layout.addWidget(title)
        
        stats_layout = QHBoxLayout()
        self.card_sites = self.create_stat_card("SITES ACTIFS", "0", "📡", "#10ac84", "#e3fcef")
        self.card_bureaux = self.create_stat_card("TOTAL BUREAUX", "0", "🏢", "#2e86de", "#e3f2fd")
        self.card_agents = self.create_stat_card("AGENTS SRM", "0", "👥", "#ff9f43", "#fff3e0")
        
        stats_layout.addWidget(self.card_sites)
        stats_layout.addWidget(self.card_bureaux)
        stats_layout.addWidget(self.card_agents)
        layout.addLayout(stats_layout)
        
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        self.bar_chartview = QChartView()
        self.bar_chartview.setRenderHint(QPainter.Antialiasing)
        self.bar_chartview.setMinimumHeight(460)
        self.bar_chartview.setStyleSheet("background-color: white; border-radius: 12px;")
        
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(15)
        shadow1.setXOffset(0)
        shadow1.setYOffset(5)
        shadow1.setColor(QColor(0, 0, 0, 40))
        self.bar_chartview.setGraphicsEffect(shadow1)
        
        self.pie_chartview = QChartView()
        self.pie_chartview.setRenderHint(QPainter.Antialiasing)
        self.pie_chartview.setMinimumHeight(460)
        self.pie_chartview.setStyleSheet("background-color: white; border-radius: 12px;")
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setXOffset(0)
        shadow2.setYOffset(5)
        shadow2.setColor(QColor(0, 0, 0, 40))
        self.pie_chartview.setGraphicsEffect(shadow2)
        
        charts_layout.addWidget(self.bar_chartview, 3)
        charts_layout.addWidget(self.pie_chartview, 2)
        
        layout.addLayout(charts_layout)
        return page

    def create_stat_card(self, title, value, icon, color, bg_icon_color):
        card = QFrame()
        card.setFixedHeight(110)
        card.setObjectName("StatCard")
        card.setStyleSheet(f"""
            QFrame#StatCard {{ background-color: white; border: 1px solid #e2e8f0; border-radius: 15px; }}
            QFrame#StatCard:hover {{ border: 1px solid {color}; }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(3)
        shadow.setYOffset(8)
        shadow.setColor(QColor(160, 175, 190, 80))
        card.setGraphicsEffect(shadow)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_title.setStyleSheet("color: #64748b; letter-spacing: 0.5px; background: transparent;")
        
        lbl_val = QLabel(value)
        lbl_val.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_val.setStyleSheet(f"color: {color}; background: transparent;")
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_val)
        
        icon_panel = QFrame()
        icon_panel.setFixedSize(55, 55)
        icon_panel.setStyleSheet(f"background-color: {bg_icon_color}; border-radius: 27px; border: none;")
        
        panel_layout = QVBoxLayout(icon_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 22))
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent;")
        panel_layout.addWidget(lbl_icon)
        
        card_layout.addWidget(text_container)
        card_layout.addStretch()
        card_layout.addWidget(icon_panel)
        
        if title == "SITES ACTIFS": self.lbl_sites_val = lbl_val
        elif title == "TOTAL BUREAUX": self.lbl_bureaux_val = lbl_val
        elif title == "AGENTS SRM": self.lbl_agents_val = lbl_val
        
        return card

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        title = QLabel("⚙️ PARAMÈTRES DE L'APPLICATION")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1a2a3a; margin-bottom: 10px;")
        layout.addWidget(title)
        
        account_box = QFrame()
        account_box.setStyleSheet("QFrame { background-color: white; border: 1px solid #e1e8ed; border-radius: 12px; }")
        account_layout = QVBoxLayout(account_box)
        account_layout.setContentsMargins(25, 20, 25, 25)
        account_layout.setSpacing(15)
        
        lbl_acc_title = QLabel("👤 Changer d'utilisateur / Connexion")
        lbl_acc_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_acc_title.setStyleSheet("color: #2e86de; border: none; background: transparent;")
        account_layout.addWidget(lbl_acc_title)
        
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Nom d'utilisateur")
        self.input_username.setFixedHeight(42)
        self.input_username.setFont(QFont("Segoe UI", 10))
        self.input_username.setStyleSheet("""
            QLineEdit { padding-left: 12px; border: 1px solid #cbd5e1; border-radius: 8px; background-color: #f8fafc; }
            QLineEdit:focus { border: 1px solid #2e86de; background-color: white; }
        """)
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Mot de passe")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(42)
        self.input_password.setFont(QFont("Segoe UI", 10))
        self.input_password.setStyleSheet("""
            QLineEdit { padding-left: 12px; border: 1px solid #cbd5e1; border-radius: 8px; background-color: #f8fafc; }
            QLineEdit:focus { border: 1px solid #2e86de; background-color: white; }
        """)
        
        btn_login_submit = QPushButton("Se connecter")
        btn_login_submit.setFixedSize(140, 42)
        btn_login_submit.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_login_submit.setCursor(Qt.PointingHandCursor)
        btn_login_submit.setStyleSheet("""
            QPushButton { background-color: #2e86de; color: white; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #1b6ca8; }
        """)
        btn_login_submit.clicked.connect(self.handle_internal_login)
        
        form_layout.addWidget(self.input_username, 2)
        form_layout.addWidget(self.input_password, 2)
        form_layout.addWidget(btn_login_submit, 1)
        
        account_layout.addLayout(form_layout)
        layout.addWidget(account_box)
        
        lang_box = QFrame()
        lang_box.setStyleSheet("background-color: white; border: 1px solid #e1e8ed; border-radius: 12px;")
        lang_layout = QVBoxLayout(lang_box)
        lang_layout.setContentsMargins(25, 20, 25, 25)
        lang_layout.setSpacing(12)
        
        lbl_lang = QLabel("🌐 Sélectionner la Langue de l'application :")
        lbl_lang.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_lang.setStyleSheet("color: #1a2a3a; border: none; background: transparent;")
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Français", "Arabe", "English"])
        self.combo_lang.setFixedHeight(40)
        self.combo_lang.setFont(QFont("Segoe UI", 10))
        self.combo_lang.setStyleSheet("QComboBox { padding-left: 10px; border: 1px solid #cbd5e1; border-radius: 8px; background-color: white; }")
        
        lang_layout.addWidget(lbl_lang)
        lang_layout.addWidget(self.combo_lang)
        layout.addWidget(lang_box)
        
        theme_box = QFrame()
        theme_box.setStyleSheet("background-color: white; border: 1px solid #e1e8ed; border-radius: 12px;")
        theme_layout = QVBoxLayout(theme_box)
        theme_layout.setContentsMargins(25, 20, 25, 25)
        theme_layout.setSpacing(15)
        
        lbl_theme = QLabel("🎨 Thème visuel de l'interface :")
        lbl_theme.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_theme.setStyleSheet("color: #1a2a3a; border: none; background: transparent;")
        
        self.radio_light = QRadioButton("Mode Clair (Fond Blanc)")
        self.radio_dark = QRadioButton("Mode Sombre (Fond Sombre)")
        self.radio_light.setChecked(True)
        self.radio_light.setFont(QFont("Segoe UI", 10))
        self.radio_dark.setFont(QFont("Segoe UI", 10))
        self.radio_light.setStyleSheet("border: none; background: transparent;")
        self.radio_dark.setStyleSheet("border: none; background: transparent;")
        
        theme_layout.addWidget(lbl_theme)
        theme_layout.addWidget(self.radio_light)
        theme_layout.addWidget(self.radio_dark)
        layout.addWidget(theme_box)
        
        layout.addStretch()
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.btn_appliquer = QPushButton("💾 Appliquer")
        self.btn_appliquer.setFixedSize(180, 48)
        self.btn_appliquer.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_appliquer.setCursor(Qt.PointingHandCursor)
        self.btn_appliquer.setStyleSheet("""
            QPushButton { background-color: #10ac84; color: white; border-radius: 10px; border: none; }
            QPushButton:hover { background-color: #0f9b75; }
        """)
        
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(15)
        btn_shadow.setXOffset(2)
        btn_shadow.setYOffset(5)
        btn_shadow.setColor(QColor(160, 175, 190, 100))
        self.btn_appliquer.setGraphicsEffect(btn_shadow)
        
        self.btn_appliquer.clicked.connect(self.save_settings)
        bottom_layout.addWidget(self.btn_appliquer)
        layout.addLayout(bottom_layout)
        
        return page

    def handle_internal_login(self):
        user = self.input_username.text()
        pwd = self.input_password.text()
        if not user or not pwd:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs !")
            return
            
        try:
            query = "SELECT * FROM utilisateurs WHERE nom_utilisateur = %s AND mot_de_passe = %s"
            self.cursor.execute(query, (user, pwd))
            result = self.cursor.fetchone()
            
            if result:
                QMessageBox.information(self, "Connexion Réussie", f"Bienvenue, {user} ! Connexion effectuée avec succès.")
            else:
                QMessageBox.critical(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect !")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erreur Base de Données", f"Erreur lors de la vérification : {err}")

    def save_settings(self):
        settings_data = {
            "langue": self.combo_lang.currentText(),
            "mode_sombre": self.radio_dark.isChecked(),
            "last_user": self.input_username.text()
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings_data, f)
            QMessageBox.information(self, "Succès", "Les modifications ont été appliquées et sauvegardées avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder les paramètres: {e}")

    def load_saved_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                lang = data.get("langue", "Français")
                idx = self.combo_lang.findText(lang)
                if idx >= 0: self.combo_lang.setCurrentIndex(idx)
                if data.get("mode_sombre", False):
                    self.radio_dark.setChecked(True)
                else:
                    self.radio_light.setChecked(True)
                self.input_username.setText(data.get("last_user", ""))
            except Exception as e:
                print(f"Erreur lors du chargement des paramètres: {e}")

    def update_kpi_values(self):
        try:
            count_sites = 0
            count_bureaux = 0
            count_agents = 0
            
            if self.db.is_connected():
                self.cursor.execute("SELECT COUNT(*) FROM sites")
                count_sites = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM bureau")
                count_bureaux = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM agent")
                count_agents = self.cursor.fetchone()[0]
            
            self.lbl_sites_val.setText(str(count_sites))
            self.lbl_bureaux_val.setText(str(count_bureaux))
            self.lbl_agents_val.setText(str(count_agents))

            # مبيان الأعمدة
            chart_bar = QChart()
            chart_bar.setTitle("Répartition des Bureaux par Site")
            chart_bar.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            chart_bar.setBackgroundVisible(False)
            
            set_db = QBarSet("Quantité")
            set_db.append([count_sites, count_bureaux, count_agents])
            set_db.setColor(QColor("#2e86de"))
            
            series_bar = QBarSeries()
            series_bar.append(set_db)
            chart_bar.addSeries(series_bar)
            
            categories = ["Sites", "Bureaux", "Agents"]
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            axis_x.setLabelsFont(QFont("Segoe UI", 9, QFont.Bold))
            chart_bar.addAxis(axis_x, Qt.AlignBottom)
            series_bar.attachAxis(axis_x)
            
            max_val = max([count_sites, count_bureaux, count_agents, 5])
            axis_y = QValueAxis()
            axis_y.setRange(0, float(max_val + 2))
            axis_y.setLabelsFont(QFont("Segoe UI", 9, QFont.Bold))
            chart_bar.addAxis(axis_y, Qt.AlignLeft)
            series_bar.attachAxis(axis_y)
            
            chart_bar.legend().setVisible(False)
            self.bar_chartview.setChart(chart_bar)

            # مبيان الدائرة
            chart_pie = QChart()
            chart_pie.setTitle("Status du Matériel / Données Globale")
            chart_pie.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            chart_pie.setBackgroundVisible(False)
            
            series_pie = QPieSeries()
            series_pie.append("Sites", max(count_sites, 1)).setColor(QColor("#10ac84"))
            series_pie.append("Bureaux", max(count_bureaux, 1)).setColor(QColor("#2e86de"))
            series_pie.append("Agents", max(count_agents, 1)).setColor(QColor("#ff9f43"))
            
            for slice_item in series_pie.slices():
                slice_item.setLabelVisible(True)
                slice_item.setLabelFont(QFont("Segoe UI", 9, QFont.Bold))
                slice_item.setLabelPosition(QPieSlice.LabelPositionOutside) 
                slice_item.setLabelArmLength(15) 
                
            chart_pie.addSeries(series_pie)
            chart_pie.legend().setFont(QFont("Segoe UI", 9, QFont.Bold))
            chart_pie.legend().setAlignment(Qt.AlignBottom)
            self.pie_chartview.setChart(chart_pie)

        except Exception as e:
            print(f"Erreur KPI: {e}")

    def display_page(self, index):
        self.pages.setCurrentIndex(index)
        if index == 0: self.update_kpi_values()
        elif index == 1: self.load_sites()
        elif index == 2: self.load_bureaux()
        elif index == 3: self.load_agents()
        elif index == 4: self.load_materiel()

    def create_action_buttons(self, table_widget, row_idx, id_value, edit_callback, delete_callback):
        container = QWidget()
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(6, 4, 6, 4)
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)

        btn_edit = QPushButton("📝")
        btn_edit.setToolTip("Modifier")
        btn_edit.setFixedSize(38, 34)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton { 
                background-color: #f1f5f9; 
                color: #334155; 
                border-radius: 6px; 
                border: 1px solid #cbd5e1; 
                font-size: 15px; 
            }
            QPushButton:hover { 
                background-color: #e2e8f0; 
                border: 1px solid #94a3b8; 
            }
        """)
        btn_edit.clicked.connect(lambda: edit_callback(id_value))

        btn_delete = QPushButton("🗑️")
        btn_delete.setToolTip("Supprimer")
        btn_delete.setFixedSize(38, 34)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton { 
                background-color: #f1f5f9; 
                color: #334155; 
                border-radius: 6px; 
                border: 1px solid #cbd5e1; 
                font-size: 15px; 
            }
            QPushButton:hover { 
                background-color: #fee2e2; 
                color: #991b1b;
                border: 1px solid #fca5a5; 
            }
        """)
        btn_delete.clicked.connect(lambda: delete_callback(id_value))

        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        table_widget.setCellWidget(row_idx, table_widget.columnCount() - 1, container)

    def export_site(self): QMessageBox.information(self, "Exporter", "Données des sites exportées avec succès.")
    def export_bureau(self): QMessageBox.information(self, "Exporter", "Données des bureaux exportées avec succès.")
    def export_agent(self): QMessageBox.information(self, "Exporter", "Données des agents exportées avec succès.")
    def export_materiel(self): QMessageBox.information(self, "Exporter", "Données du matériel exportées avec succès.")

    # ==========================================
    # 3. دالة الإضافة الجديدة والمطورة بالـ Custom Dialog
    # ==========================================
    def add_site(self):
        dialog = AddSiteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # التأكد من ملء الحقول المطلوبة
            if not data["nom"] or not data["ville"]:
                QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs (Nom et Ville) !")
                return
                
            try:
                # إدخال البيانات دفعة واحدة في استعلام واحد
                query = "INSERT INTO sites (nom_site, type_site, ville) VALUES (%s, %s, %s)"
                self.cursor.execute(query, (data["nom"], data["type"], data["ville"]))
                self.db.commit()
                
                # رسالة النجاح الأنيقة
                QMessageBox.information(self, "Succès", "Le site a été ajouté avec succès !")
                self.load_sites()  # تحديث الجدول فوراً
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Erreur base de données", f"Impossible d'ajouter le site : {err}")

    def edit_site(self, id_site):
        self.cursor.execute("SELECT nom_site, type_site, ville FROM sites WHERE id = %s", (id_site,))
        site = self.cursor.fetchone()
        if site:
            nom, ok1 = QInputDialog.getText(self, "Modifier Site", "Nom du Site :", QLineEdit.Normal, site[0])
            type_s, ok2 = QInputDialog.getText(self, "Modifier Site", "Type du Site :", QLineEdit.Normal, site[1])
            ville, ok3 = QInputDialog.getText(self, "Modifier Site", "Ville :", QLineEdit.Normal, site[2])
            if ok1 and ok2 and ok3 and nom:
                self.cursor.execute("UPDATE sites SET nom_site=%s, type_site=%s, ville=%s WHERE id=%s", (nom, type_s, ville, id_site))
                self.db.commit()
                self.load_sites()

    def delete_site(self, id_site):
        msg = QMessageBox.question(self, "Supprimer", "Voulez-vous vraiment supprimer ce site ?", QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM sites WHERE id = %s", (id_site,))
            self.db.commit()
            self.load_sites()

    def add_bureau(self):
        code, ok1 = QInputDialog.getText(self, "Ajouter Bureau", "Code Bureau :")
        nom, ok2 = QInputDialog.getText(self, "Ajouter Bureau", "Nom Bureau :")
        id_site, ok3 = QInputDialog.getInt(self, "Ajouter Bureau", "ID du Site associé :")
        if ok1 and ok2 and ok3:
            self.cursor.execute("INSERT INTO bureau (code_bureau, nom_bureau, id_site) VALUES (%s, %s, %s)", (code, nom, id_site))
            self.db.commit()
            self.load_bureaux()

    def edit_bureau(self, id_bureau):
        self.cursor.execute("SELECT code_bureau, nom_bureau, id_site FROM bureau WHERE id_bureau = %s", (id_bureau,))
        bureau = self.cursor.fetchone()
        if bureau:
            code, ok1 = QInputDialog.getText(self, "Modifier Bureau", "Code Bureau :", QLineEdit.Normal, bureau[0])
            nom, ok2 = QInputDialog.getText(self, "Modifier Bureau", "Nom Bureau :", QLineEdit.Normal, bureau[1])
            id_site, ok3 = QInputDialog.getInt(self, "Modifier Bureau", "ID du Site associé :", bureau[2])
            if ok1 and ok2 and ok3:
                self.cursor.execute("UPDATE bureau SET code_bureau=%s, nom_bureau=%s, id_site=%s WHERE id_bureau=%s", (code, nom, id_site, id_bureau))
                self.db.commit()
                self.load_bureaux()

    def delete_bureau(self, id_bureau):
        msg = QMessageBox.question(self, "Supprimer", "Voulez-vous vraiment supprimer ce bureau ?", QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM bureau WHERE id_bureau = %s", (id_bureau,))
            self.db.commit()
            self.load_bureaux()

    def add_agent(self):
        nom, ok1 = QInputDialog.getText(self, "Ajouter Agent", "Nom de l'Agent :")
        id_bureau, ok2 = QInputDialog.getInt(self, "Ajouter Agent", "ID du Bureau affecté :")
        if ok1 and ok2:
            self.cursor.execute("INSERT INTO agent (nom_agent, id_bureau) VALUES (%s, %s)", (nom, id_bureau))
            self.db.commit()
            self.load_agents()

    def edit_agent(self, id_agent):
        self.cursor.execute("SELECT nom_agent, id_bureau FROM agent WHERE id_agent = %s", (id_agent,))
        agent = self.cursor.fetchone()
        if agent:
            nom, ok1 = QInputDialog.getText(self, "Modifier Agent", "Nom de l'Agent :", QLineEdit.Normal, agent[0])
            id_bureau, ok2 = QInputDialog.getInt(self, "Modifier Agent", "ID du Bureau affecté :", agent[1])
            if ok1 and ok2:
                self.cursor.execute("UPDATE agent SET nom_agent=%s, id_bureau=%s WHERE id_agent=%s", (nom, id_bureau, id_agent))
                self.db.commit()
                self.load_agents()

    def delete_agent(self, id_agent):
        msg = QMessageBox.question(self, "Supprimer", "Voulez-vous vraiment supprimer cet agent ?", QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM agent WHERE id_agent = %s", (id_agent,))
            self.db.commit()
            self.load_agents()

    def add_materiel(self):
        nom, ok = QInputDialog.getText(self, "Ajouter Matériel", "Désignation du Matériel :")
        if ok and nom:
            self.cursor.execute("INSERT INTO materiel (nom_type) VALUES (%s)", (nom,))
            self.db.commit()
            self.load_materiel()

    def edit_materiel(self, id_mat):
        self.cursor.execute("SELECT nom_type FROM materiel WHERE id_materiel = %s", (id_mat,))
        mat = self.cursor.fetchone()
        if mat:
            nom, ok = QInputDialog.getText(self, "Modifier Matériel", "Désignation du Matériel :", QLineEdit.Normal, mat[0])
            if ok and nom:
                self.cursor.execute("UPDATE materiel SET nom_type=%s WHERE id_materiel=%s", (nom, id_mat))
                self.db.commit()
                self.load_materiel()

    def delete_materiel(self, id_mat):
        msg = QMessageBox.question(self, "Supprimer", "Voulez-vous vraiment supprimer ce matériel ?", QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM materiel WHERE id_materiel = %s", (id_mat,))
            self.db.commit()
            self.load_materiel()

    def load_sites(self):
        self.cursor.execute("SELECT id, nom_site, type_site, ville FROM sites")
        self.fill_table(self.table_sites, ["ID", "Nom du Site", "Type", "Ville", "Actions"], self.cursor.fetchall(), self.edit_site, self.delete_site)

    def load_bureaux(self):
        self.cursor.execute("SELECT b.id_bureau, b.code_bureau, b.nom_bureau, s.nom_site FROM bureau b LEFT JOIN sites s ON b.id_site = s.id")
        self.fill_table(self.table_bureaux, ["ID", "Code Bureau", "Nom Bureau", "Site", "Actions"], self.cursor.fetchall(), self.edit_bureau, self.delete_bureau)

    def load_agents(self):
        self.cursor.execute("SELECT a.id_agent, a.nom_agent, b.nom_bureau FROM agent a LEFT JOIN bureau b ON a.id_bureau = b.id_bureau")
        self.fill_table(self.table_agents, ["ID", "Nom de l'Agent", "Bureau Affecté", "Actions"], self.cursor.fetchall(), self.edit_agent, self.delete_agent)

    def load_materiel(self):
        self.cursor.execute("SELECT id_materiel, nom_type FROM materiel")
        self.fill_table(self.table_materiel, ["ID", "Désignation Matériel", "Actions"], self.cursor.fetchall(), self.edit_materiel, self.delete_materiel)

    def fill_table(self, table_widget, headers, rows, edit_callback=None, delete_callback=None):
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.setRowCount(0)
        
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if "Actions" in headers:
            table_widget.horizontalHeader().setSectionResizeMode(len(headers)-1, QHeaderView.ResizeToContents)

        for row_idx, row_data in enumerate(rows):
            table_widget.insertRow(row_idx)
            id_value = str(row_data[0]) 
            
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                table_widget.setItem(row_idx, col_idx, item)
            
            if edit_callback and delete_callback:
                self.create_action_buttons(table_widget, row_idx, id_value, edit_callback, delete_callback)

    def handle_logout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        msg.setText("Voulez-vous vraiment vous déconnecter ?")
        msg.setFont(QFont("Segoe UI", 10, QFont.Bold))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes: self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = SRMStockManager()
    window.show()
    sys.exit(app.exec_())