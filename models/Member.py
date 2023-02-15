from sqlobject import *


class Member(SQLObject):
    class sqlmeta:
        table = "members"

    name = StringCol(length=20, notNone=False)
    email = StringCol(notNone=False)
    phone = IntCol(notNone=False)
    debt = IntCol(default=0)
