from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class SettingsComponent(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = parent

        self.setWindowTitle('Initial Setup')
        self.setMinimumWidth(450)
        self.setMinimumHeight(250)
        self.setModal(True)  # Bloque l'interaction avec la fenêtre principale

        self.initUI()

    def initUI(self) -> None:
        layout = QVBoxLayout()

        # Message d'explication
        info_label = QLabel(
            'Welcome to Claire Obscur Save Loader!\n\n'
            'To get started, you need to select the game save directory.\n'
            'This is typically located at:\n\n'
            '• Windows (Microsoft Store): %LOCALAPPDATA%\\Sandfall\\Saved\\SaveGames\n'
            '• Windows (Steam): C:\\Program Files (x86)\\Steam\\steamapps\\common\\[game]\\SaveGames\n'  # noqa: E501
            '• Linux (Steam): ~/.steam/steam/steamapps/common/[game]/SaveGames\n\n'
            'The correct folder should contain at least one numeric subfolder.\n'
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Bouton de sélection
        button_layout = QHBoxLayout()
        self.path_label = QLabel('No path selected')
        self.path_label.setWordWrap(True)

        self.select_button = QPushButton('Select Game Save Directory')

        button_layout.addWidget(self.select_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.path_label)

        # Boutons d'action
        action_layout = QHBoxLayout()
        self.continue_button = QPushButton('Continue')
        self.continue_button.setEnabled(False)

        self.exit_button = QPushButton('Exit')

        action_layout.addWidget(self.continue_button)
        action_layout.addWidget(self.exit_button)

        layout.addLayout(action_layout)

        self.setLayout(layout)
