import subprocess  # noqa: S404 # Shell injection is a feature here

from PyQt5.QtCore import QObject

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.views.controls import ControlsComponent


class ControlsController(QObject):
    def __init__(
        self,
        *,
        view: ControlsComponent,
        config: Config,
    ) -> None:
        super().__init__()

        self._view = view
        self._config = config
        self.setupConnections()
        self.configUpdate()

    def setupConnections(self) -> None:
        self._view.restart_button.clicked.connect(self.restartGame)

    def configUpdate(self) -> None:
        self._view.restart_button.setVisible(self._config.restart_command is not None)

    def restartGame(self) -> None:
        if self._config.restart_command is not None:
            subprocess.run(self._config.restart_command, shell=True)  # noqa: S602 # Shell injection is a feature here
