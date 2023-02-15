from sqlobject import *
from datetime import datetime


class Transaction(SQLObject):
    class sqlmeta:
        table = "transactions"

    book_id = IntCol(notNone=False)
    member_id = IntCol(notNone=False)
    book_name = StringCol(notNone=False)
    from_date = DateCol(default=datetime.now().date())
    borrowed = BoolCol(default=True)
    fine = IntCol(default=0)
