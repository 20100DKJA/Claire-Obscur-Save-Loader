import os
from bisect import bisect_right
from collections.abc import Iterable
from typing import Self

from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QMimeData
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QStyle

from clair_obscur_save_loader.managers.save import looks_like_save_path


class DirectoryItem:
    def __init__(self, path: str, parent: Self | None, is_save_dir: bool) -> None:
        self.path = path
        self.parent = parent
        self.children: list[DirectoryItem] = []
        self.is_save_dir = is_save_dir

    def append_child(self, child: Self) -> None:
        self.children.append(child)


class SaveItemModel(QAbstractItemModel):
    def __init__(self, profile_path: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.root_item = DirectoryItem(profile_path, None, False)
        self.load_directories(self.root_item)

    def load_directories(self, parent_item: DirectoryItem) -> None:
        for dir_name in sorted(os.listdir(parent_item.path)):
            dir_path = os.path.join(parent_item.path, dir_name)
            if os.path.isdir(dir_path):
                is_save_dir = looks_like_save_path(dir_path)
                dir_item = DirectoryItem(dir_path, parent_item, is_save_dir)
                if not is_save_dir:
                    self.load_directories(dir_item)
                parent_item.append_child(dir_item)

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent is None or not parent.isValid():
            return len(self.root_item.children)
        item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 1

    def data(self, index: QModelIndex | None = None, role: int = Qt.DisplayRole) -> QVariant:
        if index is None or not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return QVariant(os.path.basename(item.path))
        if role == Qt.DecorationRole and not item.is_save_dir:
            return QVariant(
                QApplication.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DirIcon))
            )

        return QVariant()

    def get_save_data(self, index: QModelIndex) -> tuple[str, str, bool, bool]:
        item = index.internalPointer() if index.isValid() else self.root_item
        parent = item.parent if item.is_save_dir and item.parent is not None else item

        return parent.path, item.path, item.is_save_dir, item == self.root_item

    def index(self, row: int, column: int, parent: QModelIndex | None = None) -> QModelIndex:
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        if row < 0 or row >= len(parent_item.children) or column != 0:
            return QModelIndex()
        item = parent_item.children[row]

        return self.createIndex(row, column, item)

    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item.parent == self.root_item:
            return QModelIndex()

        parent_item = item.parent
        grandparent_item = parent_item.parent
        row = grandparent_item.children.index(parent_item)

        return self.createIndex(row, 0, parent_item)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlags(Qt.ItemFlag.ItemIsDropEnabled)

        item = index.internalPointer()
        if item.is_save_dir:
            return Qt.ItemFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsDragEnabled
            )

        return Qt.ItemFlags(
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropActions(Qt.DropAction.MoveAction)

    def mimeTypes(self) -> list[str]:
        return ['text/uri-list']

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        data = QMimeData()
        data.setUrls(
            QUrl.fromLocalFile(idx.internalPointer().path) for idx in indexes if idx.isValid()
        )

        return data

    def _item_for_path(self, root: DirectoryItem, path: str) -> DirectoryItem | None:
        if not path.startswith(root.path):
            return None
        if root.path == path:
            return root
        for item in root.children:
            sub_item = self._item_for_path(item, path)
            if sub_item is not None:
                return sub_item
        return None

    def _mime_data_to_items(self, data: QMimeData | None) -> list[DirectoryItem] | None:
        if data is None or data.formats() != ['text/uri-list']:
            return None

        items = []
        for url in data.urls():
            if not url.isLocalFile():
                return None
            local_path = os.path.normpath(url.toLocalFile())
            item = self._item_for_path(self.root_item, local_path)
            if item is None:
                return None
            items.append(item)

        return items

    def canDropMimeData(
        self,
        data: QMimeData | None,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        if action != Qt.MoveAction or column < -1 or column > 0:
            return False
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        dropped_items = self._mime_data_to_items(data)
        if dropped_items is None:
            return False

        return any(dropped_item.parent != parent_item for dropped_item in dropped_items)

    def dropMimeData(
        self,
        data: QMimeData | None,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        dropped_items = self._mime_data_to_items(data)
        if dropped_items is None:
            return False

        for dropped_item in dropped_items:
            new_path = os.path.join(parent_item.path, os.path.basename(dropped_item.path))
            if os.path.exists(new_path):
                return False

            row = bisect_right([child.path for child in parent_item.children], new_path)
            os.rename(dropped_item.path, new_path)

            self.beginInsertRows(parent, row, row)
            new_item = DirectoryItem(new_path, parent_item, dropped_item.is_save_dir)
            parent_item.children.insert(row, new_item)
            if not dropped_item.is_save_dir:
                self.load_directories(new_item)
            self.endInsertRows()

        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex | None = None) -> bool:
        parent_item = (
            parent.internalPointer() if parent is not None and parent.isValid() else self.root_item
        )
        if row < 0 or count < 1 or row + count > len(parent_item.children):
            return False

        self.beginRemoveRows(parent if parent is not None else QModelIndex(), row, row + count - 1)
        del parent_item.children[row : row + count]
        self.endRemoveRows()

        return True

    def refresh_path(self, path: str) -> None:
        item = self._item_for_path(self.root_item, path)
        if item is None:
            return
        if item.is_save_dir:
            return

        if item.parent is None:
            item_index = QModelIndex()
        else:
            parent_item = item.parent if item.parent is not None else self.root_item
            row_in_parent = parent_item.children.index(item)
            item_index = self.createIndex(row_in_parent, 0, item)

        new_item = DirectoryItem(item.path, item.parent, item.is_save_dir)
        self.load_directories(new_item)

        i = 0
        while True:
            a = item.children[i] if i < len(item.children) else None
            b = new_item.children[i] if i < len(new_item.children) else None
            if a is None and b is None:
                break
            if a is not None and b is not None and a.path == b.path:
                i += 1
                continue
            if b is None or (a is not None and a.path < b.path):
                self.removeRow(i, item_index)
                continue
            if a is None or a.path > b.path:
                self.beginInsertRows(item_index, i, i)
                b.parent = item
                item.children.insert(i, b)
                self.endInsertRows()
                continue
