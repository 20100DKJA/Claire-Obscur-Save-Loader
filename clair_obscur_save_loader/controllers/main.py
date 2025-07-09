import sys

from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader import config
from clair_obscur_save_loader import managers
from clair_obscur_save_loader import views

from .profile import ProfileController
from .settings import SettingsController


class MainController:
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)
        self._config = config.Config()
        self._manager = managers.MainManager()
        self._view = views.MainWindow()

        self._settings_controller = SettingsController(
            view=self._view.settings, manager=self._manager
        )
        if not self._manager.is_configured:
            self._view.settings.exec()

        profile_manager = managers.ProfileManager()

        self._profile_controller = ProfileController(
            profile_view=self._view.profile,
            save_view=self._view.save,
            popup_view=self._view.popup,
            profile_manager=profile_manager,
            save_manager=managers.SaveManager(profile_manager=profile_manager),
        )

    def run(self) -> int:
        self._view.show()
        return self._app.exec_()
