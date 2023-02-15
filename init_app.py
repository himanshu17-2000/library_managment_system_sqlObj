from flask import Flask
from api.routes import api
from models.User import User
from models.Book import Book
from models.Member import Member
from models.Transaction import Transaction
from flask_cors import CORS
from sqlobject import *

def create_app():
    app = Flask(__name__)
    Book.createTable(ifNotExists = True)
    Member.createTable(ifNotExists = True)
    Transaction.createTable(ifNotExists = True)
    CORS(app)
    app.register_blueprint(api)
    return app
