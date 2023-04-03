"""
Модель бюджета
"""
from dataclasses import dataclass
from datetime import date, timedelta
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense

@dataclass
class Budget:
    period: str
    amount: int
    budget: int
    pk: int = 0

    def calculate(self, repo: AbstractRepository['Expense']) -> int:  # TODO добавить категорию бюджета
        """Считает сумму расходов за указанный срок
        repo - репозиторий расходов
        exp - сумма расходов за период
        """
        prom = timedelta(days=0)
        if self.period == 'День':
            prom = timedelta(days=1)
        if self.period == 'Неделя':
            prom = timedelta(weeks=7)
        if self.period == 'Месяц':
            prom = timedelta(days=30)

        start_date = date.today() - prom
        end_date = date.today()
        exp = repo.get_all(where={'expense_date': (start_date, end_date)})
        for e in exp:
            self.amount += e.amount
        return self.amount


