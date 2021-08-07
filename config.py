import os 


class Configs:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
