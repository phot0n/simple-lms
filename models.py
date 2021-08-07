import app


class Members(app.db.Model):
    memberid = app.db.Column(app.db.Integer, primary_key=True)
    # keeping the username unique for simplicity
    username = app.db.Column(app.db.String(64), unique=True)
    current_rented_book = app.db.Column(app.db.String(64), nullable=True) # will have bookid
    date_of_rental = app.db.Column(app.db.String(50), nullable=True) # put date from which the book was rented
    total_money_paid = app.db.Column(app.db.Integer, default=0)
    debt = app.db.Column(app.db.Integer, default=0)

    def __repr__(self):
        return "Member {}, {}, {}, {}".format(
            self.username, self.debt, self.current_rented_book, self.date_of_rental
        )


class Librarians(app.db.Model):
    librarianid = app.db.Column(app.db.Integer, primary_key=True)
    # keeping the username unique for simplicity
    username = app.db.Column(app.db.String(64), unique=True)
    password_hash = app.db.Column(app.db.String(200))

    def __repr__(self):
        return "Librarian {}, {}".format(self.librarianid, self.username)


class Books(app.db.Model):
    bookid = app.db.Column(app.db.String(20), primary_key=True)
    title = app.db.Column(app.db.String(300))
    authors = app.db.Column(app.db.String(128))
    average_rating = app.db.Column(app.db.String(10))
    isbn = app.db.Column(app.db.String(64))
    publisher = app.db.Column(app.db.String(128))
    total_quantity = app.db.Column(app.db.Integer)
    available_quantity = app.db.Column(app.db.Integer)
    times_rented = app.db.Column(app.db.Integer)

    def __repr__(self):
        return "Book {}, {}, total_quantity: {}, available_quantity: {}, times_rented: {}".format(
            self.bookid, self.title, self.total_quantity, self.available_quantity, self.times_rented
        )


class Sessions(app.db.Model):
    sessionid = app.db.Column(app.db.String(100), primary_key=True)
    librarian_name = app.db.Column(app.db.String(64))

    def __repr__(self):
        return "Session - {}".format(self.librarian_name)
