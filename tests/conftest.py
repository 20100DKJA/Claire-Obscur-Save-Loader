import json
import os
import sys
import tempfile
from collections.abc import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.definitions import PROFILES_FOLDER_NAME
from clair_obscur_save_loader.managers import MainManager
from clair_obscur_save_loader.managers.profile import ProfileManager
from clair_obscur_save_loader.managers.save import SaveManager


@pytest.fixture(scope='session')
def qapp() -> QApplication:
    """Fixture qui fournit une QApplication pour toute la session de test"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_profiles_dir() -> Iterator[str]:
    """Crée un répertoire temporaire avec des profils de test"""
    with tempfile.TemporaryDirectory() as temp_dir:
        profiles_dir = os.path.join(temp_dir, PROFILES_FOLDER_NAME)

        os.makedirs(os.path.join(profiles_dir, 'default', 'save1'))
        os.makedirs(os.path.join(profiles_dir, 'default', 'save2'))
        os.makedirs(os.path.join(profiles_dir, 'other', 'save1'))
        os.makedirs(os.path.join(profiles_dir, 'empty'))

        yield temp_dir


@pytest.fixture
def profile_manager(mock_profiles_dir: str) -> Iterator[ProfileManager]:
    """Crée un ProfileManager configuré pour utiliser le répertoire de test"""
    with patch.object(Config(), 'save_location', mock_profiles_dir):
        manager = ProfileManager()

        yield manager


@pytest.fixture
def save_manager(profile_manager: ProfileManager) -> Iterator[SaveManager]:
    """Crée un SaveManager configuré pour utiliser le répertoire de test"""
    manager = SaveManager(profile_manager=profile_manager)
    return manager


@pytest.fixture
def mock_manager() -> MainManager:
    """Crée un mock du manager principal"""
    manager = MagicMock(spec=MainManager)
    return manager


@pytest.fixture
def mock_config_file() -> Iterator[str]:
    """Crée un fichier de configuration temporaire pour les tests"""
    test_config = {'save_location': '/path/to/test/saves'}
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json.dump(test_config, f)
        temp_path = f.name

    yield temp_path

    # Nettoyage
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def config(mock_config_file: str) -> Config:
    config = Config()
    config.save_location = None
    config.config_file = mock_config_file
    return config
