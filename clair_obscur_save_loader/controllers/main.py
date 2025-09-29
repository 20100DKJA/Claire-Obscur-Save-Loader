import sys

from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader import config
from clair_obscur_save_loader import managers
from clair_obscur_save_loader import views

from .controls import ControlsController
from .initial_setup import InitialSetupController
from .profile import ProfileController
from .settings import SettingsController


class MainController:
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)
        self._config = config.Config()
        self._view = views.MainWindow()

        self._view.applyStyle(self._app)

        self.load_geometry()
        self._view.new_geometry.connect(self.save_geometry)

        profile_manager = managers.ProfileManager()
        save_manager = managers.SaveManager(profile_manager=profile_manager)

        self._initial_setup_controller = InitialSetupController(
            view=self._view.setup,
            save_manager=save_manager,
            config=self._config,
        )
        if not self._config.is_configured():
            self._view.setup.exec()
        if not self._config.is_configured():
            return

        settings = SettingsController(
            view=self._view.settings,
            config=self._config,
            profile_manager=profile_manager,
        )
        settings.saved.connect(self.config_update)

        self._controls_controller = ControlsController(
            view=self._view.controls,
            config=self._config,
        )

        self._profile_controller = ProfileController(
            profile_view=self._view.profile,
            save_view=self._view.save,
            popup_view=self._view.popup,
            controls_controller=self._controls_controller,
            settings_controller=settings,
            config=self._config,
            profile_manager=profile_manager,
            save_manager=save_manager,
        )

    def config_update(self) -> None:
        self._controls_controller.configUpdate()

    def save_geometry(self) -> None:
        geom_data = self._view.saveGeometry()
        self._config.geometry = geom_data.toBase64().data().decode('ascii')
        self._config.save_config()

    def load_geometry(self) -> None:
        last_geometry = self._config.geometry
        if last_geometry is None:
            return
        geom_data = QByteArray.fromBase64(
            last_geometry.encode('ascii'),
            QByteArray.Base64Options(
                QByteArray.Base64Option.Base64Encoding
                | QByteArray.Base64Option.AbortOnBase64DecodingErrors
            ),
        )
        if geom_data.size() > 0:
            self._view.restoreGeometry(geom_data)

    def run(self) -> int:
        if not self._config.is_configured():
            return 1
        self._view.show()
        return self._app.exec_()
