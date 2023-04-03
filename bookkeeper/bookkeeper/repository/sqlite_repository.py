from inspect import get_annotations
import sqlite3
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    db_file - название файла базы данных
    cls - данные
    table_name - название таблицы
    fields - поля таблицы
    names, p - переменные для sql запросов
    """

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file: str = db_file
        self.cls: type = cls
        self.table_name: str = cls.__name__
        self.fields: dict[str, any] = get_annotations(cls, eval_str=True) #словарь
        self.fields.pop('pk')

        self.names = ', '.join(self.fields.keys())
        self.p = ', '.join("?" * len(self.fields))

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            res = cur.execute('SELECT name FROM sqlite_master')
            db_tables = [t[0].lower() for t in res.fetchall()]
            if self.table_name not in db_tables:
                col_names = ', '.join(self.fields.keys())
                db_q = f'CREATE TABLE IF NOT EXISTS {self.table_name} (' \
                    f'"pk" INTEGER PRIMARY KEY AUTOINCREMENT, {col_names})'
                cur.execute(db_q)
        conn.close()

    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'INSERT INTO {self.table_name} ({self.names}) VALUES ({self.p})', values)
            obj.pk = cur.lastrowid
        conn.close()
        return obj.pk

    def __row_to_obj(self, db_row: tuple) -> T:
        obj = self.cls(self.fields)
        for field, value in zip(self.fields, db_row[1:]):
            setattr(obj, field, value)
        obj.pk = db_row[0]
        return obj

    def get(self, pk: int) -> T | None:
        """Получить объект по id"""
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'SELECT * FROM {self.table_name} WHERE pk = {pk}')
            row = cur.fetchone()
        conn.close()

        if row is None:
            return None

        return self.__row_to_obj(row)

    def get_all(self, where: dict[str, any] | None = None):
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            if where is None:
                cur.execute(f'SELECT * FROM {self.table_name}')
            else:
                db_q = ' AND'.join([f'{key} = "{value}"' for key, value in where.items()])
                cur.execute(f'SELECT * FROM {self.table_name} WHERE {db_q}')

            rows = cur.fetchall()
        conn.close()

        if rows:
            return [self.__row_to_obj(row) for row in rows]
        else:
            return []

    def update(self, obj: T):
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        sets = ', '.join(f'{name} = {getattr(obj, name)}' for name in self.names)
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'UPDATE {self.table_name} SET {sets} WHERE pk = {obj.pk}')
        conn.close()

    def delete(self, pk: int):
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'DELETE FROM {self.table_name} WHERE pk = {pk}')
        conn.close()


