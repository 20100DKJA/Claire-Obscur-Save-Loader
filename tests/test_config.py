from unittest.mock import mock_open
from unittest.mock import patch

from clair_obscur_save_loader.config import Config


class TestConfig:
    def test_get_save_location(self, mock_config_file: str, config: Config) -> None:
        """Teste la récupération du chemin du jeu"""
        with patch.object(config, 'config_file', mock_config_file):
            config._load_config()
            assert config.save_location == '/path/to/test/saves'

    def test_save_location_no_config(self, config: Config) -> None:
        """Teste le comportement quand aucun fichier de configuration n'existe"""
        with (
            patch.object(config, 'config_file', '/non/existent/path'),
        ):
            config._load_config()
            game_dir = config.save_location
            assert game_dir is None

    def test_save_config(self, config: Config) -> None:
        """Teste l'enregistrement du chemin du jeu"""
        mock_open_obj = mock_open()
        config_path = '/path/to/config.json'

        with (
            patch.object(config, 'config_file', config_path),
            patch('builtins.open', mock_open_obj),
            patch('json.dump') as mock_json_dump,
            patch('os.path.exists', return_value=False),
            patch('os.makedirs') as mock_makedirs,
        ):
            config.save_location = '/new/game/dir'
            config._save_config()

            # Vérifier que le dossier a été créé si nécessaire
            mock_makedirs.assert_called_once()

            # Vérifier que le fichier a été ouvert pour écriture
            mock_open_obj.assert_called_once_with(config_path, 'w')

            # Vérifier que les données ont été écrites
            mock_json_dump.assert_called_once()
            args, _ = mock_json_dump.call_args
            assert args[0]['save_location'] == '/new/game/dir'
