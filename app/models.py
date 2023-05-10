import datetime
import shutil
from enum import Enum
from pathlib import Path

from werkzeug.utils import secure_filename

from app import app, db


def get_my_company():
    with app.app_context():
        return MyCompany.query.filter_by(name='АО "СПЕЦАВТОБАЗА №1"').first()


class NDSRate(Enum):
    null = 0
    ten = 10
    twenty = 20


class CompanyMixin:
    id = db.Column(db.Integer, primary_key=True)
    avatar_file_path = db.Column(db.String(225), default='default_image.jpg')
    name = db.Column(db.String(225), nullable=False, unique=True)
    representative = db.Column(db.String(225))
    nds = db.Column(db.Boolean, default=True)
    nds_percent = db.Column(db.Integer, default=20)

    def __repr__(self):
        return self.name


class MyCompany(CompanyMixin, db.Model):
    pass


class Partner(CompanyMixin, db.Model):
    comment = db.Column(db.String(225))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    image_url = db.Column(db.String(225))

    def __repr__(self):
        return self.name


def validate_file(file):
    return Path(file.filename).suffix in ('.doc', '.docx', '.pdf')


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(225), nullable=False, unique=True)
    file_path = db.Column(db.String(225), nullable=False)
    data_start = db.Column(db.Date, nullable=False)
    data_finish = db.Column(db.Date, nullable=False)
    current_status = db.Column(db.Boolean, default=True)
    auto_renewal = db.Column(db.Boolean, default=True)
    tender = db.Column(db.Boolean, default=False)

    amount_money = db.Column(db.Float)
    waste_money = db.Column(db.Float)
    waste_money_percent = db.Column(db.Integer)

    nds = db.Column(db.Boolean, default=True)
    nds_percent = db.Column(db.Integer)
    nds_sum = db.Column(db.Float)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('contracts'))

    my_company_id = db.Column(db.Integer, db.ForeignKey('my_company.id'), default=get_my_company().id)
    my_company = db.relationship('MyCompany', backref=db.backref('contracts'))

    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    partner = db.relationship('Partner', backref=db.backref('contracts'))

    additional_agreements_exists = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(225))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.waste_money = self.amount_money
        self.waste_money_percent = 100
        if self.nds and self.nds_percent == 0:
            self.nds_percent = int(NDSRate.twenty.value)
        self.nds_sum = self.amount_money * self.nds_percent / 100 if self.nds else 0

    def __repr__(self):
        return self.id

    def get_waste_money(self, money: float) -> float:
        '''получить количество НЕотработанных денег'''
        return self.amount_money - money

    def get_percentage(self) -> int:
        '''получить процент отработки в деньгах'''
        return 100 - int((self.waste_money / self.amount_money) * 100)

    def make_transaction(self, transaction):
        '''транзакция'''
        if self.waste_money - transaction.amount_money >= 0:
            self.waste_money -= transaction.amount_money
            transaction.done = True
        else:
            raise ValueError('Transactions exceeds the remaining money under the contract')

    def delete_transaction(self, transaction):
        self.waste_money += transaction.amount_money

    def get_remaining_duration(self) -> int:
        '''получить продолжительность контаркта в днях'''
        delta = self.data_finish - self.data_start
        return delta.days

    def get_current_duration(self) -> int:
        '''получить количество пройденых дней контракта'''
        return (datetime.date.today() - self.data_start).days

    def get_duration_percent(self) -> int:
        '''получить процент завершенности продолжительности контракта'''
        duration_percent = int(self.get_current_duration() / self.get_remaining_duration() * 100)
        return duration_percent if duration_percent <= 100 else 100

    def update_fields(self):
        self.current_status = True if self.data_finish > datetime.date.today() else False
        self.additional_agreements_exists = False if not self.additional_agreements else True

    def save_contract_file(self, file):
        folder = Path('contract_files', self.number)
        if validate_file(file):
            if not Path.exists(folder):
                folder.mkdir(parents=True, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(Path(folder, filename))

            new_name = f"{self.number}{Path(filename).suffix}"
            Path(folder, filename).rename(Path(folder, new_name))

            self.file_path = new_name

    def update_file_path(self, file):
        suffix = Path(file.filename).suffix
        self.file_path = self.number + suffix

    def delete_contract_file(self):
        folder = Path('contract_files', self.number)
        if Path.exists(folder):
            shutil.rmtree(folder)


class TransactionMoney(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    justification = db.Column(db.String(225))
    moment_of_payment = db.Column(db.DateTime, default=datetime.datetime.now().strftime("%d.%m.%Y, %H:%M"),
                                  nullable=False)
    amount_money = db.Column(db.Float, nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    transactions = db.relationship('Contract', backref=db.backref('transactions', cascade="all, delete"))
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'{self.data} - {self.amount_money}'


class AdditionalAgreement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.date.today(), nullable=False)
    file_path = db.Column(db.String(225), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    additional_agreement = db.relationship('Contract',
                                           backref=db.backref('additional_agreements',
                                                              cascade='all, delete'))
    comment = db.Column(db.String(225))

    def __repr__(self):
        return self.id

    def save_file(self, file):
        contract = Contract.query.get(self.contract_id)
        directory = Path('contract_files', contract.number)
        filename = secure_filename(file.filename)
        file.save(Path(directory, filename))
        """rename file"""
        new_name = f"{contract.number}_dop_{self.id}{Path(filename).suffix}"
        new_file = Path(directory, filename)
        new_file.rename(Path(directory, new_name))
        """update file_path"""
        self.file_path = new_name

    def delete_file(self):
        contract = Contract.query.get(self.contract_id)
        directory = Path(Path(__file__).parent.parent, 'contract_files', contract.number)
        file = Path(directory, self.file_path)
        if Path.exists(file):
            file.unlink()
