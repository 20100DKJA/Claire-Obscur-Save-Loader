from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader.views.settings import SettingsComponent


class TestSettingsComponent:
    def test_window_properties(self, qapp: QApplication) -> None:
        """Teste les propriétés de base de la fenêtre"""
        settings = SettingsComponent()

        # Vérifier les propriétés de base
        assert settings.windowTitle() == 'Initial Setup'
        assert settings.minimumWidth() == 450
        assert settings.minimumHeight() == 250
        assert settings.isModal() is True

    def test_ui_elements_exist(self, qapp: QApplication) -> None:
        """Teste que tous les éléments UI sont créés"""
        settings = SettingsComponent()

        # Vérifier la présence des boutons
        assert settings.select_button is not None
        assert settings.continue_button is not None
        assert settings.exit_button is not None
        assert settings.path_label is not None

        # Vérifier l'état initial des boutons
        assert settings.continue_button.isEnabled() is False
        assert settings.select_button.isEnabled() is True
        assert settings.exit_button.isEnabled() is True

    def test_button_text(self, qapp: QApplication) -> None:
        """Teste le texte des boutons"""
        settings = SettingsComponent()

        assert settings.select_button.text() == 'Select Game Save Directory'
        assert settings.continue_button.text() == 'Continue'
        assert settings.exit_button.text() == 'Exit'
        assert settings.path_label.text() == 'No path selected'
