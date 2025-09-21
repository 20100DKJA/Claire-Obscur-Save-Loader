import os
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from PyQt5.QtWidgets import QFileDialog

from clair_obscur_save_loader.config import Config
from clair_obscur_save_loader.controllers.initial_setup import InitialSetupController
from clair_obscur_save_loader.managers import SaveManager
from clair_obscur_save_loader.views.initial_setup import InitialSetupComponent


@pytest.fixture
def mock_initial_setup_view() -> InitialSetupComponent:
    """Crée un mock du composant de paramètres"""
    view = MagicMock(spec=InitialSetupComponent)
    view.path_label = MagicMock()
    view.continue_button = MagicMock()
    view.select_button = MagicMock()
    view.exit_button = MagicMock()
    return view


@pytest.fixture
def mock_save_manager() -> SaveManager:
    save_manager = MagicMock(spec=SaveManager)
    return save_manager


@pytest.fixture
def mock_config() -> Config:
    config = MagicMock(spec=Config)
    return config


@pytest.fixture
def controller(
    mock_initial_setup_view: InitialSetupComponent,
    mock_save_manager: SaveManager,
    mock_config: Config,
) -> InitialSetupController:
    """Crée un contrôleur avec des mocks"""
    return InitialSetupController(
        view=mock_initial_setup_view, save_manager=mock_save_manager, config=mock_config
    )


class TestInitialSetupController:
    def test_initialize_controller(self, controller: InitialSetupController) -> None:
        """Teste l'initialisation du contrôleur"""
        assert controller is not None
        assert controller._view is not None
        assert controller._save_manager is not None
        assert controller._config is not None

    def test_setup_connections(
        self,
        controller: InitialSetupController,
        mock_initial_setup_view: InitialSetupComponent,
    ) -> None:
        """Teste que les connexions de signal/slot sont configurées"""
        # Vérifie si la méthode existe
        controller.setupConnections()

        # Vérifie que les boutons ont été connectés
        assert mock_initial_setup_view.select_button.clicked.connect.called
        assert mock_initial_setup_view.exit_button.clicked.connect.called
        assert mock_initial_setup_view.continue_button.clicked.connect.called

    def test_browse_directory(
        self,
        controller: InitialSetupController,
        mock_initial_setup_view: InitialSetupComponent,
    ) -> None:
        """Teste la navigation pour sélectionner un répertoire"""
        # Créer un répertoire temporaire avec la structure attendue
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un sous-dossier numérique (comme attendu pour un dossier de sauvegarde valide)
            os.mkdir(os.path.join(temp_dir, '123456'))
            with open(os.path.join(temp_dir, '123456', 'SavesContainer.sav'), 'w'):
                pass

            # Simuler la boîte de dialogue de sélection de fichier
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=temp_dir):
                # Appelle la méthode qui gère la sélection de répertoire
                # J'utilise un nom générique qui pourrait correspondre à ta vraie méthode
                controller.browseSaveLocation()
                assert controller._config.save_location == temp_dir
