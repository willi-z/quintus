from flask import Flask
from quintus.server.api import api
from quintus.server.frontend import frontend
from quintus.server.setup import db
from quintus.server.helpers.user import User
from flask_login import LoginManager  # noqa

import os
from pathlib import Path
import json

secret_file = Path(__file__).parent / "secrets.json"
with secret_file.open("r") as fp:
    secrete_config = json.load(fp)

for key, val in secrete_config.items():
    os.environ[key] = val

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DB_USER.DB_NAME"] = os.getenv("DB_USER.DB_NAME")
app.config["DB_USER.PORT"] = os.getenv("DB_USER.PORT")
app.config["DB_USER.USER"] = os.getenv("DB_USER.USER")
app.config["DB_USER.PASSWORD"] = os.getenv("DB_USER.PASSWORD")

app.config["DB_DATA.DB_NAME"] = os.getenv("DB_DATA.DB_NAME")
app.config["DB_DATA.PORT"] = os.getenv("DB_DATA.PORT")
app.config["DB_DATA.USER"] = os.getenv("DB_DATA.USER")
app.config["DB_DATA.PASSWORD"] = os.getenv("DB_DATA.PASSWORD")
app.register_blueprint(frontend)
app.register_blueprint(api)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str):
    return User.get(user_id)


if __name__ == "__main__":
    db.init_app(app)
    login_manager.init_app(app)
    app.run(host="0.0.0.0", port=8000, debug=True)
