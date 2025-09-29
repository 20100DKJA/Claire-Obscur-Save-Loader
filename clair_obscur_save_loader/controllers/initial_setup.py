import os

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.managers import SaveManager
from clair_obscur_save_loader.managers.save import find_active_save_path
from clair_obscur_save_loader.views.initial_setup import InitialSetupComponent


class InitialSetupController(QObject):
    def __init__(
        self, *, view: InitialSetupComponent, save_manager: SaveManager, config: Config
    ) -> None:
        super().__init__()
        self._save_manager = save_manager
        self._config = config
        self._view = view
        self.setupConnections()

    def setupConnections(self) -> None:
        self._view.continue_button.clicked.connect(self.accept)
        self._view.select_button.clicked.connect(self.browseSaveLocation)
        self._view.exit_button.clicked.connect(self.reject)

    def _set_save_location(self, location: str) -> bool:
        save_location = find_active_save_path(location)
        if save_location is None:
            return False

        self._config.save_location = location

        return True

    def browseSaveLocation(self) -> None:
        folder = QFileDialog.getExistingDirectory(self._view, 'Select Game Save Directory', '')

        if folder:
            # Try to configure the save location
            folder = os.path.normpath(folder)
            if self._set_save_location(folder):
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
        if self._config.is_configured():
            self._config.save_config()
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
        QApplication.quit()
