import shutil
from pathlib import Path

from werkzeug.utils import secure_filename

from app.models import Contract, AdditionalAgreement


def validate_file(file):
    return Path(file.filename).suffix in ('.doc', '.docx', '.pdf')


class ContractDownloader:
    def __init__(self, instance):
        self.directory = 'contract_files'
        self.instance = instance

    def save(self, file):
        """check"""
        folder = Path(self.directory, self.instance.number)

        if validate_file(file):
            if not Path.exists(folder):
                folder.mkdir(parents=True, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(Path(folder, filename))

    def rename(self, file):
        new_name = f"{self.instance.number}{Path(file.filename).suffix}"
        Path(self.directory, self.instance.number, file.filename).rename(
            Path(self.directory, self.instance.number, new_name))
        """update file_path"""
        self.instance.file_path = new_name

    def save_and_rename(self, file):
        self.save(file)
        self.rename(file)

    def update_path(self, file):
        suffix = Path(file.filename).suffix
        self.instance.file_path = self.instance.number + suffix

    def delete(self):
        folder = Path(self.directory, self.instance.number)
        if Path.exists(folder):
            shutil.rmtree(folder)

    def get_data_for_download(self) -> tuple:
        directory = Path(Path(__file__).parent.parent,
                         self.directory,
                         self.instance.number)
        path = Path(self.instance.file_path)
        return directory, path


class AdditionalAgreementDownloader:
    def __init__(self, contract: Contract, additional_agreement: AdditionalAgreement):
        self.contract = contract
        self.additional_agreement = additional_agreement

        """check"""
        self.directory = Path('contract_files', contract.number)

    def save(self, file):
        filename = secure_filename(file.filename)
        file.save(Path(self.directory, filename))

    def rename(self, file):
        """rename file"""
        new_name = f"{self.contract.number}_dop_{self.additional_agreement.id}{Path(file.filename).suffix}"
        file = Path(self.directory, file.filename)
        file.rename(Path(self.directory, new_name))
        """update file_path"""
        self.additional_agreement.file_path = new_name

    def save_and_rename(self, file):
        self.save(file)
        self.rename(file)

    def delete(self):
        file = Path(self.directory, self.additional_agreement.file_path)
        if Path.exists(file):
            file.unlink()

    def get_data_for_download(self) -> tuple:
        directory = Path(Path(__file__).parent.parent, self.directory,)
        path = Path(self.additional_agreement.file_path)
        return directory, path
