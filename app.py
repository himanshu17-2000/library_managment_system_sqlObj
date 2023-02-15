from init_app import create_app
from sqlobject import *
import os

db_filename = os.path.abspath("data.sqlite")
connection_string = "sqlite:" + db_filename

sqlhub.processConnection = connectionForURI(connection_string)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
