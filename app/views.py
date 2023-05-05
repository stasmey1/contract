from app import app, db
from flask import (
    render_template,
    redirect,
    url_for,
)

from .forms import PartnerForm, CategoryForm
from .models import Partner, Category


@app.route('/')
def index():
    return render_template('index.html', category_list=Category.query.all())


@app.route('/category_form', methods=['POST', 'GET'])
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
    return render_template('category/category.html', category=Category.query.get(id))


@app.route('/partner_form', methods=['POST', 'GET'])
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
    return render_template('partner/partner.html', partner=Partner.query.get(id))
