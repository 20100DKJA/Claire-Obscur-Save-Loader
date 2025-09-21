from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.config import SaveDoubleClickAction
from clair_obscur_save_loader.managers import ProfileManager
from clair_obscur_save_loader.views.settings import SettingsWindow


class SettingsController(QObject):
    saved = pyqtSignal()

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
        self._view.restart_command_choice.currentIndexChanged.connect(self.updateRestartCommand)

    def loadSettings(self) -> None:
        self._view.startup_profile.clear()
        self._view.startup_profile.addItem('<last selected profile>')
        self._view.startup_profile.addItems(self._profile_manager.get_list_of_profiles())
        if self._config.startup_profile is None:
            self._view.startup_profile.setCurrentIndex(0)
        else:
            self._view.startup_profile.setCurrentText(self._config.startup_profile)

        self._view.expand_all_on_startup.setChecked(bool(self._config.expand_all_on_startup))

        if self._config.save_double_click_action is None:
            self._view.double_click_action.setCurrentIndex(
                self._view.double_click_action.findData(SaveDoubleClickAction.LOAD_SAVE)
            )
        else:
            self._view.double_click_action.setCurrentIndex(
                self._view.double_click_action.findData(
                    SaveDoubleClickAction(self._config.save_double_click_action)
                )
            )

        idx = 0
        if self._config.restart_command is not None:
            idx = self._view.restart_command_choice.findData(self._config.restart_command)
        if idx < 0:
            self._view.restart_command_choice.setCurrentIndex(
                self._view.restart_command_choice.findText('Custom Command')
            )
        else:
            self._view.restart_command_choice.setCurrentIndex(idx)
        self.updateRestartCommand()
        if idx < 0:
            self._view.restart_command.setText(self._config.restart_command)

    def saveSettings(self) -> None:
        self._config.startup_profile = (
            None
            if self._view.startup_profile.currentIndex() < 1
            else self._view.startup_profile.currentText()
        )
        self._config.expand_all_on_startup = self._view.expand_all_on_startup.isChecked()
        self._config.save_double_click_action = self._view.double_click_action.currentData()
        self._config.restart_command = (
            None
            if self._view.restart_command_choice.currentIndex() < 1
            or self._view.restart_command.text() == ''
            else self._view.restart_command.text()
        )
        self._config.save_config()
        self.saved.emit()

    def updateRestartCommand(self) -> None:
        self._view.restart_command.setText('')

        if self._view.restart_command_choice.currentIndex() == 0:
            self._view.restart_command.setVisible(False)
            return

        self._view.restart_command.setVisible(True)
        choice = self._view.restart_command_choice.currentData()
        if choice == '':
            self._view.restart_command.setDisabled(False)
        else:
            self._view.restart_command.setDisabled(True)
            self._view.restart_command.setText(choice)
        self._view.restart_command.setCursorPosition(0)

    def save(self) -> None:
        self.saveSettings()
        self._view.hide()

    def cancel(self) -> None:
        self._view.hide()

    def show(self) -> None:
        self.loadSettings()
        self._view.show()
