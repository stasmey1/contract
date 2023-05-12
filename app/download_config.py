import shutil
from pathlib import Path

from werkzeug.utils import secure_filename

from app.models import Contract, AdditionalAgreement


class FileMixin:
    def __init__(self):
        self.directory = Path('contract_files')

    @staticmethod
    def validate_file(file):
        return Path(file.filename).suffix in ('.doc', '.docx', '.pdf')

    def get_data_for_download(self, contract: Contract, additional_agreement: AdditionalAgreement = None) -> tuple:
        contract = Contract.query.filter_by(number=contract.number).first()
        directory = Path(Path(__file__).parent.parent, self.directory, contract.number)

        if additional_agreement is not None:
            path = Path(additional_agreement.file_path)
        else:
            path = Path(contract.file_path)

        return directory, path


class ContractFile(FileMixin):
    def __init__(self):
        super().__init__()

    def save(self, contract: Contract, file):
        folder = Path(self.directory, contract.number)
        if self.validate_file(file):
            if not Path.exists(folder):
                folder.mkdir(parents=True, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(Path(folder, filename))

    def rename(self, contract: Contract, file):
        new_name = f"{contract.number}{Path(file.filename).suffix}"
        Path(self.directory, contract.number, file.filename).rename(Path(self.directory, contract.number, new_name))
        """update file_path"""
        contract.file_path = new_name

    def save_and_rename(self, contract: Contract, file):
        self.save(contract, file)
        self.rename(contract, file)

    @staticmethod
    def update_path(contract: Contract, file):
        suffix = Path(file.filename).suffix
        contract.file_path = contract.number + suffix

    def delete(self, contract: Contract):
        folder = Path(self.directory, contract.number)
        if Path.exists(folder):
            shutil.rmtree(folder)


class AdditionalAgreementFile(FileMixin):
    def __init__(self, contract: Contract):
        super().__init__()
        self.contract = contract.query.get(contract.id)
        self.directory = Path(self.directory, contract.number)

    def save(self, file):
        filename = secure_filename(file.filename)
        file.save(Path(self.directory, filename))

    def rename(self, additional_agreement: AdditionalAgreement, file):
        """rename file"""
        new_name = f"{self.contract.number}_dop_{additional_agreement.id}{Path(file.filename).suffix}"
        new_file = Path(self.directory, file.filename)
        new_file.rename(Path(self.directory, new_name))
        """update file_path"""
        additional_agreement.file_path = new_name

    def save_and_rename(self, additional_agreement: AdditionalAgreement, file):
        self.save(file)
        self.rename(additional_agreement, file)

    def delete(self, additional_agreement: AdditionalAgreement):
        file = Path(self.directory, additional_agreement.file_path)
        if Path.exists(file):
            file.unlink()
