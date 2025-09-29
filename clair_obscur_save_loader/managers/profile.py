import os
import shutil
import stat
from typing import cast

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.definitions import PROFILES_FOLDER_NAME


class ProfileManager:
    def __init__(self) -> None:
        self.config = Config()

    def create(self, name: str) -> bool:
        if name == '':
            raise ValueError("Name can't be empty")

        new_profile_path = os.path.join(self.profiles_save_path, name)
        if os.path.exists(new_profile_path):
            raise FileExistsError('Profile already exists')
        os.makedirs(new_profile_path, exist_ok=True)
        return True

    def delete(self, name: str) -> bool:
        removed_profile_path = os.path.join(self.profiles_save_path, name)
        for root, _, _ in os.walk(removed_profile_path):
            os.chmod(root, stat.S_IRWXU)
        shutil.rmtree(removed_profile_path)
        return True

    def duplicate(self, name: str, name_of_copy: str) -> None:
        profile_path = os.path.join(self.profiles_save_path, name)
        copy_path = os.path.join(self.profiles_save_path, name_of_copy)
        shutil.copytree(profile_path, copy_path, dirs_exist_ok=True)

    def rename(self, name: str, new_name: str) -> None:
        old_profile_path = os.path.join(self.profiles_save_path, name)
        new_profile_path = os.path.join(self.profiles_save_path, new_name)
        os.rename(old_profile_path, new_profile_path)

    def get_list_of_profiles(self) -> list[str]:
        return os.listdir(self.profiles_save_path)

    def get_profile_path(self, profile: str) -> str:
        return os.path.join(self.profiles_save_path, profile)

    @property
    def profiles_save_path(self) -> str:
        if not self.config.is_configured():
            raise ValueError('Configuration is not set up')

        profile_path = os.path.join(cast('str', self.config.save_location), PROFILES_FOLDER_NAME)
        if not os.path.exists(profile_path):
            os.makedirs(profile_path, exist_ok=True)

        return profile_path
