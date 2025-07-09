import os
from typing import cast

from clair_obscur_save_loader.config import Config


class MainManager:
    def __init__(self) -> None:
        self.config = Config()
        self._current_save_path: str | None = None

    @property
    def is_configured(self) -> bool:
        return self.config.is_configured()

    @property
    def current_save_path(self) -> str | None:
        if not self.is_configured:
            return None

        if self._current_save_path is None:
            save_location = cast('str', self.config.save_location)

            # Recherche du dossier numérique pour les sauvegardes actives
            for save_folder in os.listdir(save_location):
                if save_folder.isdigit():
                    self._current_save_path = os.path.join(save_location, save_folder)
                    break

        return self._current_save_path

    def set_save_location(self, location: str) -> bool:
        if not os.path.exists(location):
            return False

        has_numeric_folder = any(
            folder.isdigit()
            for folder in os.listdir(location)
            if os.path.isdir(os.path.join(location, folder))
        )

        if not has_numeric_folder:
            return False

        self.config.save_location = location

        self.reset_paths()

        return True

    def save_config(self) -> None:
        self.config._save_config()

    def reset_paths(self) -> None:
        self._current_save_path = None
