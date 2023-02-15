from sqlobject import *


class User(SQLObject):
    class sqlmeta:
        table = "users"

    name = StringCol()
    email = StringCol()
    phone = IntCol()
    admin = BoolCol()
