from datetime import datetime, date
from sqlobject import SQLObjectNotFound
from flask import Blueprint, jsonify
from flask import request
from models.Book import Book
from models.Member import Member
from models.Transaction import Transaction

api = Blueprint("api", __name__)


@api.route("/")
def home():
    return "<h1>Himanshu kumar amb </h1>", 200


@api.route("/register", methods=["POST"])
def register_member():
    name = request.json["name"]
    email = request.json["email"]
    phone = request.json["phone"]
    single_member = Member.select(
        Member.q.email == email)  # naming coonvention
    if list(single_member) == []:
        Member(name=name, email=email, phone=phone)
        return jsonify({"message": "member added "}), 200
    return jsonify({"message": "member already access "}), 401


@api.route("/getmember/<int:_id>", methods=["GET"])
def get_member(_id):
    try:
        user = Member.get(_id)
    except SQLObjectNotFound:
        return "object not found ", 404
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


@api.route("/delmember/<int:_id>", methods=["GET"])
def delete_member(_id):
    try:
        user = Member.get(_id)
    except SQLObjectNotFound:
        return "object not found ", 404
    else:
        user.delete(_id)
        return jsonify({"message": "Member Deleted"}), 200


@api.route("/borrow", methods=["POST"])
def borrow_book():
    boro_book_id = request.json["book_id"]
    boro_member_id = request.json["member_id"]

    # ================= checking if user id exists ================================
    member = Member.select(Member.q.id == boro_member_id)
    if list(member) == []:
        return jsonify({"message": "Member Does not exists , Please register"}), 404
    # =============== Making New Tuple in Transactions =============================
    member = Member.get(boro_member_id)
    if (member.debt >= 500):
        return jsonify({"message": "Your debt exceeded 500rs repay before borrowing book"}), 200

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
    tra_id = request.json["tra_id"]
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
    # t_date = datetime.now().date()
    t_date = date(2023, 2, 28)
    diff = t_date - f_date
    new_fine = (diff.days) * 10
    new_debt = member.debt + new_fine
    tra.set(fine=new_fine)
    member.set(debt=new_debt)
    print(member.debt)
    return jsonify({"message": "Book has been Returned", "rent": tra.fine}), 200


@api.route('/debt', methods=['POST'])
def pay_debt():
    member_id = request.json['member_id']
    amount = request.json['amount']
    member = Member.get(member_id)
    p_debt = member.debt
    n_debt = p_debt-amount
    member.set(debt=n_debt)
    return jsonify({"message": "Amount returned", "amount": amount, 'remaining': member.debt}), 200


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
    members = []
    for value, key in arr:
        members.append(Member.get(key))
    return jsonify(list(map(get_dict, members))), 200


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
    name = request.json["book_name"]
    author = request.json["book_author"]
    stock = request.json["book_stock"]
    prevbook = list(Book.selectBy(book_name=name, book_author=author))[0]
    if prevbook is not None:
        prevbook.book_stock += stock
    else:
        Book(book_name=name, book_author=author, book_stock=stock)

    return jsonify({"message": "Book Added"}), 200


@api.route("/deletebook/<int:_id>", methods=["GET"])
def deletebook(_id):
    try:
        book = Book.get(_id)
    except SQLObjectNotFound:
        return "object not found ", 404
    else:
        book.delete(_id)
    return jsonify({"message": "Book deleted"}), 404


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
