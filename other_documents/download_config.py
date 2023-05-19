from pathlib import Path

from werkzeug.utils import secure_filename

from other_documents.models import OtherDocument


def validate_file(file):
    return Path(file.filename).suffix in ('.doc', '.docx', '.pdf')


class OtherDocumentDownloader:
    def __init__(self, instance: OtherDocument):
        self.directory = Path('other_document_files')
        self.instance = instance

    def save(self, file):
        if validate_file(file):
            if not Path.exists(self.directory):
                self.directory.mkdir(parents=True, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(Path(self.directory, filename))

    def rename(self, file):
        new_name = f"{self.instance.id}-{self.instance.name}{Path(file.filename).suffix}"
        Path(self.directory, file.filename).rename(Path(self.directory, new_name))
        """update file_path"""
        self.instance.file_path = new_name

    def save_and_rename(self, file):
        self.save(file)
        self.rename(file)

    def delete(self):
        file = Path(self.directory, self.instance.file_path)
        if Path.exists(file):
            file.unlink()

    def get_data_for_download(self) -> tuple:
        """check"""
        directory = Path(Path(__file__).parent.parent, self.directory)

        path = Path(self.instance.file_path)
        print(directory)
        print(path)
        return directory, path
