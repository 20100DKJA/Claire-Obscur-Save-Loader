import json
import os
from enum import StrEnum
from functools import cache
from typing import Any

from clair_obscur_save_loader.definitions import CONFIG_FILE_NAME
from clair_obscur_save_loader.definitions import CONFIG_LOCATION


class SaveDoubleClickAction(StrEnum):
    DO_NOTHING = 'DO_NOTHING'
    LOAD_SAVE = 'LOAD_SAVE'
    LOAD_SAVE_AND_RESTART_GAME = 'LOAD_SAVE_AND_RESTART_GAME'


@cache
class Config:
    def _load_config(self) -> None:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    loaded_config: dict[str, Any] = json.load(f)
                    for key, value in loaded_config.items():
                        if key == 'save_double_click_action' and value is not None:
                            value = SaveDoubleClickAction(value)
                        setattr(self, key, value)
        except Exception as e:
            raise ValueError(f'Error when loading configuration: {e}') from e

    def __init__(self) -> None:
        # Use the config location from definitions
        self.config_file = os.path.join(CONFIG_LOCATION, CONFIG_FILE_NAME)
        self.save_location: str | None = self.DEFAULT_SAVE_LOCATION
        self.last_profile: str | None = None
        self.startup_profile: str | None = None
        self.expand_all_on_startup: bool | None = None
        self.save_double_click_action: SaveDoubleClickAction | None = None
        self.restart_command: str | None = None
        self.geometry: str | None = None

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

    def save_config(self) -> None:
        if not os.path.exists(CONFIG_LOCATION):
            os.makedirs(CONFIG_LOCATION)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(
                    {
                        'save_location': self.save_location,
                        'last_profile': self.last_profile,
                        'startup_profile': self.startup_profile,
                        'expand_all_on_startup': self.expand_all_on_startup,
                        'save_double_click_action': self.save_double_click_action,
                        'restart_command': self.restart_command,
                        'geometry': self.geometry,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            raise ValueError(f'Error when saving configuration: {e}') from e

    def is_configured(self) -> bool:
        return self.save_location is not None and os.path.exists(self.save_location or '')
