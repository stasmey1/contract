from flask import Flask

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# create app
app = Flask(__name__)
app.config.from_object('config.Config')

# init_utils
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# imports
from . import views
from . import views_contract
from . import models
from . import forms
from . import constants

