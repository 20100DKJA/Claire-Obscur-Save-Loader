import sys
from typing import TYPE_CHECKING
from typing import cast

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox

from clair_obscur_save_loader.definitions import Color
from clair_obscur_save_loader.definitions import Messages
from clair_obscur_save_loader.managers.profile import ProfileManager
from clair_obscur_save_loader.managers.save import SaveManager
from clair_obscur_save_loader.views.popup import PopUpComponent
from clair_obscur_save_loader.views.profile import ProfileComponent
from clair_obscur_save_loader.views.save import SaveComponent

if TYPE_CHECKING:
    from collections.abc import Callable


class ProfileController(QObject):
    def __init__(
        self,
        *,
        profile_view: ProfileComponent,
        save_view: SaveComponent,
        popup_view: PopUpComponent,
        profile_manager: ProfileManager,
        save_manager: SaveManager,
    ) -> None:
        super().__init__()
        self._profile_view = profile_view
        self._save_view = save_view
        self._popup_view = popup_view
        self._profile_manager = profile_manager
        self._save_manager = save_manager
        self.refreshProfiles()
        self.setupConnections()

    def setupConnections(self) -> None:
        # Connecter les boutons
        self._profile_view.buttons['Create Profile'].clicked.connect(self.createProfile)
        self._profile_view.buttons['Delete Profile'].clicked.connect(self.deleteProfile)
        self._profile_view.buttons['Duplicate Profile'].clicked.connect(self.duplicateProfile)
        self._profile_view.buttons['Rename Profile'].clicked.connect(self.renameProfile)
        self._profile_view.currentTextChanged.connect(self.selectProfile)
        self._save_view.import_button.clicked.connect(self.importSave)
        self._save_view.load_button.clicked.connect(self.loadSave)

        # Connecter le menu contextuel
        self._save_view.customContextMenuRequested.connect(self.showContextMenu)

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

    # def updateSaveList(self, profile_name: str):
    #     self._view.listwidget.clear()
    #     if profile_name:
    #         saves = self._manager.get_saves(profile_name)
    #         self._view.listwidget.addItems(saves)

    def isProfileSelected(self) -> bool:
        return self._profile_view.currentIndex() != -1

    def selectProfile(self) -> None:
        if self._profile_view.currentProfile():
            self._save_view.clear()
            self._save_view.addItems(
                self._profile_manager.get_list_of_saves(self._profile_view.currentProfile())
            )

    def createProfile(self, name: str) -> None:
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
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_() == QMessageBox.Yes

    def loadSave(self) -> None:
        item = self._save_view.currentItem()
        if item:
            if self._save_manager.load_save(item.text(), self._profile_view.currentProfile()):
                self._save_view.setCurrentItem(item)
                self.showMessage(f'{item.text()} has been successfully loaded')
            else:
                self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
        else:
            self.showMessage('Select a save to load', Color.ERROR)

    def importSave(self) -> None:
        if not self._profile_view.currentProfile():
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        name, ok = QInputDialog.getText(
            self._save_view, 'Import Savestate', 'Enter name:', text='new save'
        )
        if ok and name:
            if name not in self._profile_manager.get_list_of_saves(
                self._profile_view.currentProfile()
            ):
                if '/' in name or '\\' in name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    if self._save_manager.import_save(name, self._profile_view.currentProfile()):
                        self._save_view.clear()
                        self._save_view.addItems(
                            self._profile_manager.get_list_of_saves(
                                self._profile_view.currentProfile()
                            )
                        )
                        self.showMessage(f'{name} has been successfully imported')
                    else:
                        self.showMessage('Failed to import save', Color.ERROR)
            else:
                self.showMessage(Messages.SAVESTATE_EXIST, Color.ERROR)

    def duplicateSave(self) -> None:
        if not self._profile_view.currentProfile():
            self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
            return
        old_name = cast('QListWidgetItem', self._save_view.currentItem()).text()
        new_name, ok = QInputDialog.getText(
            self._save_view, 'Duplicate Savestate', 'Enter name:', text=old_name
        )
        if ok and new_name:
            if new_name not in self._profile_manager.get_list_of_saves(
                self._profile_view.currentProfile()
            ):
                if '/' in new_name or '\\' in new_name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    if self._save_manager.duplicate_save(
                        old_name, new_name, self._profile_view.currentProfile()
                    ):
                        self._save_view.clear()
                        self._save_view.addItems(
                            self._profile_manager.get_list_of_saves(
                                self._profile_view.currentProfile()
                            )
                        )
                        self.showMessage(f'{old_name} has been duplicated as: {new_name}')
            else:
                self.showMessage(Messages.SAVESTATE_EXIST, Color.ERROR)

    def removeSave(self) -> None:
        item = self._save_view.currentItem()
        if item:
            if self.confirmAction('Warning!', f'You will delete {item.text()}', 'Are you sure?'):
                if self._save_manager.remove_save(item.text(), self._profile_view.currentProfile()):
                    self._save_view.takeItem(self._save_view.row(item))
                    self.showMessage(f'{item.text()} has been removed')
                else:
                    self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
        else:
            self.showMessage('Select a save to remove', Color.ERROR)

    def renameSave(self, item: QListWidgetItem) -> None:
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self._save_view, 'Rename Savestate', 'Enter new name:', text=old_name
        )
        if ok and new_name:
            if new_name not in self._profile_manager.get_list_of_saves(
                self._profile_view.currentProfile()
            ):
                if '/' in new_name or '\\' in new_name:
                    self.showMessage(Messages.INVALID_CARACTER, Color.ERROR)
                else:
                    if self._save_manager.rename_save(
                        old_name, new_name, self._profile_view.currentProfile()
                    ):
                        item.setText(new_name)
                        self.showMessage('Savestate has been renamed')
            else:
                self.showMessage(Messages.SAVESTATE_EXIST, Color.ERROR)

    def updateSave(self) -> None:
        item = self._save_view.currentItem()
        if item:
            if self.confirmAction('Warning!', f'You will replace {item.text()}', 'Are you sure?'):
                if self._save_manager.import_save(item.text(), self._profile_view.currentProfile()):
                    self.showMessage(f'{item.text()} has been updated')
                else:
                    self.showMessage(Messages.SELECT_PROFILE, Color.ERROR)
        else:
            self.showMessage('Select a savestate to be updated', Color.ERROR)

    def showContextMenu(self, position: QPoint) -> None:
        def open_folder() -> None:
            folder = self._save_manager.get_save_path(self._profile_view.currentProfile())
            if sys.platform == 'win32':
                import os

                os.startfile(folder)  # noqa: S606
            elif sys.platform == 'darwin':
                import subprocess  # noqa: S404

                subprocess.call(['open', folder])  # noqa: S603, S607
            elif sys.platform == 'linux':
                import subprocess  # noqa: S404

                subprocess.call(['xdg-open', folder])  # noqa: S603, S607

        item = self._save_view.itemAt(position)
        if not self.isProfileSelected() or not item:
            return
        menu = QMenu()
        method: Callable[[], None]
        for action_name, method in [
            ('Rename', lambda: self.renameSave(item)),
            ('Duplicate', self.duplicateSave),
            ('Replace', self.updateSave),
            ('Delete', self.removeSave),
            ('Open Folder Path', open_folder),
        ]:
            action = QAction(action_name, self._save_view.root)
            action.triggered.connect(method)
            menu.addAction(action)

        menu.exec_(self._save_view.viewport().mapToGlobal(position))
