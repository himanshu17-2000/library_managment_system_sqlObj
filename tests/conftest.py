import pytest
from flask import jsonify
from init_app import create_app

@pytest.fixture()
def app():
    testing = True
    app  = create_app(testing) 
    app.config.update({
        "TESTING": True,
    })
    return app 

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
