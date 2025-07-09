from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


class SaveComponent(QListWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = parent

        # Save list and context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Save action buttons
        self.import_button = QPushButton('Import Savestate', self)
        self.load_button = QPushButton('Load Savestate', self)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.import_button)
        self.h_layout.addWidget(self.load_button)
