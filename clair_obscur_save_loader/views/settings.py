from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class SettingsWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle('Settings')
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setModal(True)

        self.initUI()

    def initUI(self) -> None:
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.startup_profile = QComboBox()
        form_layout.addRow('Startup Profile:', self.startup_profile)

        restart_layout = QVBoxLayout()
        self.restart_command_choice = QComboBox()
        self.restart_command_choice.addItem('<disabled>', '')
        self.restart_command_choice.addItem(
            'Windows (Steam)',
            'taskkill /F /im SandFall-Win64-Shipping.exe & start steam://rungameid/1903340',
        )
        self.restart_command_choice.addItem(
            'Windows (Game Pass)',
            'taskkill /F /im SandFall-WinGDK-Shipping.exe & explorer.exe shell:AppsFolder\\'
            + 'KeplerInteractive.Expedition33_ymj30pw7xe604!AppExpedition33Shipping',
        )
        self.restart_command_choice.addItem(
            'Linux (Steam)',
            'pkill -A -f SandFall-Win64-Shipping.exe; pidwait -A -f SandFall-Win64-Shipping.exe; '
            + 'xdg-open "steam://rungameid/1903340"',
        )
        self.restart_command_choice.addItem('Custom Command', '')
        restart_layout.addWidget(self.restart_command_choice)
        self.restart_command = QLineEdit()
        self.restart_command.setVisible(False)
        restart_layout.addWidget(self.restart_command)
        form_layout.addRow('Restart Command:', restart_layout)

        layout.addLayout(form_layout)

        action_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.cancel_button = QPushButton('Cancel')
        action_layout.addWidget(self.save_button)
        action_layout.addWidget(self.cancel_button)
        layout.addLayout(action_layout)

        self.setLayout(layout)
