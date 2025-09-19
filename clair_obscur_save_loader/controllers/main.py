import sys

from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader import config
from clair_obscur_save_loader import managers
from clair_obscur_save_loader import views

from .initial_setup import InitialSetupController
from .profile import ProfileController


class MainController:
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)
        self._config = config.Config()
        self._manager = managers.MainManager()
        self._view = views.MainWindow()

        self._initial_setup_controller = InitialSetupController(
            view=self._view.setup, manager=self._manager
        )
        if not self._manager.is_configured:
            self._view.setup.exec()

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
