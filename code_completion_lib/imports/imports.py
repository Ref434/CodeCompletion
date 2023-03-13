import re
import os
from code_completion_lib.necessary_functions import write_as_csv
import pandas as pd


class Imports:

    path: str = None

    def __init__(self, path: str):
        self.path = path

    def _line_processing(self, line: list, format: str = 'default'):
        imports: list = []

        if format == 'only_lib':
            if len(line) > 1:
                if line[0] == "import":
                    for index in range(1, len(line)):
                        imports.append(line[index].split(".", 1)[0])

                if line[0] == "from":
                    imports.append(line[1].split(".", 1)[0])

        if format == 'default':
            if line[0] == "import":
                for index in range(1, len(line)):
                    imports.append(line[index])

            if line[0] == "from":
                tmp = line[1]
                for index in range(3, len(line)):
                    imports.append(f"{tmp}.{line[index]}")\

        if format == 'usage':
            if len(line) > 3:
                if line[2] == 'as':
                    return [[line[1], line[2], line[3]]]

            if line[0] == "import":
                for index in range(1, len(line)):
                    imports.append([line[index]])

            elif line[0] == "from":
                tmp = line[1]
                for index in range(3, len(line)):
                    imports.append([tmp, line[index]])



        return imports

    def find_imports(self, code: str, format: str = 'default'):
        imports: list = []

        if format == 'only_lib':
            reg_exp = re.findall(r"^\bimport\s\S+|^\bfrom\s\S+\simport", code, flags=re.ASCII and re.MULTILINE)
        if format == 'default':
            reg_exp = re.findall(r"\bimport\s+\S+|\bfrom\s+\S+\s+import\s+[^,\s]+(?:\s*,\s*[^,\s]+)*", code, flags=re.ASCII)
        if format == 'usage':
            reg_exp = re.findall(r"\bimport\s+\S+\s+as\s+\S+|\bimport\s+\S+|\bfrom\s+\S+\s+import\s+[^,\s]+(?:\s*,\s*[^,\s]+)*", code, flags=re.ASCII)

        reg_exp = [match.rstrip().replace(",", " ").replace(";", " ").split(" ") for match in reg_exp]

        for match in reg_exp:
            for word in match:
                if word == "":
                    match.remove(word)
            imports.extend(self._line_processing(match, format))

        return imports


    def process(self):

        # List of imports for each notebook [[imports for first notebook][imports for second notebook]...]
        all_imports: list = []

        # List for saving as csv
        csv_imports: list = []

        i: int = 0

        # Dict(i:notebook name)
        notebook_name: dict = {}

        for filename in os.listdir(self.path):

            full_path: str = os.path.join(self.path, filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                code = file.read()

            imports_one_file = self.find_imports(code, format='only_lib')

            if len(imports_one_file) != 0:
                notebook_name[i] = filename
                i += 1
                imports_sorted = []
                [imports_sorted.append(element) for element in imports_one_file if element not in imports_sorted]
                all_imports.append(imports_sorted)

        imports_without_repetitions = []
        for notebook in all_imports:
            [imports_without_repetitions.append(element) for element in notebook if element not in imports_without_repetitions
             and isinstance(element, str)]

        imports_without_repetitions.insert(0, 'filename')
        csv_imports.append(imports_without_repetitions)

        for i in range(len(all_imports)):
            # Adding notebook name
            tmp = [notebook_name[i]]

            # Made vector of imports
            for element in imports_without_repetitions:
                if element == 'filename':
                    continue
                if all_imports[i].count(element) != 0:
                    tmp.append(1)
                else:
                    tmp.append(0)

            csv_imports.append(tmp)

        write_as_csv(csv_imports, r'code_completion_lib\imports\imports.csv', 'w')

        df = pd.read_csv(r'code_completion_lib\imports\imports.csv')
        tmp = df.iloc[:, 1:]
        df = df.drop(columns=tmp.columns[tmp.sum() <= 40])
        df = df.loc[~(df.iloc[:, 1:] == 0).all(axis=1)]
        df.to_csv(r'code_completion_lib\imports\preprocessing_imports.csv')

        print("Find imports ended.")
