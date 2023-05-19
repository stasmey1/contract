from pathlib import Path

from app.models import Partner


def get_models_for_form(app, model):
    with app.app_context():
        return model.query.all()


def validate_file(file):
    if not Path(file.filename).suffix in ('.doc', '.docx', '.pdf'):
        raise ValueError('allowed_extensions: doc, docx, pdf')
    return file


def get_search_name_list(request) -> list:
    search_name = request.form.get('search_partner')
    partner_name_list = [i.name for i in Partner.query.all()]
    search_name_list = list()
    for partner_name in partner_name_list:
        name_list = [search_name,
                     search_name.capitalize(),
                     search_name.lower(),
                     search_name.upper()]
        for search_name in name_list:
            if search_name in partner_name:
                search_name_list.append(partner_name)

    return search_name_list
