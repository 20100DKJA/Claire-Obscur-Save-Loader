import os
from unittest.mock import patch

import pytest

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.definitions import PROFILES_FOLDER_NAME
from clair_obscur_save_loader.managers.save import SaveManager


class TestSaveManager:
    def test_get_saves_list(self, save_manager: SaveManager) -> None:
        """Teste la récupération de la liste des sauvegardes"""
        saves = save_manager.profile_manager.get_list_of_saves('default')

        # Vérifier le contenu de la liste
        assert len(saves) == 2
        assert 'save1' in saves
        assert 'save2' in saves

    def test_load_save(self, save_manager: SaveManager) -> None:
        """Teste le chargement d'une sauvegarde"""
        with pytest.raises(
            FileNotFoundError, match='No active save folder found, please check your configuration.'
        ):
            save_manager.load_save('save1', 'other')

    def test_import_save(self, save_manager: SaveManager, mock_profiles_dir: str) -> None:
        """Teste l'importation d'une sauvegarde"""
        with patch.object(
            Config(), 'save_location', os.path.join(mock_profiles_dir, PROFILES_FOLDER_NAME)
        ):
            target = os.path.join(mock_profiles_dir, PROFILES_FOLDER_NAME, '78541323')
            os.makedirs(target)
            assert save_manager.import_save('save1', 'default')
