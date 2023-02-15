from sqlobject import *


class Book(SQLObject):
    class sqlmeta:
        table = "books"

    book_name = StringCol(length=20, notNone=False)
    book_author = StringCol(length=20, notNone=False)
    book_stock = IntCol(default=20)
    book_votes = IntCol(length=20, default=0)
