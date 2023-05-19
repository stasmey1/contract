from flask_login import login_required

from app import app, db
from flask import render_template, redirect, url_for, request, flash

from .forms import PartnerForm, CategoryForm
from .models import Partner, Category, Contract
from .utils import get_search_name_list


@app.post('/search')
def search():
    partner_name_list = get_search_name_list(request)
    search_partner = db.session.query(Partner).filter(Partner.name.in_(partner_name_list)).first()
    contract_list = Contract.query.filter_by(partner=search_partner).all()

    if not contract_list:
        flash('Контрагент не найден')
        return redirect(url_for('index'))

    return render_template('contract/contract_list.html', contract_list=contract_list)


@app.route('/')
def index():
    return render_template('index.html', category_list=Category.query.all())


@app.route('/category_form', methods=['POST', 'GET'])
@login_required
def category_form():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('category/category_form.html', form=form)


@app.route('/category_list')
def category_list():
    return render_template('category/category_list.html', category_list=Category.query.all())


@app.route('/category/<id>')
def category(id):
    category = Category.query.get(id)
    contract_list = Contract.query.filter_by(category=category).all()
    return render_template('contract/contract_list.html', contract_list=contract_list)


@app.route('/partner_form', methods=['POST', 'GET'])
@login_required
def partner_form():
    form = PartnerForm()
    if form.validate_on_submit():
        partner = Partner(name=form.name.data,
                          representative=form.representative.data,
                          nds=form.nds.data,
                          nds_percent=form.nds_percent.data,
                          comment=form.comment.data)
        if partner.nds and partner.nds_percent == 0:
            partner.nds_percent = 20
        db.session.add(partner)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('partner/partner_form.html', form=form)


@app.route('/partner/<id>')
def partner(id):
    partner = Partner.query.get(id)
    contract_list = Contract.query.filter_by(partner=partner).all()
    return render_template('contract/contract_list.html', contract_list=contract_list)


@app.route('/partner_list')
def partner_list():
    return render_template('partner/partner_list.html', partner_list=Partner.query.all())
