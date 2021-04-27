import os
import sys
import requests

from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()


class BoostFetcher:
    BASE_URL = 'https://boostnote.io/api/'
    DOC_URI = 'docs'
    FOLDERS_URI = 'folders'

    def __init__(self, token, base_folder):
        self.token = token
        self._processed_docs = set()
        self._processed_folders = set()
        self.folder_cache = {}

        self.base_folder = Path(base_folder).absolute()

        self.session = requests.Session()
        self.session.headers['Authorization'] = f"Bearer {self.token}"

    def _fetch_folder_data(self, folder_id) -> dict:
        """
        Gets folder data from database
        """
        response = self.session.get(
            f"{self.BASE_URL}{self.FOLDERS_URI}/{folder_id}"
        )

        return response.json()['folder']

    def _fetch_doc_data(self, doc_id) -> dict:
        """
        Get document data from server
        """
        response = self.session.get(
            f"{self.BASE_URL}{self.DOC_URI}/{doc_id}"
        )

        return response.json()['doc']

    def _process_doc(self, doc_id: str, folder_path: Path):
        """
        Reads and save the document in a folder
        """
        doc = self._fetch_doc_data(doc_id)
        title = doc['head']['title']
        filename = folder_path / f"{slugify(title)}.md"

        print(F"Saving: {filename}")

        with filename.open('w') as f:
            f.write(doc['head']['content'])

        self._processed_docs.add(doc_id)

    def _get_folder(self, folder_id):
        """
        Returns a folder given it's id
        Looks of it in the cache first
        """
        if folder_id not in self.folder_cache:
            self.folder_cache[folder_id] = self._fetch_folder_data(folder_id)

        return self.folder_cache[folder_id]

    def _process_folder(self, folder_data: dict):
        """
        Navigate through a directory looking for its documents
        """
        pathname = folder_data['pathname']
        pathname = pathname[1:] if pathname.startswith('/') else pathname
        path = self.base_folder / pathname
        path.mkdir(parents=True, exist_ok=True)
        for doc_id in folder_data['childDocsIds']:
            if doc_id not in self._processed_docs:
                self._process_doc(doc_id, path)

        self._processed_folders.add(folder_data['id'])

        # Processing subfolders

        for folder_id in folder_data['childFoldersIds']:
            if folder_id not in self._processed_folders:
                self._process_folder(self._get_folder(folder_id))

    def fetch_folders(self) -> requests.Response:
        response = self.session.get(f"{self.BASE_URL}{self.FOLDERS_URI}")

        for folder in response.json()['folders']:
            if folder['id'] not in self._processed_folders:
                self._process_folder(folder)


if __name__ == '__main__':
    token = os.environ.get('BOOST_TOKEN')
    assert token, 'A token is required, please set it in your environment'
    if len(sys.argv) > 1:
        base_folder = sys.argv[1]
    else:
        base_folder = os.environ.get('BASE_DIR', './backup')
    fetcher = BoostFetcher(token, base_folder)
    fetcher.fetch_folders()
