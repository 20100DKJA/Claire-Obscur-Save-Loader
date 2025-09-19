from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class SettingsWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle('Settings')
        self.setMinimumWidth(650)
        self.setMinimumHeight(250)
        self.setModal(True)

        self.initUI()

    def initUI(self) -> None:
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.startup_profile = QComboBox()
        form_layout.addRow('Startup Profile:', self.startup_profile)

        layout.addLayout(form_layout)

        action_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.cancel_button = QPushButton('Cancel')
        action_layout.addWidget(self.save_button)
        action_layout.addWidget(self.cancel_button)
        layout.addLayout(action_layout)

        self.setLayout(layout)
