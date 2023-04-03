"""
Модель view для трат
"""
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton
from bookkeeper.view.categories_view import CategoryDialog
from datetime import timedelta
import sys


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.header_names = list(data[0].__dataclass_fields__.keys())
        #self.header_names = ['x', 'y', 'z']

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_names[section]
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0].__dataclass_fields__)
        #return 3

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Карманный бухгалтер")

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel('Расходы'))

        self.expenses_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.expenses_grid)

        self.layout.addWidget(QLabel('Бюджет'))

        self.budget_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.budget_grid)

        self.bottom_controls = QGridLayout()

        self.bottom_controls.addWidget(QLabel('Сумма'), 0, 0)

        self.amount_line_edit = QLineEdit()
        self.bottom_controls.addWidget(self.amount_line_edit, 0, 1)

        self.bottom_controls.addWidget(QLabel('Комментарий'), 1, 0)

        self.comment_line_edit = QLineEdit()
        self.bottom_controls.addWidget(self.comment_line_edit, 1, 1)

        self.bottom_controls.addWidget(QLabel('Категория'), 2, 0)

        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems
        self.bottom_controls.addWidget(self.category_dropdown, 2, 1)

        self.category_edit_button = QPushButton('Редактировать')
        self.bottom_controls.addWidget(self.category_edit_button, 2, 2)
        self.category_edit_button.clicked.connect(self.show_cats_dialog)

        self.expense_add_button = QPushButton('Добавить')
        self.bottom_controls.addWidget(self.expense_add_button, 3, 1)
        self.expense_add_button.clicked.connect(self.on_expense_add_button_clicked) #TODO кнопка

        self.expense_delete_button = QPushButton('Удалить')
        self.bottom_controls.addWidget(self.expense_delete_button, 3, 2)
        self.expense_delete_button.clicked.connect(self.on_expense_delete_button_clicked) #TODO кнопка

        self.bottom_controls.addWidget(QLabel('Бюджет'), 4, 0)

        self.budget_line_edit = QLineEdit()
        self.bottom_controls.addWidget(self.budget_line_edit, 4, 1)

        self.bottom_controls.addWidget(QLabel('Период'), 5, 0)

        self.period_dropdown = QComboBox()
        self.period_dropdown.addItems(['День', 'Неделя', 'Месяц'])
        self.bottom_controls.addWidget(self.period_dropdown, 5, 1)

        self.budget_add_button = QPushButton('Задать бюджет')
        self.bottom_controls.addWidget(self.budget_add_button, 6, 1)
        self.budget_add_button.clicked.connect(self.on_budget_add_button_clicked)

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(self.bottom_controls)

        self.layout.addWidget(self.bottom_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def set_expense_table(self, data):
        if data:
            self.item_model = TableModel(data)
            self.expenses_grid.setModel(self.item_model)
            self.expenses_grid.resizeColumnsToContents()
            grid_width = sum([self.expenses_grid.columnWidth(x) for x in range(0, self.item_model.columnCount(0) + 1)])
            self.setFixedSize(grid_width + 80, 600)

    def set_budget_table(self, data):
        if data:
            self.item_model = TableModel(data)
            self.budget_grid.setModel(self.item_model)
            self.budget_grid.resizeColumnsToContents()
            grid_width = sum([self.budget_grid.columnWidth(x) for x in range(0, self.item_model.columnCount(0) + 1)])
            self.setFixedSize(grid_width + 80, 600)

    def set_category_dropdown(self, data):
        if data:
            for c in data:
                self.category_dropdown.addItem(c.name, c.pk)

    def on_expense_add_button_clicked(self, slot: object):
        self.expense_add_button.clicked.connect(slot)

    def on_expense_delete_button_clicked(self, slot: object):
        self.expense_delete_button.clicked.connect(slot)

    def on_budget_add_button_clicked(self, slot: object):
        self.budget_add_button.clicked.connect(slot)

    def on_category_edit_button_clicked(self, slot: object):
        self.category_edit_button.clicked.connect(slot)

    def get_comment(self) -> str:
        return str(self.comment_line_edit.text())

    def get_amount(self) -> float:
        return float(self.amount_line_edit.text())

    def  get_budget_amount(self):
       return float(self.budget_line_edit.text())

    def __get_selected_row_indices(self) -> list[int]:
        return list(set([qmi.row() for qmi in self.expenses_grid.selectionModel().selection().indexes()]))

    def get_selected_expenses(self) -> list[int] | None:
        idx = self.__get_selected_row_indices()
        if not idx:
            return None
        return [self.item_model._data[i].pk for i in idx]

    def get_selected_budget(self):
        return self.period_dropdown.itemData(self.category_dropdown.currentIndex())

    def get_selected_cat(self) -> int:
        return self.category_dropdown.itemData(self.category_dropdown.currentIndex())

    def show_cats_dialog(self, data):
        if data:
            cat_dlg = CategoryDialog(data)
            cat_dlg.setWindowTitle('Редактирование категорий')
            cat_dlg.setGeometry(300, 100, 600, 300)
            cat_dlg.exec()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
