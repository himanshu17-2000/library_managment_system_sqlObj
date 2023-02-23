from datetime import datetime, date
from sqlobject import SQLObjectNotFound
from flask import Blueprint, jsonify, request
from models.Book import Book
from models.Member import Member
from models.Transaction import Transaction
import requests

api = Blueprint("api", __name__)


@api.route("/")
def home():
    try:
        args = request.args
        url = "https://hapi-books.p.rapidapi.com/nominees/romance/2020"
        if args.to_dict() != {}:
            url = f"https://hapi-books.p.rapidapi.com/nominees/{args['genre']}/{args['year']}"

        headers = {
            "X-RapidAPI-Key": "9c254922afmsh6ac51f1b70c0bdep1978f1jsn7f9444b252cf",
            "X-RapidAPI-Host": "hapi-books.p.rapidapi.com",
        }

        response = requests.request("GET", url, headers=headers)

        books = response.json()
        print(books)
        for book in books:
            b = Book(
                book_name=book["name"],
                book_author=book["author"],
                book_votes=book["votes"],
            )
    except:
        return (
            "<h1>Something Went Wrong in Third Party Api or YOur are Filling repeated Values </h1>",
            400,
        )
    return "<h1>Himanshu kumar amb </h1>", 200


@api.route("/register", methods=["POST"])
def register_member():
    name = ""
    email = ""
    phone = None
    try:
        name = request.json["name"]
        email = request.json["email"]
        phone = request.json["phone"]

    except KeyError:
        return jsonify({"message": "Key Error = All values not Available"}), 404

    if name == "" or email == "" or phone == None:
        return jsonify({"message": "Please fill all values"}), 400
    mem_id = None
    single_member = Member.select(Member.q.email == email)  # naming coonvention
    if list(single_member) == []:
        mem_id = Member(name=name, email=email, phone=phone).id
        return jsonify({"message": "member added", "mem_id": mem_id}), 200
    return (
        jsonify(
            {"message": "member already exists", "mem_id": list(single_member)[0].id}
        ),
        401,
    )


@api.route("/getmember/<int:_id>", methods=["GET"])
def get_member(_id):
    try:
        user = Member.get(_id)
    except SQLObjectNotFound:
        return jsonify({"message": "member not found"}), 404
    else:

        def get_dict(item):
            return {
                "member_id": item.id,
                "name": item.name,
                "email": item.email,
                "phone": item.phone,
                "debt": item.debt,
            }

        arr = list(map(get_dict, [user]))
        return jsonify(arr), 200


@api.route("/getmembers", methods=["GET"])
def get_members():
    user = Member.select()
    user = list(user)

    def get_dict(item):
        return {
            "member_id": item.id,
            "name": item.name,
            "email": item.email,
            "phone": item.phone,
            "debt": item.debt,
        }

    arr = list(map(get_dict, user))
    return jsonify(arr), 200


@api.route("/delmember/<int:_id>", methods=["DELETE"])
def delete_member(_id):
    try:
        user = Member.get(_id)
    except SQLObjectNotFound:
        return jsonify({"message": "Object Not found"}), 404
    else:
        pending_tra = list(Transaction.selectBy(member_id=user.id , borrowed=True))
        if(pending_tra != []):
            return jsonify({"message": "Can't Revoke member ship please return borrowed book, and pay your rent"}),400 
        user.delete(_id)
        return jsonify({"message": "Member Deleted"}), 200


@api.route("/borrow", methods=["POST"])
def borrow_book():
    boro_book_id = None
    boro_member_id = None
    try:
        boro_book_id = request.json["book_id"]
        boro_member_id = request.json["member_id"]
    except KeyError:
        return jsonify({"message": "Key Error = All values not Available"}), 404

    if boro_book_id == None or boro_member_id == None:
        return jsonify({"message": "Please fill all values"}), 400

    # ================= checking if user id exists ================================
    member = Member.select(Member.q.id == boro_member_id)
    if list(member) == []:
        return jsonify({"message": "Member Does not exists , Please register"}), 404
    # =============== Making New Tuple in Transactions =============================
    member = Member.get(boro_member_id)
    if member.debt >= 500:
        return (
            jsonify(
                {"message": "Your debt exceeded 500rs repay before borrowing book"}
            ),
            200,
        )

    book = Book.select(Book.q.id == boro_book_id)
    book = list(book)[0]
    if book.book_stock <= 0:
        return jsonify({"message": "Book Out of stock"}), 404
    single_tra = list(
        Transaction.selectBy(
            book_id=boro_book_id, member_id=boro_member_id, borrowed=True
        )
    )
    if single_tra != []:
        return jsonify({"message": "First_return the previouly borrowed book"})
    Tra = Transaction(
        book_id=boro_book_id, member_id=boro_member_id, book_name=book.book_name
    )
    new_book_stock = book.book_stock - 1
    new_book_votes = book.book_votes + 1
    book.set(book_stock=new_book_stock, book_votes=new_book_votes)
    return jsonify({"message": "Thanks for Borrowing Book", "tra_id": Tra.id}), 200


@api.route("/return", methods=["POST"])
def return_book():
    tra_id = None
    try:
        tra_id = request.json["tra_id"]
    except KeyError:
        return jsonify({"message": "Key Error = All values not Available"}), 404
    if tra_id == None:
        return jsonify({"message": "Please fill all values"}), 400
    try:
        temp_tra = Transaction.get(tra_id)
    except SQLObjectNotFound:
        return (
            jsonify({"message": "Invalid Transaction id"}),
            400,
        )

    test = list(Transaction.selectBy(id=tra_id, borrowed=False))
    if test != []:
        return (
            jsonify({"message": "Old Record,Book already Returned"}),
            200,
        )

    tra = list(Transaction.selectBy(id=tra_id, borrowed=True))[0]
    book = list(Book.selectBy(id=tra.book_id))[0]
    member = list(Member.selectBy(id=tra.member_id))[0]
    new_book_stock = book.book_stock + 1
    book.set(book_stock=new_book_stock)
    tra.set(borrowed=False)
    f_date = tra.from_date
    t_date = datetime.now().date()
    # t_date = date(2023, 2, 28)
    diff = t_date - f_date
    new_fine = (diff.days) * 10
    new_debt = member.debt + new_fine
    tra.set(fine=new_fine)
    member.set(debt=new_debt)
    return jsonify({"message": "Book has been Returned", "rent": tra.fine}), 200


@api.route("/debt", methods=["POST"])
def pay_debt():
    member_id = None
    amount = None
    try:
        member_id = request.json["member_id"]
        amount = request.json["amount"]
    except KeyError:
        return jsonify({"message": "Key Error = All values not Available"}), 404
    if member_id == None and amount == None:
        return jsonify({"message": "Please fill all values"}), 400
    try:
        member = Member.get(member_id)
        if(member.debt == 0 ):
            return jsonify({"message": "No Debt left","fine" :member.debt}), 200
        
    except SQLObjectNotFound:
        return jsonify({"message": "Object Not Found"}), 404

    p_debt = member.debt
    n_debt = p_debt - amount
    member.set(debt=n_debt)
    return (
        jsonify(
            {"message": "Amount returned", "amount": amount, "remaining": member.debt}
        ),
        200,
    )


@api.route("/popular", methods=["GET"])
def popular():
    def get_dict(item):
        return {
            "book_id": item.id,
            "book_name": item.book_name,
            "book_author": item.book_author,
            "book_stock": item.book_stock,
            "votes": item.book_votes,
        }

    data = list(Book.select())
    arr = sorted(list(map(get_dict, data)), key=lambda x: x["votes"])
    return jsonify(arr[::-1]), 200


@api.route("/highpaying", methods=["GET"])
def highpaying():
    def get_dict(item):
        return {
            "book_id": item.id,
            "book_name": item.name,
            "book_author": item.email,
            "book_stock": item.phone,
            "votes": item.debt,
        }

    transactions = list(Transaction.select())
    dic = {}
    for transaction in transactions:
        if transaction.member_id not in dic:
            dic[transaction.member_id] = 1
        else:
            dic[transaction.member_id] += 1
    arr = [(v, k) for k, v in dic.items()]
    arr.sort()
    print(arr)
    members = []
    for value, key in arr:
        try:
            members.append(Member.get(key))
        except:
            continue
    print(members)
    return jsonify(list(map(get_dict, members))), 200
    # return "hell0" , 200


@api.route("/books", methods=["GET"])
def fetchbooks():
    def get_dict(item):
        return {
            "book_id": item.id,
            "book_name": item.book_name,
            "book_author": item.book_author,
            "book_stock": item.book_stock,
            "votes": item.book_votes,
        }

    data = list(Book.select())
    return jsonify(list(map(get_dict, data))), 200


@api.route("/addbook", methods=["POST"])
def addbook():
    try:
        name = None
        author = None
        stock = None

        try:
            name = request.json["book_name"]
            author = request.json["book_author"]
            stock = request.json["book_stock"]
        except KeyError:
            return jsonify({"message": "Key Error = All values not Available"}), 404

        if name == "" or author == "" or stock == None:
            return jsonify({"message": "Please fill all values"}), 400

        prevbook = Book.selectBy(book_name=name, book_author=author)
        book_id = None
        if list(prevbook) != []:
            prev_book = list(prevbook)[0]
            prev_book.book_stock += stock
        else:
            book_id = Book(book_name=name, book_author=author, book_stock=stock).id

    except:
        return jsonify({"message": "Something Went Wrong"}), 400

    return jsonify({"message": "Book Added", "book_id": book_id}), 200


@api.route("/deletebook/<int:_id>", methods=["DELETE"])
def deletebook(_id):
    try:
        book = Book.get(_id)
    except SQLObjectNotFound:
        return jsonify({"message": "Book Not Found"}), 404
    else:
        book.delete(_id)
    return jsonify({"message": "Book deleted"}), 200


@api.route("/transactions", methods=["GET"])
def transactions():
    def get_dict(item):
        return {
            "tra_id": item.id,
            "book_id": item.book_id,
            "member_id": item.member_id,
            "book_name": item.book_name,
            "from_date": str(item.from_date),
            "fine": item.fine,
            "borrowed": item.borrowed,
        }

    tras = list(Transaction.select())
    return jsonify(list(map(get_dict, tras)))


@api.route("/transactions/<int:_id>", methods=["GET"])
def transaction_by_id(_id):
    def get_dict(item):
        return {
            "tra_id": item.id,
            "book_id": item.book_id,
            "member_id": item.member_id,
            "book_name": item.book_name,
            "from_date": str(item.from_date),
            "fine": item.fine,
            "borrowed": item.borrowed,
        }

    try:
        tras = Transaction.get(_id)
    except SQLObjectNotFound:
        return "object not found ", 404
    return jsonify(list(map(get_dict, [tras])))


@api.route("/get_book_by_name", methods=["POST"])
def get_book_by_name():
    obj = request.json
    book = None
    if obj.get("book_name") is not None and obj.get("author") is not None:
        book = Book.selectBy(
            book_name=obj.get("book_name"), book_author=obj.get("author")
        )
    elif obj.get("book_name") is None and obj.get("author") is not None:
        book = Book.selectBy(book_author=obj.get("author"))
    elif obj.get("book_name") is not None and obj.get("author") is None:
        book = Book.selectBy(book_name=obj.get("book_name"))

    def get_dict(item):
        return {
            "book_id": item.id,
            "book_name": item.book_name,
            "book_author": item.book_author,
            "book_stock": item.book_stock,
            "votes": item.book_votes,
        }

    books = list(book)
    return jsonify(list(map(get_dict, books))), 200



