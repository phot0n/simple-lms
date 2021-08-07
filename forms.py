from wtforms import Form, StringField, IntegerField
from wtforms import PasswordField, validators


class LibrarianLoginForm(Form):
    username = StringField("username", [
            validators.Length(min=3, max=64), 
            validators.DataRequired()
        ]
    )
    password = PasswordField("password", [
            validators.Length(min=3),
            validators.DataRequired()
        ]
    )


class AddBooksForm(Form):
    title = StringField("title")
    no_of_books = IntegerField("no_of_books", [
        validators.DataRequired()
        ]
    )
    authors = StringField("authors")
    publishers = StringField("publishers")
    isbn = StringField("isbn")


class AddDeleteMemberForm(Form):
    username = StringField("username", [
        validators.Length(min=3),
        validators.DataRequired()
        ]
    )


class RentReturnBookForm(Form):
    bookid = StringField("bookid", [
        validators.Length(min=1),
        validators.DataRequired()
        ]
    )
    member_username = StringField("member_username", [
        validators.Length(min=3),
        validators.DataRequired()
        ]
    )


class SearchForm(Form):
    bookid = StringField("bookid")
    title = StringField("title")
    author = StringField("author")


class DebtForm(Form):
    username = StringField("username", [
        validators.DataRequired()
        ]
    )
    amount = IntegerField("amount", [
        validators.DataRequired()
        ]
    )
