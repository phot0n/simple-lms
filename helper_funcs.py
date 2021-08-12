from flask import request

import interact_db


def get_cookies(req : request):
    return req.cookies.to_dict()


def check_session(req : request):
    cookies = get_cookies(req)
    if cookies:
        for lib_name, uid in cookies.items():
            # check all the cookies 
            # (we do this because flask also creates it's own "session" cookie)
            if interact_db.DBInteraction.check_session(lib_name, uid):
                return True
    return False


def del_session(req: request):
    cookies = get_cookies(req)
    if cookies:
        for lib_name, uid in cookies.items():
            interact_db.DBInteraction.delete_session(lib_name, uuid=uid)


def convert_books_obj_to_dict(books : list):
    books_dict = {}
    if books:
        for book in books:
            books_dict[book.bookid] = [
                book.title, 
                book.authors, 
                book.publisher,
                book.average_rating,
                book.available_quantity,
                book.total_quantity
            ]

    return books_dict


def get_report_data(books : list, members : list):
    books_chart= {
        "rented": [],
        "available": [],
        "total": [],
        "title": []
    }
    members_chart = {
        "name": [],
        "total_paid": []
    }

    for book in books:
        books_chart["rented"].append(book.times_rented)
        books_chart["available"].append(book.available_quantity)
        books_chart["total"].append(book.total_quantity)
        books_chart["title"].append(book.title)

    for member in members:
        members_chart["name"].append(member.username)
        members_chart["total_paid"].append(member.total_money_paid)
    
    return books_chart, members_chart
