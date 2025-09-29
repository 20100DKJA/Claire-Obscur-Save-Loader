from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog

from clair_obscur_save_loader.views.initial_setup import InitialSetupComponent


class TestInitialSetupComponentIntegration:
    def test_initial_setup_dialog_displays(self, qapp: QApplication, monkeypatch) -> None:  # noqa: ANN001
        """Teste que la fenêtre modale s'affiche correctement"""
        exec_called = False

        def mock_exec_(self):  # noqa: ANN001, ANN202
            nonlocal exec_called
            exec_called = True
            return QDialog.Accepted

        monkeypatch.setattr(QDialog, 'exec_', mock_exec_)

        initial_setup = InitialSetupComponent()
        result = initial_setup.exec_()

        assert exec_called is True
        assert result == QDialog.Accepted
