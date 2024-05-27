from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Development


app = Flask(__name__)
app.config.from_object(Development)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .views import home
from .mod_users import users
from .mod_posts import posts

app.register_blueprint(users)
app.register_blueprint(posts)
