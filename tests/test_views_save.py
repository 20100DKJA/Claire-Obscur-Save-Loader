import pytest
from PyQt5.QtWidgets import QApplication

from clair_obscur_save_loader.views.save import SaveComponent


@pytest.fixture
def save_component(qapp: QApplication) -> SaveComponent:
    """Crée une instance de SaveComponent"""
    return SaveComponent()


class TestSaveComponent:
    def test_component_initialization(self, save_component: SaveComponent) -> None:
        assert save_component is not None
        assert save_component.count() == 0

    def test_add_save_item(self, save_component: SaveComponent) -> None:
        save_component.addItem('123456')

        assert save_component.count() == 1
        assert save_component.item(0).text() == '123456'

    def test_clear_saves(self, save_component: SaveComponent) -> None:
        save_component.addItem('123456')
        save_component.addItem('789012')

        save_component.clear()

        assert save_component.count() == 0

    def test_get_selected_save(self, save_component: SaveComponent) -> None:
        save_component.addItem('123456')
        save_component.addItem('789012')

        # Sélectionner un élément
        save_component.setCurrentRow(1)

        # Vérifier la sélection
        selected = save_component.currentItem().text()
        assert selected == '789012'
