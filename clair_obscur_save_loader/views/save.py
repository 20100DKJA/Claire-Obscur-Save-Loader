from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QWidget

from clair_obscur_save_loader.controllers.save import SaveItemModel


class SaveComponent(QTreeView):
    save_double_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = parent

        self._save_item_model: SaveItemModel | None = None

        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Save list and context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Save action buttons
        self.import_button = QPushButton('Import', self)
        self.load_button = QPushButton('Load', self)
        self.replace_button = QPushButton('Replace', self)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.import_button)
        self.h_layout.addWidget(self.load_button)
        self.h_layout.addWidget(self.replace_button)

    def change_profile(self, model: SaveItemModel) -> None:
        self._save_item_model = model
        self.setModel(model)

    def clear(self) -> None:
        self._save_item_model = None
        self.setModel(QStandardItemModel())

    def current_save_model(self) -> SaveItemModel | None:
        return self._save_item_model

    def selected_save_data(self) -> tuple[str | None, str | None, bool, bool]:
        if self._save_item_model is None:
            return None, None, False, False

        return self._save_item_model.get_save_data(self.currentIndex())

    def save_data_at(self, position: QPoint) -> tuple[str | None, str | None, bool, bool]:
        if self._save_item_model is None:
            return None, None, False, False

        return self._save_item_model.get_save_data(self.indexAt(position))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.setCurrentIndex(QModelIndex())
        QTreeView.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self._save_item_model is not None:
            _, _, is_save_dir, _ = self._save_item_model.get_save_data(self.indexAt(event.pos()))
            if is_save_dir:
                self.save_double_clicked.emit()
        QTreeView.mouseDoubleClickEvent(self, event)
