import requests
import json
import pytest


def test_home_route(client):
    res = client.get("/")
    assert res.status_code == 200


def test_register_route(client):
    data = {"name": "vishwa", "email": "vishwa@gmail.com", "phone": 7854213265}
    url = "/register"

    resp = client.post(url, json=data)
    res_json = resp.json
    assert resp.status_code != 200
    assert resp.status_code == 401
    assert type(res_json) == type({})
    if resp.status_code == 401:
        assert res_json["message"] == "member already access"


def test_get_member_id(client):
    resp1 = client.get("/getmember/10")
    resp2 = client.get("/getmember/1")
    resp1_json = resp1.json
    resp2_json = resp2.json
    assert resp1.status_code != 200
    assert resp1_json["message"] == "member not found"
    assert resp2.status_code == 200
    assert resp2_json[0]["name"] == "poojan"


def test_get_allmembers(client):
    resp = client.get("/getmembers")
    assert resp.status_code == 200
    assert resp.json != []
    assert resp.json[1]["name"] != ""


def test_borrow_route(client):
    data1 = {"member_id": 1, "book_id": 1}

    res1 = client.post("/borrow", json=data1)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] != ""
    assert res1.json["message"] == "First_return the previouly borrowed book"
    data2 = {"member_id": 1, "book_id": 2}
    res2 = client.post("/borrow", json=data2)
    print(res2.json)
    assert res2.status_code == 200
    assert res2.json["message"] != ""
    assert res2.json["message"] == "First_return the previouly borrowed book"


def test_return_book_route(client):
    data1 = {"tra_id": 3}
    res1 = client.post("/return", json=data1)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] != ""
    assert res1.json["message"] == "Old Record,Book already Returned"


def test_return_book_route(client):
    data1 = {"tra_id": 3}
    res1 = client.post("/return", json=data1)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] != ""
    assert res1.json["message"] == "Old Record,Book already Returned"


def test_debt_fetch(client):
    amount = 10
    data1 = {"member_id": 1, "amount": amount}
    res1 = client.post("/debt", json=data1)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] != ""
    assert res1.json["message"] == "Amount returned"
    assert res1.json["amount"] == amount


def test_debt_fetch_invalid(client):
    amount = 10
    data1 = {"member_id": 100, "amount": amount}
    res1 = client.post("/debt", json=data1)
    print(res1.json)
    assert res1.status_code == 404
    assert res1.json["message"] != ""
    assert res1.json["message"] == "Object Not Found"


def test_popular_fetch(client):
    res1 = client.get("/popular")
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json != []


def test_popular_fetch_invalid(client):
    res1 = client.get("/popular")
    print(res1.json)
    assert res1.status_code != 400
    assert len(res1.json) > 0


def test_highpaying_fetch(client):
    res1 = client.get("/highpaying")
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json != []
    assert len(res1.json) > 0


def test_addbook(client):
    data = {
        "book_name": "Murder on orient express",
        "book_author": "Agatha cristie",
        "book_stock": 10,
    }
    res1 = client.post("/addbook", json=data)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] == "Book Added"


@pytest.mark.xfail
def test_deleted_book_id(client):
    res1 = client.get("/deletebook/21")

    assert res1.status_code == 200
    assert res1.json["message"] == "Book deleted"


def test_deleted_book_id_invalid(client):
    res1 = client.get("/deletebook/21")

    assert res1.status_code == 404
    assert res1.json["message"] == "Book deleted"


def test_transactions_fetch(client):
    res1 = client.get("/transactions")

    assert res1.status_code == 200
    assert res1.json != []
    assert len(res1.json) > 0


@pytest.mark.xfail
def test_transactions_by_id(client):
    res1 = client.get("/transactions/1")

    assert res1.status_code == 200
    assert res1.json != []
    assert len(res1.json) > 0


def test_transactions_by_id_invalid(client):
    res1 = client.get("/transactions/1")

    assert res1.status_code == 404
    assert res1.json != []
    assert res1.json == None
