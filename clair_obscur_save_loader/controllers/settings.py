from typing import cast

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget

from clair_obscur_save_loader.managers.main import MainManager
from clair_obscur_save_loader.views.settings import SettingsComponent


class SettingsController(QObject):
    def __init__(self, *, view: SettingsComponent, manager: MainManager) -> None:
        super().__init__()
        self._manager = manager
        self._view = view
        self.setupConnections()

    def setupConnections(self) -> None:
        self._view.continue_button.clicked.connect(self.accept)
        self._view.select_button.clicked.connect(self.browseSaveLocation)
        self._view.exit_button.clicked.connect(self.reject)

    def browseSaveLocation(self) -> None:
        folder = QFileDialog.getExistingDirectory(self._view, 'Select Game Save Directory', '')

        if folder:
            # Try to configure the save location
            if self._manager.set_save_location(folder):
                self._view.path_label.setText(f'Selected: {folder}')
                self._view.continue_button.setEnabled(True)
            else:
                QMessageBox.warning(
                    self._view,
                    'Invalid Directory',
                    'The selected directory does not appear to be a valid game save location.\n'
                    'Please select a directory containing at least one numeric subfolder.',
                )

    def accept(self) -> None:
        if self._manager.is_configured:
            self._manager.save_config()
            QMessageBox.information(self._view.root, 'Success', 'Configuration successful!\n')
            self._view.close()
        else:
            QMessageBox.critical(
                self._view.root,
                'Configuration Failed',
                'Unable to configure the save location.\n'
                'Please select a valid game save directory.',
            )

    def reject(self) -> None:
        cast('QWidget', self._view.root).close()
