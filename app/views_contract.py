from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required
from sqlalchemy import text

from app import app, db
from app.forms import ContractAdd, TransactionMoneyForm, ContractEditInfo, ContractEditFile, AdditionalAgreementForm
from app.models import Partner, Category, Contract, TransactionMoney, AdditionalAgreement
from .download_config import ContractDownloader, AdditionalAgreementDownloader
from .template_utils import template_bool_color


@app.route('/contract_list')
def contract_list():
    return render_template('contract/contract_list.html',
                           contract_list=Contract.query.order_by(text('data_start DESC')).
                           filter_by(current_status=True).all())


@app.route('/contract_archive_list')
def contract_archive_list():
    return render_template('contract/contract_list.html',
                           contract_list=Contract.query.order_by(text('data_start DESC')).
                           filter_by(current_status=False).all())


@app.route('/contract_add', methods=['POST', 'GET'])
@login_required
def contract_add():
    form = ContractAdd()
    if form.validate_on_submit():
        file = form.file_path.data
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
        downloader = ContractDownloader(contract)
        downloader.save_and_rename(file)

        db.session.add(contract)
        db.session.commit()
        return redirect(url_for('contract', id=contract.id))

    return render_template('contract/contract_add.html', form=form)


@app.route('/contract_edit/<id>', methods=['POST', 'GET'])
@login_required
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


@app.route('/contract_check/<id>')
def contract_check(id):
    contract = Contract.query.get(id)
    contract.update_fields()
    db.session.add(contract)
    db.session.commit()
    return redirect(url_for('contract', id=contract.id))


@app.route('/contract_edit_file/<id>', methods=['POST', 'GET'])
@login_required
def contract_edit_file(id):
    contract = Contract.query.get(id)
    downloader = ContractDownloader(contract)
    form = ContractEditFile()

    if form.validate_on_submit():
        new_file = form.file_path.data
        downloader.delete()
        downloader.save_and_rename(new_file)
        downloader.update_path(new_file)

        db.session.add(contract)
        db.session.commit()

        return redirect(url_for('contract', id=contract.id))

    return render_template('contract/contract_edit_file.html', form=form)


@app.route('/contract_delete/<id>', methods=['POST', 'GET'])
@login_required
def contract_delete(id):
    contract = Contract.query.get(id)
    downloader = ContractDownloader(contract)

    if request.method == "POST":
        downloader.delete()

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
                           transaction_list=transaction_list,
                           template_bool_color=template_bool_color)


@app.route('/download_file/<number>')
def download_contract_file(number):
    contract = Contract.query.filter_by(number=number).first()
    downloader = ContractDownloader(contract)
    directory = downloader.get_data_for_download()[0]
    path = downloader.get_data_for_download()[1]
    return send_from_directory(directory=directory, path=path, as_attachment=True)


@app.route('/contract/<id>/add_transaction', methods=['POST', ])
@login_required
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


@app.route('/contract/<id>/delete_transaction/<trans_id>')
@login_required
def delete_transaction(id, trans_id):
    contract = Contract.query.get(id)
    transaction = TransactionMoney.query.get(trans_id)
    contract.delete_transaction(transaction)
    db.session.delete(transaction)
    db.session.add(contract)
    db.session.commit()
    return redirect(url_for('contract', id=contract.id))


@app.route('/<contract_id>/additional_agreement_add', methods=['POST', 'GET'])
@login_required
def additional_agreement_add(contract_id):
    form = AdditionalAgreementForm()
    contract = Contract.query.get(contract_id)
    if form.validate_on_submit():
        file = form.file_path.data
        additional_agreement = AdditionalAgreement(file_path=file.filename,
                                                   data=form.data.data,
                                                   contract_id=Contract.query.get(contract_id).id,
                                                   comment=form.comment.data)
        db.session.add(additional_agreement)
        db.session.commit()
        """save file"""
        downloader = AdditionalAgreementDownloader(contract, additional_agreement)
        downloader.save_and_rename(file)
        """update contract"""
        contract.additional_agreements_exists = True

        db.session.add(additional_agreement, contract)
        db.session.commit()
        return redirect(url_for('contract', id=contract_id))

    return render_template('contract/additional_agreement_add.html', form=form)


@app.route('/<contract_id>/additional_agreement_delete/<id>', methods=['POST', 'GET'])
@login_required
def additional_agreement_delete(contract_id, id):
    contract = Contract.query.get(contract_id)
    additional_agreement = AdditionalAgreement.query.get(id)
    downloader = AdditionalAgreementDownloader(contract, additional_agreement)

    if request.method == "POST":
        downloader.delete()
        db.session.delete(additional_agreement)
        db.session.commit()

        contract.update_fields()
        db.session.add(contract)
        db.session.commit()

        return redirect(url_for('contract', id=contract_id))

    return render_template('contract/contract_delete.html')


@app.route('/<contract_id>/download_additional_agreement_file/<id>')
def download_additional_agreement_file(contract_id, id):
    additional_agreement = AdditionalAgreement.query.get(id)
    contract = Contract.query.get(contract_id)
    try:
        downloader = AdditionalAgreementDownloader(contract, additional_agreement)
        directory = downloader.get_data_for_download()[0]
        path = downloader.get_data_for_download()[1]
        return send_from_directory(directory=directory, path=path, as_attachment=True)
    except:
        return 'Файл не найден'