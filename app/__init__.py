from flask import Flask
from flask_login import LoginManager

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.Config')

"""register blueprints"""

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)


from other_documents.main import other_documents
app.register_blueprint(other_documents, url_prefix='/other_documents')

from auth.main import auth
app.register_blueprint(auth, url_prefix='/auth')


from . import views, views_contract, models, forms
from other_documents import models
from auth import models
