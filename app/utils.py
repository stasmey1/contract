from enum import Enum





def get_models_for_form(app, model):
    with app.app_context():
        return model.query.all()