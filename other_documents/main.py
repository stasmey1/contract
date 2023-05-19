from flask import Blueprint, request, send_from_directory
from flask import render_template, redirect, url_for
from flask_login import login_required

from app import db
from other_documents.download_config import OtherDocumentDownloader
from other_documents.forms import OtherDocumentForm
from other_documents.models import OtherDocument

other_documents = Blueprint('other_documents', __name__, static_folder='static', template_folder='templates')


@other_documents.route('/')
def other_document_list():
    other_document_list = OtherDocument.query.all()
    return render_template('other_documents/other_document_list.html',
                           other_document_list=other_document_list)


@other_documents.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    form = OtherDocumentForm()
    if form.validate_on_submit():
        file = form.file_path.data
        other_document = OtherDocument(name=form.name.data,
                                       file_path=file.filename,
                                       comment=form.comment.data)

        db.session.add(other_document)
        db.session.commit()

        downloader = OtherDocumentDownloader(other_document)
        downloader.save_and_rename(file)

        db.session.add(other_document)
        db.session.commit()

        return redirect(url_for('other_documents.other_document_list'))

    return render_template('other_documents/add.html', form=form)


@other_documents.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    other_document = OtherDocument.query.get(id)

    if request.method == "POST":
        downloader = OtherDocumentDownloader(other_document)
        downloader.delete()

        db.session.delete(other_document)
        db.session.commit()

        return redirect(url_for('other_documents.other_document_list'))

    return render_template('other_documents/delete.html')


@other_documents.route('/download/<id>')
def download(id):
    other_document = OtherDocument.query.get(id)
    downloader = OtherDocumentDownloader(other_document)
    directory, path = downloader.get_data_for_download()[0], downloader.get_data_for_download()[1]
    return send_from_directory(directory=directory, path=path, as_attachment=True)
