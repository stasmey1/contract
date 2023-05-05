from enum import Enum
from pathlib import Path


def get_models_for_form(app, model):
    with app.app_context():
        return model.query.all()


def validate_file(file):
    if not Path(file.filename).suffix in ('.doc', '.docx', '.pdf'):
        raise ValueError('allowed_extensions: doc, docx, pdf')
    return file
