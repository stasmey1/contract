from pathlib import Path

from flask import render_template, redirect, url_for, request, send_from_directory
from sqlalchemy import text

from app import app, db
from app.forms import ContractAdd, TransactionMoneyForm, ContractEditInfo, ContractEditFile, AdditionalAgreementForm
from app.models import Partner, Category, Contract, TransactionMoney, AdditionalAgreement
from .utils import validate_file


@app.route('/contract_list')
def contract_list():
    return render_template('contract/contract_list.html',
                           contract_list=Contract.query.order_by(text('data_start DESC')).all())


@app.route('/contract_add', methods=['POST', 'GET'])
def contract_add():
    form = ContractAdd()
    if form.validate_on_submit():
        file = validate_file(form.file_path.data)
        contract = Contract(number=form.number.data,
                            file_path=file.filename,
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
        contract.save_contract_file(file)
        db.session.add(contract)
        db.session.commit()
        return redirect(url_for('contract', id=contract.id))

    return render_template('contract/contract_add.html', form=form)


@app.route('/contract_edit/<id>', methods=['POST', 'GET'])
def contract_edit(id):
    contract = Contract.query.get(id)
    form = ContractEditInfo(
        number=contract.number,
        data_start=contract.data_start,
        data_finish=contract.data_finish,
        auto_renewal=contract.auto_renewal,
        tender=contract.tender,
        amount_money=contract.amount_money,
        nds=contract.nds,
        nds_percent=contract.nds_percent,
        comment=contract.comment
    )
    if form.validate_on_submit():
        contract.number = form.number.data
        contract.data_start = form.data_start.data
        contract.data_finish = form.data_finish.data
        contract.tender = form.tender.data
        contract.amount_money = form.amount_money.data
        contract.nds = form.nds.data
        contract.nds_percent = int(form.nds_percent.data)
        contract.comment = form.comment.data

        db.session.add(contract)
        db.session.commit()

        return redirect(url_for('contract', id=contract.id))

    return render_template('contract/contract_edit.html', form=form)


@app.route('/contract_edit_file/<id>', methods=['POST', 'GET'])
def contract_edit_file(id):
    contract = Contract.query.get(id)
    form = ContractEditFile()
    if form.validate_on_submit():
        new_file = form.file_path.data
        contract.delete_contract_file()
        contract.save_contract_file(new_file)
        contract.update_file_path(new_file)
        db.session.add(contract)
        db.session.commit()
        return redirect(url_for('contract', id=contract.id))

    return render_template('contract/contract_edit_file.html', form=form)


@app.route('/contract_delete/<id>', methods=['POST', 'GET'])
def contract_delete(id):
    contract = Contract.query.get(id)
    if request.method == "POST":
        contract.delete_contract_file()
        db.session.delete(contract)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('contract/contract_delete.html')


@app.route('/contract/<id>')
def contract(id):
    contract = Contract.query.get(id)
    transaction_list = TransactionMoney.query.filter_by(contract_id=contract.id).order_by(
        text('moment_of_payment DESC')).all()
    return render_template('contract/contract.html',
                           contract=contract,
                           form=TransactionMoneyForm(),
                           transaction_list=transaction_list)


@app.route('/download_file/<number>')
def download_file(number):
    contract = Contract.query.filter_by(number=number).first()
    directory = Path(Path(__file__).parent.parent, 'contract_files', contract.number)
    path = Path(contract.file_path)
    return send_from_directory(directory=directory, path=path, as_attachment=True)


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
            return redirect(request.url)

    return redirect(url_for('contract', id=contract.id))


@app.route('/<contract_id>/additional_agreement_add', methods=['POST', 'GET'])
def additional_agreement_add(contract_id):
    form = AdditionalAgreementForm()
    if form.validate_on_submit():
        file = validate_file(form.file_path.data)
        additional_agreement = AdditionalAgreement(file_path=file.filename,
                                                   data=form.data.data,
                                                   contract_id=Contract.query.get(contract_id).id,
                                                   comment=form.comment.data)

        db.session.add(additional_agreement)
        db.session.commit()
        """save file"""
        additional_agreement.save_file(file)

        db.session.add(additional_agreement)
        db.session.commit()
        return redirect(url_for('contract', id=contract_id))

    return render_template('contract/additional_agreement_add.html', form=form)


@app.route('/<contract_id>/additional_agreement_delete/<id>', methods=['POST', 'GET'])
def additional_agreement_delete(contract_id, id):
    if request.method == "POST":
        additional_agreement = AdditionalAgreement.query.get(id)
        additional_agreement.delete_file()
        db.session.delete(additional_agreement)
        db.session.commit()
        return redirect(url_for('contract', id=contract_id))

    return render_template('contract/contract_delete.html')


@app.route('/<contract_id>/download_additional_agreement_file/<id>')
def download_additional_agreement_file(contract_id,id):
    additional_agreement = AdditionalAgreement.query.get(id)
    contract = Contract.query.get(contract_id)
    directory = Path(Path(__file__).parent.parent, 'contract_files', contract.number)
    path = Path(additional_agreement.file_path)
    return send_from_directory(directory=directory, path=path, as_attachment=True)
