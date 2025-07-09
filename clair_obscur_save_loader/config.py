import json
import os
from functools import cache
from typing import Any

from clair_obscur_save_loader.definitions import CONFIG_FILE_NAME
from clair_obscur_save_loader.definitions import CONFIG_LOCATION


@cache
class Config:
    def _load_config(self) -> None:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    loaded_config: dict[str, Any] = json.load(f)
                    for key, value in loaded_config.items():
                        setattr(self, key, value)
        except Exception as e:
            raise ValueError(f'Error when loading configuration: {e}') from e

    def __init__(self) -> None:
        # Use the config location from definitions
        self.config_file = os.path.join(CONFIG_LOCATION, CONFIG_FILE_NAME)
        self.save_location: str | None = self.DEFAULT_SAVE_LOCATION

        self._load_config()

    @property
    def DEFAULT_SAVE_LOCATION(self) -> str | None:
        # Define folder base on classic installation(Windows / Steam)
        if os.getenv('LOCALAPPDATA') and os.path.exists(
            os.path.join(os.environ['LOCALAPPDATA'], 'Sandfall')
        ):
            return os.path.join(os.environ['LOCALAPPDATA'], 'Sandfall', 'Saved', 'SaveGames')
        # In others cases, it's not determinable
        return None

    def _save_config(self) -> None:
        if not os.path.exists(CONFIG_LOCATION):
            os.makedirs(CONFIG_LOCATION)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(
                    {
                        'save_location': self.save_location,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            raise ValueError(f'Error when saving configuration: {e}') from e

    def is_configured(self) -> bool:
        return self.save_location is not None and os.path.exists(self.save_location or '')
