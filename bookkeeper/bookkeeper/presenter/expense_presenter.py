"""
Модель Презентера
"""

from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.utils import read_tree


class ExpensePresenter:

    def __init__(self, model, view, cat_repo, exp_repo, budget_repo):
        self.model = model
        self.view = view
        self.exp_repo = exp_repo
        self.budget_repo = budget_repo
        self.cat_repo = cat_repo

        self.exp_data = exp_repo.get_all()

        self.cat_data = cat_repo.get_all()
        self.budget_data = budget_repo.get_all()

        cats = '''
                        продукты
                            мясо
                                сырое мясо
                                мясные продукты
                            сладости
                        книги
                        одежда
                        '''.splitlines()
        #if self.cat_data is None:
        #Category.create_from_tree(read_tree(cats), self.cat_repo)

        self.view.on_expense_add_button_clicked(self.handle_expense_add_button_clicked)

        self.view.on_expense_delete_button_clicked(self.handle_expense_delete_button_clicked)

        self.view.on_category_edit_button_clicked(self.handle_category_edit_button_clicked)

        self.view.on_budget_add_button_clicked(self.handle_budget_add_button_clicked)



    def update_expense_data(self):
        if self.exp_data is not None:
            for e in self.exp_data:
                for c in self.cat_data:
                    if c.pk == e.category:
                        e.category = c.name
                        break
        self.view.set_expense_table(self.exp_data)

    def update_cat_data(self):  # TODO: доделать
        self.view.set_category_dropdown(self.cat_data)

    def update_budget_data(self):
        self.view.set_budget_table(self.budget_data)

    def show(self):
        self.view.show()
        self.update_expense_data()
        self.view.set_category_dropdown(self.cat_data)

    def handle_expense_add_button_clicked(self) -> None:
        cat_pk = self.view.get_selected_cat()
        amount = self.view.get_amount()
        comment = self.view.get_comment()

        exp = Expense(int(amount), cat_pk, str(comment))

        self.exp_repo.add(exp)
        self.update_expense_data()

    def handle_expense_delete_button_clicked(self) -> None:
        selected = self.view.get_selected_expenses()
        if selected:
            for e in selected:
                self.exp_repo.delete(e)
            self.update_expense_data()

    def handle_category_edit_button_clicked(self):
        self.view.show_cats_dialog(self.cat_data)

    def handle_budget_add_button_clicked(self):
        period = self.view.get_selected_budget()
        budget = self.view.get_budget_amount()
        amount = Budget(period=period, amount=0, budget=0).calculate(self.exp_repo)
        budg = Budget(period, int(amount), int(budget))
        self.budget_repo.add(budg)
        self.update_budget_data()



