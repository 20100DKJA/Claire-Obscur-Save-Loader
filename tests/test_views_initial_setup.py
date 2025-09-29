from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader.views.initial_setup import InitialSetupComponent


class TestInitialSetupComponent:
    def test_window_properties(self, qapp: QApplication) -> None:
        """Teste les propriétés de base de la fenêtre"""
        initial_setup = InitialSetupComponent()

        # Vérifier les propriétés de base
        assert initial_setup.windowTitle() == 'Initial Setup'
        assert initial_setup.minimumWidth() == 450
        assert initial_setup.minimumHeight() == 250
        assert initial_setup.isModal() is True

    def test_ui_elements_exist(self, qapp: QApplication) -> None:
        """Teste que tous les éléments UI sont créés"""
        initial_setup = InitialSetupComponent()

        # Vérifier la présence des boutons
        assert initial_setup.select_button is not None
        assert initial_setup.continue_button is not None
        assert initial_setup.exit_button is not None
        assert initial_setup.path_label is not None

        # Vérifier l'état initial des boutons
        assert initial_setup.continue_button.isEnabled() is False
        assert initial_setup.select_button.isEnabled() is True
        assert initial_setup.exit_button.isEnabled() is True

    def test_button_text(self, qapp: QApplication) -> None:
        """Teste le texte des boutons"""
        initial_setup = InitialSetupComponent()

        assert initial_setup.select_button.text() == 'Select Game Save Directory'
        assert initial_setup.continue_button.text() == 'Continue'
        assert initial_setup.exit_button.text() == 'Exit'
        assert initial_setup.path_label.text() == 'No path selected'
