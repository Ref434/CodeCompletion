import os
import re
import json
from code_completion_lib.logger.logger import Logger

class Parser:

    # Dict {language: frequency}
    languages: dict = {}

    parse_from: str = None
    parse_to: str = None

    num_files: int = 0

    def __init__(self, parse_from: str, parse_to: str):
        self.logger = Logger(__name__)

        self.parse_from = parse_from
        self.parse_to = parse_to
        self.num_files = sum(os.path.isfile(os.path.join(self.parse_from, f)) for f in os.listdir(self.parse_from))

    def _get_notebook(self, notebook_path: str):
        with open(notebook_path, 'r', encoding='utf-8') as notebook:
            try:
                return json.load(notebook, strict=False)
            except:
                return None

    def _save_as_txt_file(self, filename: str, code: str):
        with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
            f.write(code)

    def _get_source_from_code_cell(self, cell):
        return ''.join(cell['source'])

    def _get_cells_content(self, notebook_cells):
        yield from (
            ("code.txt", self._get_source_from_code_cell(current_cell))
            for i, current_cell in enumerate(notebook_cells, 1)
            if current_cell['cell_type'] == "code"
        )

    def _save_languages(self, languages: dict):
        with open(r"analysis\jupyters\languages.json", "w") as write_file:
            json.dump(languages, write_file, indent=4)

    def check_language(self):
        failed: int = 0

        for filename in os.listdir(self.parse_from):
            full_path: str = os.path.join(self.parse_from, filename)

            try:
                notebook = self._get_notebook(full_path)

                if notebook['metadata']['kernelspec']['language'] in self.languages:
                    self.languages[notebook['metadata']['kernelspec']['language']] += 1
                else:
                    self.languages[notebook['metadata']['kernelspec']['language']] = 1
            except Exception:
                failed += 1

        try:
            self.logger.info(f"{failed / self.num_files * 100}% failed in check_language func")
        except ZeroDivisionError:
            self.logger.error("ZeroDivisionError")
        self._save_languages(self.languages)

    def parse(self):
        failed: int = 0

        for filename in os.listdir(self.parse_from):
            if filename.endswith(".ipynb"):
                try:
                    full_path: str = os.path.join(self.parse_from, filename)
                    full_code: str = ""

                    notebook = self._get_notebook(full_path)

                    # Passing not python notebooks
                    if not notebook['metadata']['kernelspec']['language'].startswith("python"):
                        continue

                    for name, code in self._get_cells_content(notebook['cells']):
                        full_code += "\n" + code

                    # Deleting comments from code
                    full_code = re.sub(r"#.+\n", "", full_code)

                    self._save_as_txt_file(os.path.join(self.parse_to, filename.replace(".ipynb", "")), full_code)
                except Exception:
                    failed += 1

        try:
            self.logger.info(f"{failed / self.num_files * 100}% failed in parse func")
        except ZeroDivisionError:
            self.logger.error("ZeroDivisionError")
        self._save_languages(self.languages)
