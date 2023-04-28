import datetime

from flask import render_template, redirect, url_for
from sqlalchemy import text, Transaction

from app import app, db
from app.forms import ContractAdd, TransactionMoneyForm
from app.models import Partner, Category, Contract, TransactionMoney


@app.route('/contract_list')
def contract_list():
    return render_template('contract/contract_list.html',
                           contract_list=Contract.query.order_by(text('data_start DESC')).all())


@app.route('/contract_add', methods=['POST', 'GET'])
def contract_add():
    form = ContractAdd()
    if form.validate_on_submit():
        contract = Contract(number=form.number.data,
                            file_path=form.file_path.data.filename,
                            data_start=form.data_start.data,
                            data_finish=form.data_finish.data,
                            auto_renewal=form.auto_renewal.data,
                            tender=form.tender.data,
                            amount_money=form.amount_money.data,
                            nds=form.nds.data,
                            nds_percent=int(form.nds_percent.data),
                            category_id=Category.query.filter_by(name=form.category_id.data).first().id,
                            partner_id=Partner.query.filter_by(name=form.partner_id.data).first().id,
                            comment=form.comment.data)
        db.session.add(contract)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('contract/contract_add.html', form=form)


@app.route('/contract/<id>')
def contract(id):
    contract = Contract.query.get(id)
    transaction_list = TransactionMoney.query.filter_by(contract_id=contract.id).order_by(text('moment_of_payment DESC')).all()
    return render_template('contract/contract.html',
                           contract=contract,
                           form=TransactionMoneyForm(),
                           transaction_list=transaction_list)


@app.route('/contract/<id>/add_transaction', methods=['POST', ])
def add_transaction(id):
    contract = Contract.query.get(id)
    form = TransactionMoneyForm()
    if form.validate_on_submit():
        transaction = TransactionMoney(justification=form.justification.data,
                                       amount_money=form.amount_money.data,
                                       contract_id=contract.id)
        try:
            contract.make_transaction(transaction)
            db.session.add(transaction)
            db.session.add(contract)
            db.session.commit()
        except ValueError:
            form.errors['transaction_error'] = 'contract amount exceeded'

    return redirect(url_for('contract', id=contract.id))
