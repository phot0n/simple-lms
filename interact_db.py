from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc
from flask import flash, abort

import app
import models



class DBInteraction:
    '''
    This class is used to interact with the db
    '''

    @staticmethod
    def initialize_db():
        app.db.create_all()

    @staticmethod
    def delete_db():
        app.db.drop_all()

    @staticmethod
    def add_books(data : list):
        '''
        TODO: optimize
        '''

        inserted_books = DBInteraction.get_all_books()
        if inserted_books:
            for inserted_book in inserted_books:
                for book in data:
                    if book["bookID"] == inserted_book.bookid:
                        inserted_book.total_quantity += book["available_quantity"]
                        inserted_book.available_quantity += book["available_quantity"]
                        data.remove(book)
                        break

        if data:
            entries = []
            for b in data:
                entry = models.Books(
                    bookid=b["bookID"], 
                    title=b["title"], 
                    authors=b["authors"], 
                    average_rating=b["average_rating"], 
                    isbn=b["isbn"], 
                    publisher=b["publisher"], 
                    total_quantity=b["available_quantity"],
                    available_quantity=b["available_quantity"],
                    times_rented=b["times_rented"]
                )
                entries.append(entry)
            app.db.session.add_all(entries)

        app.db.session.commit()
        print("Added/Updated Books")

    @staticmethod
    def get_book(bookid : str):
        return models.Books.query.filter_by(bookid=bookid).first()

    @staticmethod
    def get_all_books():
        return models.Books.query.all()

    @staticmethod
    def add_librarian(username : str, password : str):
        if not isinstance(username, str) or \
            not isinstance(password, str):
            raise Exception(
                "Please provide username (string) and password (string)\
                    to be registered as a librarian"
            )

        if not username or not password:
            raise Exception("Username and/or Password cannot be empty!")

        try:
            app.db.session.add(
                models.Librarians(
                    username=username, 
                    password_hash=generate_password_hash(password)
                )
            )
            app.db.session.commit()
            flash(f"{username} Added as a Librarian")
        except exc.IntegrityError:
            flash(
                "Librarian with the same username exists\
                    (Librarian's Username should be Unique)"
            )


    @staticmethod
    def get_all_librarians():
        return models.Librarians.query.all()

    @staticmethod
    def check_librarian(username : str, password : str):
        if not isinstance(username, str) or \
            not isinstance(password, str):
            raise Exception(
                "Please provide username (string) and password (string)\
                    to be checked as a librarian"
            )

        if not username or not password:
            raise Exception("Username and/or Password cannot be empty!")

        librarian = models.Librarians.query.filter_by(username=username).first()
        if librarian:
            if not check_password_hash(librarian.password_hash, password):
                flash(f"Wrong password for librarian `{username}`")
                return
            return True

        flash(f"Librarian `{username}` doesn't exist!")

    @staticmethod
    def add_member(username : str):
        if not isinstance(username, str):
            raise Exception(
                "Please provide username (string) and password (string)\
                    to be registered as a member"
            )

        if not username:
            raise Exception("Username and/or Password cannot be empty!")

        try:
            app.db.session.add(
                models.Members(
                    username=username
                )
            )
            app.db.session.commit()
            flash(f"{username} Added as a Member")
        except exc.IntegrityError:
            flash("Member with the same username exists\
                (Member's Username should be Unique)")

    @staticmethod
    def delete_member(username : str):
        member = models.Members.query.filter_by(username=username).first()
        if member:
            app.db.session.delete(
                member
            )
            app.db.session.commit()
            flash(f"{username} deleted as a member!")
        else:
            flash(f"{username} doesn't exist as a member!")

    @staticmethod
    def get_all_members():
        return models.Members.query.all()

    @staticmethod
    def get_member(username : str):
        if not isinstance(username, str):
            raise Exception(
                "Please provide username (string) and password (string)\
                    to be checked as a member"
            )

        if not username:
            raise Exception("Username cannot be empty!")

        return models.Members.query.filter_by(username=username).first()

    @staticmethod
    def update_member_and_book(
        username: str, 
        bookid: str, 
        rent : bool=False, 
        return_book : bool=False
        ):
        '''
        TODO: clean up
        '''
        member = DBInteraction.get_member(username)
        book = DBInteraction.get_book(bookid)
        msg = ""

        if rent:
            if book and book.available_quantity > 0 and member:
                if not member.current_rented_book:
                    if member.debt < 500:
                        member.current_rented_book = True
                        member.date_of_rental = datetime.now().strftime("%d/%m/%Y")
                        book.available_quantity -= 1
                        book.times_rented += 1

                        app.db.session.commit()
                        msg = f"The Book `{bookid}` has been rented\
                            to Member `{username}`"
                    else:
                        msg = f"Book cannot be issued to the member `{username}`\
                            as they have debt Rs. `{member.debt}`"

                else:
                    msg = f"Member `{username}` currently has a rented book.\
                        Please return it first!"
            else:
                msg = f"The Book `{bookid}` and/or Member `{username}` doesn't exist"

        if return_book:
            if book and member:
                if member.current_rented_book:
                    todays_date = datetime.now()
                    date_of_rental = datetime.strptime(
                        member.date_of_rental, 
                        "%d/%m/%Y"
                    )
                    num_of_days_rented = (todays_date - date_of_rental).days
                    # 10rs rent for each day
                    amount_owed = num_of_days_rented * 10

                    member.current_rented_book = False
                    member.date_of_rental = None
                    member.debt += amount_owed
                    book.available_quantity += 1

                    app.db.session.commit()
                    msg = f"Member `{username}` owes Rs.`{amount_owed}`\
                        for renting book `{bookid}` for `{num_of_days_rented}` days\
                        - @ Rs. 10/day - Adding it to Debt!"

                else:
                    msg = f"Member `{username}` currently has no rented book!"
            else:
                msg = f"The Book `{bookid}` and/or Member `{username}` doesn't exist"

        flash(msg)

    @staticmethod
    def update_member_debt(username : str, amount : int):
        if not username or not amount:
            raise Exception("Username and/or amount cannot be empty!")

        member = DBInteraction.get_member(username=username)
        if member:
            if amount <= member.debt:
                member.debt = member.debt - amount
                member.total_money_paid += amount
                if member.debt == 0:
                    flash(f"Member `{username}` paid their whole debt!")
                flash("Updated Member's debt")
            else:
                flash(f"Amount is more than member's debt.\
                    Deducting Rs. `{member.debt}` (Debt) from Rs. {amount}!")
                member.total_money_paid += member.debt
                member.debt = 0

            app.db.session.commit()
        else:
            flash(f"Member `{username}` not found")

    @staticmethod
    def add_session(librarian_name : str, uuid : str):
        if not librarian_name or not uuid:
            raise Exception("Librarian name and/or uuid cannot be empty!")

        app.db.session.add(
            models.Sessions(
                sessionid=uuid,
                librarian_name=librarian_name
            )
        )
        app.db.session.commit()

    @staticmethod
    def check_session(librarian_name : str, uuid : str):
        session = models.Sessions.query.filter_by(sessionid=uuid).first()
        if session:
            return session.librarian_name == librarian_name
        return False

    @staticmethod
    def delete_session(librarian_name : str, uuid : str=""):
        if uuid:
            # gets the specific session
            session = models.Sessions.query.filter_by(sessionid=uuid).first()
        else:
            if not librarian_name:
                raise Exception("Librarian's name is required to delete the session!")
            # gets first session created by user
            session = models.Sessions.query.filter_by(
                librarian_name=librarian_name
            ).first()

        if session:
            app.db.session.delete(
                session
            )
            app.db.session.commit()
            print("Session Deleted")
        else:
            print(f"Session for `{librarian_name}` doesn't exist!")

    @staticmethod
    def get_librarian_sessions(librarian_name : str):
        if not librarian_name:
            raise Exception("Librarian's Name cannot be empty")
        return models.Sessions.query.filter_by(librarian_name=librarian_name).all()
