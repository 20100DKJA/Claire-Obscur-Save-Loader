from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from clair_obscur_save_loader.definitions import APP_TITLE
from clair_obscur_save_loader.definitions import Color


class LabelComponent(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(APP_TITLE, parent)
        self.root = parent
        self.setFont(QFont('Helvetica', 15))
        self.setStyleSheet(f'color: {Color.INFO}')
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
