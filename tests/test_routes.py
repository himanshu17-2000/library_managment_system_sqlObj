import requests
import json
import pytest
from models.Member import Member

@pytest.mark.xfail
def test_home_route(client):
    res = client.get("/")
    assert res.status_code == 200


def test_register_route(client):
    data1 = {"name": "Poojan", "email": "Poojan@gmail.com", "phone": 321657892}
    resp = client.post('/register' , json=data1)
    resp_json = resp.json
    id = resp_json['mem_id']
    assert resp.status_code == 200 
    assert resp_json['message'] == 'member added' 
    assert resp_json['mem_id']  > 0 
    resp = client.delete(f'/delmember/{id}')


def test_register_route_invalid_1(client):
    data1 = {"email": "vishwa@gmail.com", "phone": 7854213265}
    url = "/register"
    resp = client.post(url, json=data1)
    res_json = resp.json
    assert resp.status_code == 404
    assert res_json["message"] == "Key Error = All values not Available"

    data2 = {"name": "", "email": "vishwa@gmail.com", "phone": 7854213265}
    url = "/register"
    resp2 = client.post(url, json=data2)
    res2_json = resp2.json
    assert resp2.status_code == 400
    assert res2_json["message"] == "Please fill all values"


def test_delete_member1(client):
    data1 = {"name": "rockey", "email": "rockey@gmail.com", "phone": 321654987}
    resp1 = client.post('/register' , json=data1)
    resp1_json = resp1.json
    id = resp1_json['mem_id']
    resp = client.delete(f"/delmember/{id}")
    assert resp.status_code == 200


def test_get_member_id(client):
    resp1 = client.get("/getmember/10")
    resp1_json = resp1.json
    assert resp1.status_code==404


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
    assert res1.json["message"] == "First_return the previouly borrowed book"

def test_borrow_route_invalid(client):
    data1 = {"member_id": 1, "book_id": 1}
    res1 = client.post("/borrow", json=data1)
    print(res1.json)
    assert res1.status_code == 200
    assert res1.json["message"] != ""
    assert res1.json["message"] == "First_return the previouly borrowed book"
    

def test_return_book_route(client):
    data1 = {"tra_id": 1}
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
    # assert res1.json["message"] != ""
    # assert res1.json["message"] == "Amount returned"
    # assert res1.json["amount"] == amount


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




def test_deleted_book_id(client):
    data1= {
        "book_name": "Atomic Habits",
        "book_author": "anonymous",
        "book_stock": 10,
    }
    res1 = client.post("/addbook" , json=data1)
    print(res1.json)
    res1 = client.delete(f"/deletebook/{res1.json['book_id']}")
    assert res1.status_code == 200
    assert res1.json["message"] == "Book deleted"


def test_deleted_book_id_invalid(client):
    res1 = client.delete("/deletebook/21")

    assert res1.status_code == 404
    assert res1.json["message"] == "Book Not Found"


def test_transactions_fetch(client):
    res1 = client.get("/transactions")

    assert res1.status_code == 200
    assert res1.json != []
    assert len(res1.json) > 0

def test_transactions_by_id(client):
    res1 = client.get("/transactions/3")
    assert res1.status_code == 200
    assert res1.json != []
    assert len(res1.json) > 0


def test_transactions_by_id_invalid(client):
    res1 = client.get("/transactions/1231")
    assert res1.status_code == 404
    assert res1.json != []
    assert res1.json == None


def test_end_to_end(client):
    # Registering Member 
    data1 = {"name": "Harsh", "email": "Harsh@gmail.com", "phone": 9865322154}
    resp = client.post('/register' , json=data1)
    resp_json = resp.json
    mem_id = resp_json['mem_id']
    assert resp.status_code == 200 
    assert resp_json['message'] == 'member added' 
    assert resp_json['mem_id']  > 0 

    # Borrow book 
    data2={"member_id":mem_id , "book_id":1}
    resp_borrow = client.post('/borrow' , json=data2)
    resp_borrow_json = resp_borrow.json
    tra_id= resp_borrow_json['tra_id']
    assert resp_borrow_json["message"]=="Thanks for Borrowing Book"
    assert resp_borrow.status_code == 200

    #return book 
    data3={"tra_id":tra_id}
    resp_return = client.post('/return' , json=data3)
    resp_return_json =  resp_return.json
    fine = resp_return_json['rent']
    assert resp_return_json["message"]=="Book has been Returned"
    assert resp_return.status_code == 200

    #returning fine 
    data4={"member_id":mem_id,"amount":fine}
    resp_debt = client.post('/debt',json= data4)
    resp_debt_json = resp_debt.json
    assert resp_debt.status_code == 200 

    #deleting member 
    resp_delete_member = client.delete(f'/delmember/{mem_id}')
    resp_delete_member_json =  resp_delete_member.json
    assert resp_delete_member.status_code == 200
    assert resp_delete_member_json['message'] == "Member Deleted"
    
    