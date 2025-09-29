from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


class ControlsComponent(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = parent

        layout = QHBoxLayout()

        self.restart_button = QPushButton('Restart Game')
        layout.addWidget(self.restart_button)

        self.setLayout(layout)
