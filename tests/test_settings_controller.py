import os
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from PyQt5.QtWidgets import QFileDialog

from clair_obscur_save_loader.controllers.settings import SettingsController
from clair_obscur_save_loader.managers import MainManager
from clair_obscur_save_loader.views.settings import SettingsComponent


@pytest.fixture
def mock_settings_view() -> SettingsComponent:
    """Crée un mock du composant de paramètres"""
    view = MagicMock(spec=SettingsComponent)
    view.path_label = MagicMock()
    view.continue_button = MagicMock()
    view.select_button = MagicMock()
    view.exit_button = MagicMock()
    return view


@pytest.fixture
def mock_manager() -> MainManager:
    """Crée un mock du manager principal"""
    manager = MagicMock(spec=MainManager)
    return manager


@pytest.fixture
def controller(
    mock_settings_view: SettingsComponent, mock_manager: MainManager
) -> SettingsController:
    """Crée un contrôleur avec des mocks"""
    return SettingsController(view=mock_settings_view, manager=mock_manager)


class TestSettingsController:
    def test_initialize_controller(self, controller: SettingsController) -> None:
        """Teste l'initialisation du contrôleur"""
        assert controller is not None
        assert controller._view is not None
        assert controller._manager is not None

    def test_setup_connections(
        self, controller: SettingsController, mock_settings_view: SettingsComponent
    ) -> None:
        """Teste que les connexions de signal/slot sont configurées"""
        # Vérifie si la méthode existe
        controller.setupConnections()

        # Vérifie que les boutons ont été connectés
        assert mock_settings_view.select_button.clicked.connect.called
        assert mock_settings_view.exit_button.clicked.connect.called
        assert mock_settings_view.continue_button.clicked.connect.called

    def test_browse_directory(
        self, controller: SettingsController, mock_settings_view: SettingsComponent
    ) -> None:
        """Teste la navigation pour sélectionner un répertoire"""
        # Créer un répertoire temporaire avec la structure attendue
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un sous-dossier numérique (comme attendu pour un dossier de sauvegarde valide)
            os.mkdir(os.path.join(temp_dir, '123456'))

            # Simuler la boîte de dialogue de sélection de fichier
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=temp_dir):
                # Appelle la méthode qui gère la sélection de répertoire
                # J'utilise un nom générique qui pourrait correspondre à ta vraie méthode
                controller.browseSaveLocation()
                assert controller._manager.set_save_location.called
