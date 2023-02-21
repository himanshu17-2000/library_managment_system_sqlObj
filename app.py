from init_app import create_app
from sqlobject import *
import os


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
