from init_app import create_app
from sqlobject import *
import os

testing = True 
app = create_app(testing)

if __name__ == "__main__":
    app.run(debug=True)
