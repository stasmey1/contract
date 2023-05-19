from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    FileField
)
from wtforms.validators import DataRequired, Length


class OtherDocumentForm(FlaskForm):
    name = StringField('Наименование', validators=[DataRequired(), ])
    file_path = FileField('Файл', validators=[DataRequired(), ])
    comment = StringField('Комментарий', validators=[Length(min=5, message='минимум 5 символов')])
    submit = SubmitField('Отправить')
