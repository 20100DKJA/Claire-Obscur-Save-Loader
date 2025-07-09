from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog

from clair_obscur_save_loader.views.settings import SettingsComponent


class TestSettingsComponentIntegration:
    def test_settings_dialog_displays(self, qapp: QApplication, monkeypatch) -> None:  # noqa: ANN001
        """Teste que la fenêtre modale s'affiche correctement"""
        exec_called = False

        def mock_exec_(self):  # noqa: ANN001, ANN202
            nonlocal exec_called
            exec_called = True
            return QDialog.Accepted

        monkeypatch.setattr(QDialog, 'exec_', mock_exec_)

        settings = SettingsComponent()
        result = settings.exec_()

        assert exec_called is True
        assert result == QDialog.Accepted
