from app import app
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    BooleanField,
    FileField,
    DateField, FloatField, IntegerField, DateTimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length, ValidationError,
)

from .constants import NDSRate
from .models import Category, Partner
from .utils import get_models_for_form


class PartnerForm(FlaskForm):
    name = StringField('Наименование', validators=[DataRequired(), ])
    representative = StringField('Представитель', validators=[DataRequired(), ])
    nds = BooleanField('НДС', default=True)
    nds_percent = SelectField('Ставка НДС', choices=[_.value for _ in NDSRate])
    avatar_file_path = FileField('Аватар')
    comment = StringField('Комментарий')
    submit = SubmitField('Отправить')


class CategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), ])
    submit = SubmitField('Отправить')


class ContractFormMixin(FlaskForm):
    number = StringField('Номер', validators=[DataRequired(), ])
    data_start = DateField('Дата начала', validators=[DataRequired(), ])
    data_finish = DateField('Дата окончания', validators=[DataRequired(), ])
    auto_renewal = BooleanField('Автопродление')
    tender = BooleanField('Тендерный')
    amount_money = FloatField('Сумма договора')
    nds = BooleanField('НДС')
    nds_percent = SelectField('Ставка НДС',
                              choices=[_.value for _ in NDSRate])
    comment = StringField('Комментарий')

    submit = SubmitField('Отправить')


class ContractAdd(ContractFormMixin):
    category_id = SelectField('Категория',
                              choices=[_.name for _ in get_models_for_form(app, Category)],
                              validators=[DataRequired(), ])
    partner_id = SelectField('Контрагент',
                             choices=[_.name for _ in get_models_for_form(app, Partner)],
                             validators=[DataRequired(), ])
    file_path = FileField('Файл', validators=[DataRequired(), ])


class ContractEditInfo(ContractFormMixin):
    pass


class ContractEditFile(FlaskForm):
    file_path = FileField('Файл', validators=[DataRequired(), ])
    submit = SubmitField('Отправить')


class TransactionMoneyForm(FlaskForm):
    justification = StringField('Обоснование')
    amount_money = FloatField('Сумма', validators=[DataRequired(), ])
    submit = SubmitField('Отправить')


class AdditionalAgreementForm(FlaskForm):
    file_path = FileField('Файл', validators=[DataRequired(), ])
    data = DateField('Дата')
    comment = StringField('Комментарий')
    submit = SubmitField('Отправить')
