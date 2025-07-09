import os
import shutil
import stat
from typing import cast

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.managers.profile import ProfileManager


class SaveManager:
    def __init__(self, *, profile_manager: ProfileManager) -> None:
        self.config = Config()
        self.config.is_configured()
        self.profile_manager = profile_manager

    def get_save_path(self, profile: str) -> str:
        return os.path.join(cast('str', self.profile_manager.profiles_save_path), profile)

    @property
    def active_save_path(self) -> str:
        for folder in os.listdir(self.config.save_location):
            if folder.isdigit():
                return os.path.join(cast('str', self.config.save_location), folder)
        raise FileNotFoundError('No active save folder found, please check your configuration.')

    def import_save(self, name: str, profile: str) -> bool:
        if profile == '':
            raise ValueError("Profile can't be empty")
        new_save_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, name
        )
        if os.path.exists(new_save_path):
            os.chmod(new_save_path, stat.S_IWUSR)
            shutil.rmtree(new_save_path)
        shutil.copytree(self.active_save_path, new_save_path, dirs_exist_ok=True)
        return True

    def duplicate_save(self, name: str, name_of_copy: str, profile: str) -> bool:
        if profile == '':
            raise ValueError("Profile can't be empty")
        old_save_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, name
        )
        new_save_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, name_of_copy
        )
        if os.path.exists(new_save_path):
            os.chmod(new_save_path, stat.S_IWUSR)
            shutil.rmtree(new_save_path)
        shutil.copytree(old_save_path, new_save_path, dirs_exist_ok=True)
        return True

    def remove_save(self, name: str, profile: str) -> bool:
        if profile == '':
            raise ValueError("Profile can't be empty")
        removed_save_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, name
        )
        os.chmod(removed_save_path, stat.S_IWUSR)
        shutil.rmtree(removed_save_path)
        return True

    def rename_save(self, old_name: str, new_name: str, profile: str) -> bool:
        if profile == '':
            raise ValueError("Profile can't be empty")
        old_name_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, old_name
        )
        new_name_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, new_name
        )
        os.rename(old_name_path, new_name_path)
        return True

    def load_save(self, name: str, profile: str) -> bool:
        if profile == '':
            raise ValueError("Profile can't be empty")

        loaded_save_path = os.path.join(
            cast('str', self.profile_manager.profiles_save_path), profile, name
        )

        if os.path.exists(self.active_save_path):
            for file in os.listdir(self.active_save_path):
                item_path = os.path.join(self.active_save_path, file)
                if file == 'Backup':
                    for subfile in os.listdir(item_path):
                        os.remove(os.path.join(item_path, subfile))
                else:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

        try:
            shutil.copytree(loaded_save_path, self.active_save_path, dirs_exist_ok=True)
        except Exception:
            return False

        return True
