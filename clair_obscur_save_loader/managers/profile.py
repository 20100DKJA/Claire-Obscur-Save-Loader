import os
import shutil
import stat
from typing import cast

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.definitions import PROFILES_FOLDER_NAME


class ProfileManager:
    def __init__(self) -> None:
        self.config = Config()
        if not self.config.is_configured():
            raise ValueError('Configuration is not set up')

    def create(self, name: str) -> bool:
        if name == '':
            raise ValueError("Name can't be empty")

        new_profile_path = os.path.join(cast('str', self.profiles_save_path), name)
        if os.path.exists(new_profile_path):
            raise FileExistsError('Profile already exists')
        os.makedirs(new_profile_path, exist_ok=True)
        return True

    def delete(self, name: str) -> bool:
        removed_profile_path = os.path.join(cast('str', self.profiles_save_path), name)
        for root, dirs, _ in os.walk(removed_profile_path):
            os.chmod(root, stat.S_IWUSR)
            for d in dirs:
                if d == 'Backup':
                    continue
                dirs_path: str = os.path.join(removed_profile_path, d)
                for folder_and_file in os.listdir(dirs_path):
                    if folder_and_file == 'Backup':
                        os.chmod(os.path.join(dirs_path, folder_and_file), stat.S_IWUSR)
                os.chmod(dirs_path, stat.S_IWUSR)
        shutil.rmtree(removed_profile_path)
        return True

    def duplicate(self, name: str, name_of_copy: str) -> None:
        profile_path = os.path.join(cast('str', self.profiles_save_path), name)
        copy_path = os.path.join(cast('str', self.profiles_save_path), name_of_copy)
        shutil.copytree(profile_path, copy_path, dirs_exist_ok=True)

    def rename(self, name: str, new_name: str) -> None:
        old_profile_path = os.path.join(cast('str', self.profiles_save_path), name)
        new_profile_path = os.path.join(cast('str', self.profiles_save_path), new_name)
        os.rename(old_profile_path, new_profile_path)

    def get_list_of_profiles(self) -> list[str]:
        return os.listdir(cast('str', self.profiles_save_path))

    def get_list_of_saves(self, profile: str) -> list[str]:
        return os.listdir(os.path.join(cast('str', self.profiles_save_path), profile))

    @property
    def profiles_save_path(self) -> str | None:
        if not self.config.is_configured():
            return None

        profile_path = os.path.join(cast('str', self.config.save_location), PROFILES_FOLDER_NAME)
        if not os.path.exists(profile_path):
            os.makedirs(profile_path, exist_ok=True)

        return profile_path
