from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class ProfileComponent(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = parent

        self.buttons: dict[str, QPushButton] = {}

        # Profile selection
        self.setEditable(True)
        edit = self.lineEdit()

        edit.setReadOnly(True)
        edit.setPlaceholderText('Select')
        self.setInsertPolicy(QComboBox.NoInsert)

        # Profile buttons
        self.vbox_profile = QVBoxLayout()
        for label in [
            'Create Profile',
            'Delete Profile',
            'Duplicate Profile',
            'Rename Profile',
        ]:
            self.buttons[label] = QPushButton(label, self.root)
            self.vbox_profile.addWidget(self.buttons[label], alignment=Qt.AlignTop)

    def currentProfile(self) -> str:
        return self.currentText()
