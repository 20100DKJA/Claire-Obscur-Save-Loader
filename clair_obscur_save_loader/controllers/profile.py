import os.path
import sys
from typing import TYPE_CHECKING

from clair_obscur_save_loader.controllers.controls import ControlsController

if TYPE_CHECKING:
    from collections.abc import Callable

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QStyle

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.config import SaveDoubleClickAction
from clair_obscur_save_loader.controllers.save import SaveItemModel
from clair_obscur_save_loader.controllers.settings import SettingsController
from clair_obscur_save_loader.definitions import Color
from clair_obscur_save_loader.definitions import Messages
from clair_obscur_save_loader.managers.profile import ProfileManager
from clair_obscur_save_loader.managers.save import SaveManager
from clair_obscur_save_loader.views.popup import PopUpComponent
from clair_obscur_save_loader.views.profile import ProfileComponent
from clair_obscur_save_loader.views.save import SaveComponent


class ProfileController(QObject):
    def __init__(
        self,
        *,
        profile_view: ProfileComponent,
        save_view: SaveComponent,
        popup_view: PopUpComponent,
        controls_controller: ControlsController,
        settings_controller: SettingsController,
        config: Config,
        profile_manager: ProfileManager,
        save_manager: SaveManager,
    ) -> None:
        super().__init__()
        self._profile_view = profile_view
        self._save_view = save_view
        self._popup_view = popup_view
        self._controls_controller = controls_controller
        self._settings_controller = settings_controller
        self._config = config
        self._profile_manager = profile_manager
        self._save_manager = save_manager
        try:
            _ = save_manager.active_save_path
        except FileNotFoundError as e:
            self.showMessage(e.args[0], Color.ERROR)
        self.refreshProfiles()
        self.setStartupProfile()
        self.selectProfile()
        self.setupConnections()
        if self._config.expand_all_on_startup:
            self._save_view.expandAll()

    def setupConnections(self) -> None:
        # Connecter les boutons
        self._profile_view.buttons['Create Profile'].clicked.connect(self.createProfile)
        self._profile_view.buttons['Delete Profile'].clicked.connect(self.deleteProfile)
        self._profile_view.buttons['Duplicate Profile'].clicked.connect(self.duplicateProfile)
        self._profile_view.buttons['Rename Profile'].clicked.connect(self.renameProfile)
        self._profile_view.buttons['Settings'].clicked.connect(self.openSettings)
        self._profile_view.currentTextChanged.connect(self.selectProfile)
        self._save_view.import_button.clicked.connect(self.importSave)
        self._save_view.load_button.clicked.connect(self.loadSave)
        self._save_view.replace_button.clicked.connect(self.replaceSave)
        self._save_view.save_double_clicked.connect(self.save_double_clicked)

        # Connecter le menu contextuel
        self._save_view.customContextMenuRequested.connect(self.showContextMenu)

    def setStartupProfile(self) -> None:
        initial = (
            self._config.last_profile
            if self._config.startup_profile is None
            else self._config.startup_profile
        )
        profiles = self._profile_manager.get_list_of_profiles()
        if initial is not None and initial in profiles:
            self._profile_view.setCurrentText(initial)

    def refreshProfiles(self) -> None:
        current = self._profile_view.currentProfile()
        self._profile_view.clear()
        profiles = self._profile_manager.get_list_of_profiles()
        self._profile_view.addItems(profiles)

        # Restaurer la sélection précédente si possible
        if current in profiles:
            self._profile_view.setCurrentText(current)
        else:
            self._profile_view.setCurrentIndex(-1)

    def isProfileSelected(self) -> bool:
        return self._profile_view.currentIndex() != -1

    def selectProfile(self) -> None:
        if self._profile_view.currentProfile():
            model = SaveItemModel(
                self._profile_manager.get_profile_path(self._profile_view.currentProfile())
            )
            self._save_view.change_profile(model)
            self._config.last_profile = self._profile_view.currentProfile()
            self._config.save_config()
        else:
            self._save_view.clear()
        self._save_view.selectionModel().selectionChanged.connect(self.selectSaveItem)
        self.selectSaveItem()

    def createProfile(self) -> None:
        name, ok = QInputDialog.getText(
            self._profile_view,
            'Create Profile',
            'Enter name:',
            text='new Profile',
        )
        if ok and name:
            if name not in self._profile_manager.get_list_of_profiles():
                if '/' in name or '\\' in name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    self._profile_manager.create(name)
                    self._profile_view.addItem(name)
                    self._profile_view.setCurrentText(name)
                    self.selectProfile()
                    self.showMessage(f'{name} has been successfully created')
            else:
                self.showMessage(f'{name} already exists', Color.ERROR)

    def deleteProfile(self) -> None:
        if not self.isProfileSelected():
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        name = self._profile_view.currentProfile()
        if self.confirmAction('Warning!', f'You will delete {name} Profile', 'Are you sure?'):
            self._profile_manager.delete(name)
            self._profile_view.clear()
            self._profile_view.addItems(self._profile_manager.get_list_of_profiles())
            self._profile_view.setCurrentIndex(-1)
            self._save_view.clear()
            self.showMessage(f'{name} has been successfully deleted')

    def renameProfile(self) -> None:
        if not self.isProfileSelected():
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        old_name = self._profile_view.currentProfile()
        new_name, ok = QInputDialog.getText(
            self._profile_view, 'Rename Profile', 'Enter new name:', text=old_name
        )
        if ok and new_name:
            if new_name not in self._profile_manager.get_list_of_profiles():
                if '/' in new_name or '\\' in new_name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    self._profile_manager.rename(old_name, new_name)
                    self._profile_view.setItemText(self._profile_view.currentIndex(), new_name)
                    self.showMessage('Profile has been renamed')
            else:
                self.showMessage(f'{new_name} already exists', Color.ERROR)

    def duplicateProfile(self) -> None:
        if not self.isProfileSelected():
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        old_name = self._profile_view.currentProfile()
        new_name, ok = QInputDialog.getText(
            self._profile_view,
            'Duplicate Profile',
            'Enter name:',
            text=old_name,
        )
        if ok and new_name:
            if new_name not in self._profile_manager.get_list_of_profiles():
                if '/' in new_name or '\\' in new_name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    self._profile_manager.duplicate(old_name, new_name)
                    self._profile_view.addItem(new_name)
                    self._profile_view.setCurrentText(new_name)
                    self.selectProfile()
                    self.showMessage(f'{old_name} has been duplicated as: {new_name}')
            else:
                self.showMessage(f'{new_name} already exists', Color.ERROR)

    def showMessage(self, text: str, color: Color = Color.INFO) -> None:
        self._popup_view.setStyleSheet(f'color: {color};')
        self._popup_view.setText(text)

    def confirmAction(self, title: str, text: str, informative_text: str) -> bool:
        msg = QMessageBox(self._profile_view)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        no_button = msg.addButton(QMessageBox.No)
        no_button.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DialogCancelButton))
        )
        yes_button = msg.addButton(QMessageBox.Yes)
        yes_button.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DialogOkButton))
        )
        msg.setEscapeButton(no_button)
        msg.exec_()
        return msg.clickedButton() == yes_button

    def selectSaveItem(self) -> None:
        _, _, is_save_data, _ = self._save_view.selected_save_data()
        self._save_view.load_button.setEnabled(is_save_data)
        self._save_view.replace_button.setEnabled(is_save_data)

        return None

    def importSave(self) -> None:
        profile = self._profile_view.currentProfile()
        parent_path, _, _, _ = self._save_view.selected_save_data()
        model = self._save_view.current_save_model()
        if not profile or parent_path is None or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        name, ok = QInputDialog.getText(
            self._save_view, 'Import Savestate', 'Enter name:', text='new save'
        )
        if not ok or not name:
            return
        if '/' in name or '\\' in name:
            self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
            return
        try:
            self._save_manager.import_save(name, profile, parent_path, False)
            model.refresh_path(parent_path)
            self.showMessage(f'{name} has been successfully imported')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def loadSave(self) -> None:
        profile = self._profile_view.currentProfile()
        if profile is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        _, item_path, is_save_dir, _ = self._save_view.selected_save_data()
        if item_path is None or not is_save_dir:
            self.showMessage('Select a save to load', Color.ERROR)
            return
        try:
            self._save_manager.load_save(profile, item_path)
            self.showMessage(f'{os.path.basename(item_path)} has been successfully loaded')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def duplicateSaveData(self, parent_path: str, item_path: str) -> None:
        profile = self._profile_view.currentProfile()
        model = self._save_view.current_save_model()
        if not profile or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        old_name = os.path.basename(item_path)
        new_name, ok = QInputDialog.getText(
            self._save_view, 'Duplicate Savestate', 'Enter name:', text=old_name
        )
        if not ok or not new_name:
            return
        if '/' in new_name or '\\' in new_name:
            self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
            return
        try:
            self._save_manager.duplicate_save(old_name, new_name, profile, parent_path)
            model.refresh_path(parent_path)
            self.showMessage(f'{old_name} successfully duplicated')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def removeSaveData(self, parent_path: str, item_path: str) -> None:
        profile = self._profile_view.currentProfile()
        model = self._save_view.current_save_model()
        if not profile or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        item_name = os.path.basename(item_path)
        if not self.confirmAction('Warning!', f'You will delete {item_name}', 'Are you sure?'):
            return
        try:
            self._save_manager.remove_save(item_path, profile, parent_path)
            model.refresh_path(parent_path)
            self.showMessage(f'{item_name} has been removed')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def renameSaveData(self, parent_path: str, item_path: str) -> None:
        profile = self._profile_view.currentProfile()
        model = self._save_view.current_save_model()
        if not profile or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        old_name = os.path.basename(item_path)
        new_name, ok = QInputDialog.getText(
            self._save_view, 'Rename Savestate', 'Enter new name:', text=old_name
        )
        if not ok or not new_name:
            return
        if '/' in new_name or '\\' in new_name:
            self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
            return
        try:
            self._save_manager.rename_save(old_name, new_name, profile, parent_path)
            model.refresh_path(parent_path)
            self.showMessage(f'{new_name} successfully renamed')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def replaceSave(self) -> None:
        parent_path, item_path, is_save_dir, _ = self._save_view.selected_save_data()
        self.replaceSaveData(parent_path, item_path, is_save_dir)

    def replaceSaveData(
        self, parent_path: str | None, item_path: str | None, is_save_dir: bool
    ) -> None:
        profile = self._profile_view.currentProfile()
        model = self._save_view.current_save_model()
        if not profile or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        if parent_path is None or item_path is None or not is_save_dir:
            self.showMessage('Select a savestate to be updated', Color.ERROR)
            return
        item_name = os.path.basename(item_path)
        if not self.confirmAction('Warning!', f'You will replace {item_name}', 'Are you sure?'):
            return

        try:
            self._save_manager.import_save(item_name, profile, parent_path, True)
            self.showMessage(f'{item_name} has been successfully replaced')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def refresh_folder(self, item_path: str) -> None:
        model = self._save_view.current_save_model()
        if model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        model.refresh_path(item_path)

    def new_folder(self, parent_path: str) -> None:
        profile = self._profile_view.currentProfile()
        model = self._save_view.current_save_model()
        if not profile or model is None:
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        name, ok = QInputDialog.getText(
            self._save_view, 'New Folder', 'Enter folder name:', text='new folder'
        )
        if not ok or not name:
            return
        if '/' in name or '\\' in name:
            self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
            return
        try:
            self._save_manager.new_folder(name, profile, parent_path)
            model.refresh_path(parent_path)
            self.showMessage(f'{name} successfully created')
        except ValueError as e:
            self.showMessage(e.args[0], Color.ERROR)
            return

    def showContextMenu(self, position: QPoint) -> None:
        if self._save_view.current_save_model() is None:
            return

        def open_folder(folder: str) -> None:
            if sys.platform == 'win32':
                import os

                os.startfile(folder)  # noqa: S606
            elif sys.platform == 'darwin':
                import subprocess  # noqa: S404

                subprocess.call(['open', folder])  # noqa: S603, S607
            elif sys.platform == 'linux':
                import subprocess  # noqa: S404

                subprocess.call(['xdg-open', folder])  # noqa: S603, S607

        parent_path, item_path, is_save_dir, is_root = self._save_view.save_data_at(position)
        if not self.isProfileSelected() or parent_path is None or item_path is None:
            return
        menu = QMenu()
        method: Callable[[], None]
        if is_save_dir:
            options = [
                ('Rename', lambda: self.renameSaveData(parent_path, item_path)),
                ('Duplicate', lambda: self.duplicateSaveData(parent_path, item_path)),
                ('Delete', lambda: self.removeSaveData(parent_path, item_path)),
                ('Replace', lambda: self.replaceSaveData(parent_path, item_path, is_save_dir)),
                ('Open Folder Path', lambda: open_folder(parent_path)),
            ]
        elif is_root:
            options = [
                ('New Folder', lambda: self.new_folder(parent_path)),
                ('Refresh Folder', lambda: self.refresh_folder(item_path)),
                ('Open Folder Path', lambda: open_folder(parent_path)),
                ('Expand All', self._save_view.expandAll),
                ('Collapse All', self._save_view.collapseAll),
            ]
        else:
            options = [
                ('New Folder', lambda: self.new_folder(parent_path)),
                ('Refresh Folder', lambda: self.refresh_folder(item_path)),
                ('Open Folder Path', lambda: open_folder(parent_path)),
                ('Rename', lambda: self.renameSaveData(os.path.dirname(item_path), item_path)),
                (
                    'Duplicate',
                    lambda: self.duplicateSaveData(os.path.dirname(item_path), item_path),
                ),
                ('Delete', lambda: self.removeSaveData(os.path.dirname(parent_path), item_path)),
            ]
        for action_name, method in options:
            action = QAction(action_name, self._save_view.root)
            action.triggered.connect(method)
            menu.addAction(action)

        menu.exec_(self._save_view.viewport().mapToGlobal(position))

    def openSettings(self) -> None:
        self._settings_controller.show()

    def save_double_clicked(self) -> None:
        mode = self._config.save_double_click_action
        mode = mode if mode is not None else SaveDoubleClickAction.LOAD_SAVE
        if (
            mode == SaveDoubleClickAction.LOAD_SAVE
            or mode == SaveDoubleClickAction.LOAD_SAVE_AND_RESTART_GAME
        ):
            self.loadSave()
        if mode == SaveDoubleClickAction.LOAD_SAVE_AND_RESTART_GAME:
            self._controls_controller.restartGame()
