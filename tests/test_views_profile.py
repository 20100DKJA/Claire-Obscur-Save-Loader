import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton

from clair_obscur_save_loader.views.profile import ProfileComponent


@pytest.fixture
def profile_component(qapp: QApplication) -> ProfileComponent:
    """Crée une instance de ProfileComponent"""
    return ProfileComponent()


class TestProfileComponent:
    def test_component_initialization(self, profile_component: ProfileComponent) -> None:
        assert profile_component is not None

        assert isinstance(profile_component, QComboBox)
        assert profile_component.count() == 0

        assert profile_component.buttons
        for button in profile_component.buttons.values():
            assert isinstance(button, QPushButton)
        assert profile_component.vbox_profile.count() == len(profile_component.buttons)

    def test_add_profile_item(self, profile_component: ProfileComponent) -> None:
        """Teste l'ajout d'un élément à la liste des profils"""
        profile_component.addItem('default')

        assert profile_component.count() == 1
        assert profile_component.itemText(0) == 'default'

    def test_clear_profiles(self, profile_component: ProfileComponent) -> None:
        """Teste la suppression de tous les profils"""
        profile_component.addItem('default')
        profile_component.addItem('advanced')

        profile_component.clear()

        assert profile_component.count() == 0

    def test_get_selected_profile(self, profile_component: ProfileComponent) -> None:
        """Teste la récupération du profil sélectionné"""
        profile_component.addItem('default')
        profile_component.addItem('advanced')

        profile_component.setCurrentIndex(1)

        selected = profile_component.currentText()
        assert selected == 'advanced'

    def test_button_states(self, profile_component: ProfileComponent) -> None:
        assert profile_component.buttons['Create Profile'].isEnabled()
        assert profile_component.buttons['Delete Profile'].isEnabled()
        assert profile_component.buttons['Duplicate Profile'].isEnabled()
        assert profile_component.buttons['Rename Profile'].isEnabled()
