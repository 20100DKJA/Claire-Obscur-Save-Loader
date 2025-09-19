from PyQt5.QtCore import QObject

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.managers import ProfileManager
from clair_obscur_save_loader.views.settings import SettingsWindow


class SettingsController(QObject):
    def __init__(
        self,
        *,
        view: SettingsWindow,
        config: Config,
        profile_manager: ProfileManager,
    ) -> None:
        super().__init__()

        self._view = view
        self._config = config
        self._profile_manager = profile_manager
        self.setupConnections()

    def setupConnections(self) -> None:
        self._view.save_button.clicked.connect(self.save)
        self._view.cancel_button.clicked.connect(self.cancel)

    def loadSettings(self) -> None:
        self._view.startup_profile.clear()
        self._view.startup_profile.addItem('<last selected profile>')
        self._view.startup_profile.addItems(self._profile_manager.get_list_of_profiles())
        if self._config.startup_profile is None:
            self._view.startup_profile.setCurrentIndex(0)
        else:
            self._view.startup_profile.setCurrentText(self._config.startup_profile)

    def saveSettings(self) -> None:
        self._config.startup_profile = (
            None
            if self._view.startup_profile.currentIndex() < 1
            else self._view.startup_profile.currentText()
        )
        self._config.save_config()

    def save(self) -> None:
        self.saveSettings()
        self._view.hide()

    def cancel(self) -> None:
        self._view.hide()

    def show(self) -> None:
        self.loadSettings()
        self._view.show()
