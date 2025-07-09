from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget


class PopUpComponent(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__('', parent)
        self.root = parent

        # Popup message label
        self.setFont(QFont('Helvetica', 15))
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
