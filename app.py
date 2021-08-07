import os
import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Configs


f_app = Flask(__name__)
f_app.config.from_object(Configs)
f_app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(f_app)

import interact_db
import routes


# ref: https://flask.palletsprojects.com/en/2.0.x/patterns/lazyloading/#converting-to-centralized-url-map
f_app.add_url_rule('/', view_func=routes.login_page, methods=['GET', 'POST'])
f_app.add_url_rule('/index', view_func=routes.index_page, methods=['GET', 'POST'])
f_app.add_url_rule('/reports', view_func=routes.reports)
f_app.add_url_rule('/logout', view_func=routes.logout)



if __name__ == "__main__":
    if not os.path.exists(
        Configs.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
    ):
        print("Initializing DB")
        interact_db.DBInteraction.initialize_db()

    f_app.run(debug=True, host="0.0.0.0", use_reloader=True)
