import sys
import os
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
                             QMessageBox, QComboBox, QRadioButton, QInputDialog,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent, QPoint
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries

class HoverHandler(QStackedWidget):
    """ كلاس مخصص للتعامل مع تأثيرات الحركة عند مرور الفأرة """
    def __init__(self, target_widget, is_card=False):
        super().__init__()
        self.target = target_widget
        self.is_card = is_card

class SRMStockManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRM SM - GESTION DE STOCK v3.0 3D")
        self.resize(1400, 880)
        
        # Connexion a la Base de Donnees
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
                                 f"Impossible de se connecter a MySQL.\n"
                                 f"Veuillez verifier que le serveur MySQL est active sur XAMPP !\n\nDetails: {err}")
            sys.exit()

        self.initUI()

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

        self.display_page(0)

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

        # أزرار القائمة الجانبية
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
            QPushButton:hover { background-color: #10ac84; color: white; }
        """)
        # إضافة مستشعر الحركة للأزرار الجانبية (تتحرك قليلاً لليمين عند لمسها)
        btn.installEventFilter(self)
        return btn

    def setup_content(self):
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background-color: #f4f6f9;")
        
        self.table_sites = self.create_table()
        self.table_bureaux = self.create_table()
        self.table_agents = self.create_table()
        self.table_materiel = self.create_table()

        self.pages.addWidget(self.create_kpi_page())
        self.pages.addWidget(self.create_page_layout("GESTION DES SITES", self.table_sites, self.add_site, self.delete_site))
        self.pages.addWidget(self.create_page_layout("GESTION DES BUREAUX", self.table_bureaux, self.add_bureau, self.delete_bureau))
        self.pages.addWidget(self.create_page_layout("GESTION DES AGENTS", self.table_agents, self.add_agent, self.delete_agent))
        self.pages.addWidget(self.create_page_layout("TYPES DE MATÉRIEL", self.table_materiel, self.add_materiel, self.delete_materiel))
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
            QHeaderView::section { background-color: #10ac84; color: white; padding: 8px; border: none; }
        """)
        return table

    def create_page_layout(self, title_text, table_obj, add_callback, delete_callback):
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
        btn_delete = QPushButton("🗑️ Supprimer")
        btn_refresh = QPushButton("🔄 Actualiser")
        
        for btn, color, hover in [(btn_add, "#10ac84", "#0f9b75"), (btn_delete, "#ee5253", "#d63031"), (btn_refresh, "#2e86de", "#1b6ca8")]:
            btn.setFixedSize(110, 35)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border-radius: 4px; }}"
                              f"QPushButton:hover {{ background-color: {hover}; }}")
            header_layout.addWidget(btn)

        btn_add.clicked.connect(add_callback)
        btn_delete.clicked.connect(delete_callback)
        btn_refresh.clicked.connect(self.refresh_current_page)
        
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
        
        # كروت إحصائية ثلاثية الأبعاد وبارزة بالكامل مع أنيميشن عند لمسها
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
        # إضافة تأثير عمق 3D للمبيان الأول
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
        # إضافة تأثير عمق 3D للمبيان الثاني
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
        # تصميم ثلاثي أبعاد حقيقي ونظيف (Soft 3D / Neumorphic Style)
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white; 
                border: 1px solid #e2e8f0; 
                border-radius: 15px;
            }}
        """)
        
        # إضافة تأثير الظل ثلاثي الأبعاد العميق للكارت
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
        
        # لوحة الأيقونة المجسمة بالدائرة الملونة الخفيفة
        icon_panel = QFrame()
        icon_panel.setFixedSize(55, 55)
        icon_panel.setStyleSheet(f"background-color: {bg_icon_color}; border-radius: 27px; border: none;")
        
        panel_layout = QVBoxLayout(icon_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 22)) # أيقونات مجسمة وبارزة
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent;")
        panel_layout.addWidget(lbl_icon)
        
        card_layout.addWidget(text_container)
        card_layout.addStretch()
        card_layout.addWidget(icon_panel)
        
        # تفعيل تتبع الأحداث والتحريك للكارت عند ملامسة الفأرة
        card.setMouseTracking(True)
        card.installEventFilter(self)
        
        return card

    def eventFilter(self, watched, event):
        """ فلتر الأحداث لصناعة حركات (Animations) تفاعلية وسلسة مثل التطبيقات الاحترافية """
        # 1. حركة الأزرار الجانبية (تتحرك قليلاً لليمين وتغير لون الخط)
        if isinstance(watched, QPushButton) and watched in [self.btn_kpi, self.btn_sites, self.btn_bureaux, self.btn_agents, self.btn_materiel, self.btn_settings, self.btn_logout]:
            if event.type() == QEvent.Enter:
                watched.setStyleSheet("background-color: #10ac84; color: white; padding-left: 25px; border-radius: 5px;")
            elif event.type() == QEvent.Leave:
                watched.setStyleSheet("background-color: transparent; color: #FFFFFF; padding-left: 15px; border-radius: 5px;")

        # 2. حركة الكروت العلوية (ترتفع للأعلى قليلاً لتأكيد اللمس ثلاثي الأبعاد)
        elif isinstance(watched, QFrame) and watched.objectName() == "StatCard":
            if event.type() == QEvent.Enter:
                watched.window().setCursor(Qt.PointingHandCursor)
                # رفع الكارت للأعلى قليلاً وإعطاء تأثير ظل أعمق
                watched.setStyleSheet("background-color: #ffffff; border: 1px solid #10ac84; border-radius: 15px;")
                if watched.graphicsEffect():
                    watched.graphicsEffect().setYOffset(12)
                    watched.graphicsEffect().setBlurRadius(25)
            elif event.type() == QEvent.Leave:
                watched.window().setCursor(Qt.ArrowCursor)
                watched.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 15px;")
                if watched.graphicsEffect():
                    watched.graphicsEffect().setYOffset(8)
                    watched.graphicsEffect().setBlurRadius(20)

        return super().eventFilter(watched, event)

    def update_kpi_values(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM sites")
            count_sites = self.cursor.fetchone()[0]
            self.card_sites.findChildren(QLabel)[1].setText(str(count_sites))
            
            self.cursor.execute("SELECT COUNT(*) FROM bureau")
            count_bureaux = self.cursor.fetchone()[0]
            self.card_bureaux.findChildren(QLabel)[1].setText(str(count_bureaux))
            
            self.cursor.execute("SELECT COUNT(*) FROM agent")
            count_agents = self.cursor.fetchone()[0]
            self.card_agents.findChildren(QLabel)[1].setText(str(count_agents))

            # مبيان أعمدة احترافي ومتناسق
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
            
            axis_y = QValueAxis()
            axis_y.setRange(0, max([count_sites, count_bureaux, count_agents, 5]) + 2)
            axis_y.setLabelsFont(QFont("Segoe UI", 9, QFont.Bold))
            chart_bar.addAxis(axis_y, Qt.AlignLeft)
            series_bar.attachAxis(axis_y)
            
            chart_bar.legend().setVisible(False)
            self.bar_chartview.setChart(chart_bar)

            # مبيان دائري احترافي ومتناسق
            chart_pie = QChart()
            chart_pie.setTitle("Status du Matériel / Données Globale")
            chart_pie.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            chart_pie.setBackgroundVisible(False)
            
            series_pie = QPieSeries()
            series_pie.append("Sites", count_sites).setColor(QColor("#10ac84"))
            series_pie.append("Bureaux", count_bureaux).setColor(QColor("#2e86de"))
            series_pie.append("Agents", count_agents).setColor(QColor("#ff9f43"))
            
            for slice in series_pie.slices():
                slice.setLabelVisible(True)
                slice.setLabelFont(QFont("Segoe UI", 9, QFont.Bold))
                
            chart_pie.addSeries(series_pie)
            chart_pie.legend().setFont(QFont("Segoe UI", 9, QFont.Bold))
            chart_pie.legend().setAlignment(Qt.AlignBottom)
            self.pie_chartview.setChart(chart_pie)

        except Exception as e:
            print(f"Erreur KPI: {e}")

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        title = QLabel("⚙️ PARAMÈTRES DE L'APPLICATION")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        lang_box = QFrame()
        lang_box.setStyleSheet("background-color: white; border: 1px solid #e1e8ed; border-radius: 8px; padding: 20px;")
        lang_layout = QVBoxLayout(lang_box)
        lbl_lang = QLabel("Sélectionner la Langue de l'application :")
        lbl_lang.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Français", "Arabe", "English"])
        self.combo_lang.setFont(QFont("Segoe UI", 10))
        lang_layout.addWidget(lbl_lang)
        lang_layout.addWidget(self.combo_lang)
        layout.addWidget(lang_box)
        
        theme_box = QFrame()
        theme_box.setStyleSheet("background-color: white; border: 1px solid #e1e8ed; border-radius: 8px; padding: 20px;")
        theme_layout = QVBoxLayout(theme_box)
        lbl_theme = QLabel("Thème visuel de l'interface :")
        lbl_theme.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        self.radio_light = QRadioButton("Mode Clair (Fond Blanc)")
        self.radio_dark = QRadioButton("Mode Sombre (Fond Sombre)")
        self.radio_light.setChecked(True)
        self.radio_light.setFont(QFont("Segoe UI", 10))
        self.radio_dark.setFont(QFont("Segoe UI", 10))
        
        theme_layout.addWidget(lbl_theme)
        theme_layout.addWidget(self.radio_light)
        theme_layout.addWidget(self.radio_dark)
        layout.addWidget(theme_box)
        
        layout.addStretch()
        return page

    def display_page(self, index):
        self.pages.setCurrentIndex(index)
        if index == 0: self.update_kpi_values()
        elif index == 1: self.load_sites()
        elif index == 2: self.load_bureaux()
        elif index == 3: self.load_agents()
        elif index == 4: self.load_materiel()

    def refresh_current_page(self):
        self.display_page(self.pages.currentIndex())

    # --- FUNCTIONS CRUD ORIGINALES ---
    def add_site(self):
        nom, ok1 = QInputDialog.getText(self, "Ajouter Site", "Nom du Site :")
        type_s, ok2 = QInputDialog.getText(self, "Ajouter Site", "Type du Site :")
        ville, ok3 = QInputDialog.getText(self, "Ajouter Site", "Ville :")
        if ok1 and ok2 and ok3 and nom:
            self.cursor.execute("INSERT INTO sites (nom_site, type_site, ville) VALUES (%s, %s, %s)", (nom, type_s, ville))
            self.db.commit()
            self.load_sites()

    def delete_site(self):
        row = self.table_sites.currentRow()
        if row >= 0:
            id_site = self.table_sites.item(row, 0).text()
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

    def delete_bureau(self):
        row = self.table_bureaux.currentRow()
        if row >= 0:
            id_bureau = self.table_bureaux.item(row, 0).text()
            self.cursor.execute("DELETE FROM bureau WHERE id_bureau = %s", (id_bureau,))
            self.db.commit()
            self.load_bureaux()

    def add_agent(self):
        nom, ok1 = QInputDialog.getText(self, "Ajouter Agent", "Nom de l'Agent :")
        id_bureau, ok2 = QInputDialog.getInt(self, "Ajouter Agent", "ID du Bureau affecté :")
        if ok1 and ok2:
            self.cursor.execute("INSERT INTO agent (nom_agent, id_bureau) VALUES (%s)", (nom, id_bureau))
            self.db.commit()
            self.load_agents()

    def delete_agent(self):
        row = self.table_agents.currentRow()
        if row >= 0:
            id_agent = self.table_agents.item(row, 0).text()
            self.cursor.execute("DELETE FROM agent WHERE id_agent = %s", (id_agent,))
            self.db.commit()
            self.load_agents()

    def add_materiel(self):
        nom, ok = QInputDialog.getText(self, "Ajouter Matériel", "Désignation du Matériel :")
        if ok and nom:
            self.cursor.execute("INSERT INTO materiel (nom_type) VALUES (%s)", (nom,))
            self.db.commit()
            self.load_materiel()

    def delete_materiel(self):
        row = self.table_materiel.currentRow()
        if row >= 0:
            id_mat = self.table_materiel.item(row, 0).text()
            self.cursor.execute("DELETE FROM materiel WHERE id_materiel = %s", (id_mat,))
            self.db.commit()
            self.load_materiel()

    def load_sites(self):
        self.cursor.execute("SELECT id, nom_site, type_site, ville FROM sites")
        self.fill_table(self.table_sites, ["ID", "Nom du Site", "Type", "Ville"], self.cursor.fetchall())

    def load_bureaux(self):
        self.cursor.execute("SELECT b.id_bureau, b.code_bureau, b.nom_bureau, s.nom_site FROM bureau b LEFT JOIN sites s ON b.id_site = s.id")
        self.fill_table(self.table_bureaux, ["ID", "Code Bureau", "Nom Bureau", "Site"], self.cursor.fetchall())

    def load_agents(self):
        self.cursor.execute("SELECT a.id_agent, a.nom_agent, b.nom_bureau FROM agent a LEFT JOIN bureau b ON a.id_bureau = b.id_bureau")
        self.fill_table(self.table_agents, ["ID", "Nom de l'Agent", "Bureau Affecté"], self.cursor.fetchall())

    def load_materiel(self):
        self.cursor.execute("SELECT id_materiel, nom_type FROM materiel")
        self.fill_table(self.table_materiel, ["ID", "Désignation Matériel"], self.cursor.fetchall())

    def fill_table(self, table_widget, headers, rows):
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            table_widget.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                table_widget.setItem(row_idx, col_idx, item)

    def handle_logout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        msg.setText("Voulez-vous vraiment vous déconnecter ?")
        msg.setFont(QFont("Segoe UI", 10, QFont.Bold))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = SRMStockManager()
    window.show()
    sys.exit(app.exec_())