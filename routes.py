import re
import uuid
import yaml
from flask import request
from flask import redirect
from flask import render_template
from flask import flash, url_for
from flask import make_response


import interact_db
import forms
import helper_funcs
from data_fetcher import frappeAPI


# /
def login_page():
    login_form = forms.LibrarianLoginForm(request.form)

    if request.method == "GET":
        if helper_funcs.check_session(request):
            return redirect(url_for("index_page"))

        return render_template("login.html", form=login_form)

    if request.method == "POST":
        if login_form.validate():

            # if user presses login button
            if request.form.get("log"):
                if interact_db.DBInteraction.check_librarian(
                    login_form.username.data, 
                    login_form.password.data
                ):
                    # check number of cookies for a user
                    if len(
                        interact_db.DBInteraction.get_librarian_sessions(
                            login_form.username.data
                        )
                    ) + 1 > 4:
                        print(
                            f"Max number of sessions for librarian\
                            `{login_form.username.data}` reached, Removing first created!"
                        )
                        interact_db.DBInteraction.delete_session(
                            login_form.username.data
                        )

                    unique_id = str(uuid.uuid4())
                    interact_db.DBInteraction.add_session(
                        login_form.username.data, 
                        unique_id
                    )
                    # make cookie
                    res = make_response(redirect(url_for("index_page")))
                    print("Making New Cookie")
                    # NOTE: as a cookie's structure is of the form of key:value,
                    # I've taken key to be the librarian's name so that there is only 
                    # 1 value associated with it at any point and will overrite the 
                    # uuid(value) in the cases.
                    res.set_cookie(
                        login_form.username.data, 
                        value=unique_id
                    ) 
                    return res

            # if user presses register button
            if request.form.get("register"):
                interact_db.DBInteraction.add_librarian(
                    login_form.username.data, 
                    login_form.password.data
                )
        else:
            flash("Not able to Validate. Please Provide Librarian's Username and Password")

        return redirect(url_for("login_page"))


# /index
def index_page(booklist=None):
    booksform = forms.AddBooksForm(request.form)
    membersform = forms.AddDeleteMemberForm(request.form)
    rentalform = forms.RentReturnBookForm(request.form)
    searchform = forms.SearchForm(request.form)
    debtform = forms.DebtForm(request.form)

    if request.method == "GET":
        if helper_funcs.check_session(request):
            # check the request args for searched books
            args_books = request.args.get("booklist", None)
            if args_books and args_books != "{}":
                books = yaml.load(
                    args_books, Loader=yaml.BaseLoader
                )
            else:
                books = helper_funcs.convert_books_obj_to_dict(
                    interact_db.DBInteraction.get_all_books()
                )

            return render_template(
                "index.html", 
                bookform=booksform, 
                memberform=membersform, 
                rentalform=rentalform,
                searchform=searchform,
                debtform=debtform,
                book_dict=books
            )

        return redirect(url_for("login_page"))

    if request.method == "POST":
        msg = ""
        books = {}

        if request.form.get("add-books"):
            if booksform.validate():
                l, d = frappeAPI.get_data(
                    number_of_books=booksform.no_of_books.data,
                    title=booksform.title.data,
                    authors=booksform.authors.data,
                    publisher=booksform.publishers.data,
                    isbn=booksform.isbn.data
                )
                interact_db.DBInteraction.add_books(d)
                msg = f"Found {l} books for the query - Added to the Database"

        if request.form.get("add-member"):
            if membersform.validate():
                interact_db.DBInteraction.add_member(membersform.username.data)

            if request.form.get("delete-member"):
                interact_db.DBInteraction.delete_member(membersform.username.data)

        if request.form.get("rent-book"):
            if rentalform.validate():
                interact_db.DBInteraction.update_member_and_book(
                    rentalform.member_username.data,
                    rentalform.bookid.data,
                    rent=True
                )

        if request.form.get("return-book"):
            if rentalform.validate():
                interact_db.DBInteraction.update_member_and_book(
                    rentalform.member_username.data,
                    rentalform.bookid.data,
                    return_book=True 
                )

        if request.form.get("pay-debt"):
            if debtform.validate():
                interact_db.DBInteraction.update_member_debt(
                    debtform.username.data,
                    debtform.amount.data
                )

        if request.form.get("search-book"):
            all_books = interact_db.DBInteraction.get_all_books()
            # TODO: make this better
            for b in all_books:
                if searchform.bookid.data:
                    if re.search(searchform.bookid.data.strip(), b.bookid):
                        books[b.bookid]= [
                            b.title, 
                            b.authors, 
                            b.publisher,
                            b.average_rating,
                            b.available_quantity,
                            b.total_quantity
                        ]
                        continue

                if searchform.title.data:
                    if re.search(
                        searchform.title.data.strip().lower(), 
                        b.title.lower()
                    ):
                        books[b.bookid]= [
                            b.title, 
                            b.authors, 
                            b.publisher,
                            b.average_rating,
                            b.available_quantity,
                            b.total_quantity
                        ]
                        continue
                
                if searchform.author.data:
                    if re.search(
                        searchform.author.data.strip().lower(), 
                        b.authors.lower()
                    ):
                        books[b.bookid]= [
                            b.title, 
                            b.authors, 
                            b.publisher,
                            b.average_rating,
                            b.available_quantity,
                            b.total_quantity
                        ]

            if not books:
                msg = "No books found for the query"            

        flash(msg)

        if books:
            return redirect(url_for("index_page", booklist=books))
        return redirect(url_for("index_page"))

# /logout
def logout():
    '''
    This method is helpful in logging the user out.
    It will delete the session from the db 
    (but won't remove the cookie from the browser.
    though we can do that by setting the expiry date of the cookie 
    to something previous from when it was set)
    '''

    helper_funcs.del_session(request)
    return redirect(url_for("login_page"))


# /reports
def reports():
    if helper_funcs.check_session(request):
        book_dict, member_dict = helper_funcs.get_report_data(
            interact_db.DBInteraction.get_all_books(),
            interact_db.DBInteraction.get_all_members()
        )
        return render_template("reports.html", books=book_dict, members=member_dict)
    return redirect(url_for("login_page"))
