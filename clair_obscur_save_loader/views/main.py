import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget

from clair_obscur_save_loader.definitions import APP_TITLE

from .label import LabelComponent
from .popup import PopUpComponent
from .profile import ProfileComponent
from .save import SaveComponent
from .settings import SettingsComponent


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(0, 0, 500, 500)
        self.initUI()

    def applyStyle(self) -> None:
        self.setStyleSheet("""
            QMainWindow{
                background-color: #181818;
            }
            QListWidget{
                background-color: #1f1f1f;
                color: #cccccc;
            }
            QComboBox{
                background-color: #2c2c2c;
                color: #cccccc;
            }
            QComboBox QAbstractItemView {
                background: #2c2c2c;

                color: #cccccc;
                selection-background-color: #cccccc;
                selection-color: #5f5f5f;
            }

            QPushButton{
                background-color :  #5f5f5f;
                color : #eeeeee;
            }

            QPushButton:hover{
                background-color :  #cccccc;
                color : #5f5f5f;
            }
        """)

    def initUI(self) -> None:
        base = (
            sys._MEIPASS
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
            else os.path.join(os.path.dirname(__file__))
        )
        icon_path = os.path.join(base, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.applyStyle()

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setSpacing(5)

        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.label = LabelComponent(self)
        self.popup = PopUpComponent(self)
        self.profile = ProfileComponent(self)
        self.save = SaveComponent(self)
        self.settings = SettingsComponent(self)

        # Layout positioning
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.profile, 0, 1)
        layout.addLayout(self.profile.vbox_profile, 1, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.save, 1, 0)
        layout.addLayout(self.save.h_layout, 2, 0)
        layout.addWidget(self.popup, 3, 0)
