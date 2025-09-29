import os
import shutil
import stat
from contextlib import suppress

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.definitions import Messages
from clair_obscur_save_loader.managers.profile import ProfileManager


def looks_like_save_path(location: str) -> bool:
    return os.path.exists(location) and os.path.exists(os.path.join(location, 'SavesContainer.sav'))


def looks_like_active_save_path(location: str) -> bool:
    return looks_like_save_path(location) and os.path.basename(location).isdigit()


def find_active_save_path(location: str) -> str | None:
    if not os.path.exists(location):
        return None

    for folder_name in sorted(os.listdir(location)):
        folder_path = os.path.join(location, folder_name)
        if os.path.isdir(folder_path) and looks_like_active_save_path(folder_path):
            return folder_path

    return None


class SaveManager:
    def __init__(self, *, profile_manager: ProfileManager) -> None:
        self.config = Config()
        self.config.is_configured()
        self.profile_manager = profile_manager

    def get_save_path(self, profile: str) -> str:
        return os.path.join(self.profile_manager.profiles_save_path, profile)

    @property
    def active_save_path(self) -> str:
        folder = (
            find_active_save_path(self.config.save_location)
            if self.config.save_location is not None
            else None
        )
        if folder is None:
            raise FileNotFoundError('No active save folder found, please check your configuration.')
        return folder

    def import_save(self, name: str, profile: str, parent_path: str, replace: bool) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        new_save_path = os.path.join(parent_path, name)
        if not new_save_path.startswith(
            os.path.join(self.profile_manager.profiles_save_path, profile)
        ):
            raise ValueError('Importing outside of profile directory')
        if os.path.exists(new_save_path):
            if not replace:
                raise ValueError(Messages.SAVESTATE_EXIST)
            for root, _, _ in os.walk(new_save_path):
                os.chmod(root, stat.S_IRWXU)
            shutil.rmtree(new_save_path)
        elif replace:
            raise ValueError('Savestate does not exist')
        try:
            shutil.copytree(self.active_save_path, new_save_path, dirs_exist_ok=True)
        except Exception as e:
            raise ValueError('Failed to import save') from e

    def duplicate_save(self, old_name: str, new_name: str, profile: str, parent_path: str) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        old_save_path = os.path.join(parent_path, old_name)
        new_save_path = os.path.join(parent_path, new_name)
        if os.path.exists(new_save_path):
            raise ValueError(Messages.SAVESTATE_EXIST)
        try:
            shutil.copytree(old_save_path, new_save_path, dirs_exist_ok=True)
        except Exception as e:
            raise ValueError('Failed to duplicate save') from e

    def remove_save(self, item_path: str, profile: str, parent_path: str) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        if not item_path.startswith(os.path.join(self.profile_manager.profiles_save_path, profile)):
            raise ValueError('Deleting outside of profile directory')
        if not os.path.exists(item_path):
            raise ValueError('Savestate does not exist')
        try:
            for root, _, _ in os.walk(item_path):
                os.chmod(root, stat.S_IRWXU)
            shutil.rmtree(item_path)
        except Exception as e:
            raise ValueError('Failed to remove save') from e

    def rename_save(self, old_name: str, new_name: str, profile: str, parent_path: str) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        old_save_path = os.path.join(parent_path, old_name)
        new_save_path = os.path.join(parent_path, new_name)
        if os.path.exists(new_save_path):
            raise ValueError(Messages.SAVESTATE_EXIST)
        try:
            os.rename(old_save_path, new_save_path)
        except Exception as e:
            raise ValueError('Failed to rename save') from e

    def load_save(self, profile: str, item_path: str) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        if not item_path.startswith(os.path.join(self.profile_manager.profiles_save_path, profile)):
            raise ValueError('Loading outside of profile directory')
        try:
            dst = self.active_save_path
            with suppress(OSError):
                for root, _, _ in os.walk(dst):
                    os.chmod(root, stat.S_IRWXU)
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(item_path, dst, dirs_exist_ok=True)
        except Exception as e:
            raise ValueError('Failed to load savestate') from e

    def new_folder(self, name: str, profile: str, parent_path: str) -> None:
        if profile == '':
            raise ValueError("Profile can't be empty")
        new_path = os.path.join(parent_path, name)
        if os.path.exists(new_path):
            raise ValueError(Messages.SAVESTATE_EXIST)
        try:
            os.mkdir(new_path)
        except Exception as e:
            raise ValueError('Failed to create folder') from e
