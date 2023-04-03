from PySide6 import QtWidgets
from bookkeeper.view.expense_view import MainWindow
from bookkeeper.presenter.expense_presenter import ExpensePresenter
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree
import sys

db_name = 'test.db'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    view = MainWindow()

    model = [Category, Expense, Budget]

    cat_repo = SQLiteRepository(db_name, Category)

    exp_repo = SQLiteRepository(db_name, Expense)

    budget_repo = SQLiteRepository(db_name, Budget)

    window = ExpensePresenter(model, view, cat_repo, exp_repo, budget_repo) #передать три репозитория
    window.show()
    app.exec()
