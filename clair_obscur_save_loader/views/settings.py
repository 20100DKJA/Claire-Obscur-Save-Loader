from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from clair_obscur_save_loader.config import SaveDoubleClickAction


class SettingsWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle('Settings')
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setModal(True)

        self.initUI()

    def initUI(self) -> None:
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.startup_profile = QComboBox()
        form_layout.addRow('Startup Profile:', self.startup_profile)

        self.expand_all_on_startup = QCheckBox('Expand all folders')
        form_layout.addRow('On Startup:', self.expand_all_on_startup)

        self.double_click_action = QComboBox()
        self.double_click_action.addItem('Do nothing', SaveDoubleClickAction.DO_NOTHING)
        self.double_click_action.addItem('Load save', SaveDoubleClickAction.LOAD_SAVE)
        self.double_click_action.addItem(
            'Load save and restart game', SaveDoubleClickAction.LOAD_SAVE_AND_RESTART_GAME
        )
        form_layout.addRow('On Double-Click Save:', self.double_click_action)

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

        action_layout = QDialogButtonBox(Qt.Horizontal)
        self.cancel_button = QPushButton('Cancel')
        self.save_button = QPushButton('Save')
        self.cancel_button.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DialogCancelButton))
        )
        self.save_button.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DialogOkButton))
        )
        action_layout.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        action_layout.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        layout.addWidget(action_layout)

        self.setLayout(layout)
