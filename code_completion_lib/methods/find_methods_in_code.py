import re
import os

from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports

from code_completion_lib.necessary_functions import get_code, write_as_csv, read_json,find_imported_methods
from code_completion_lib.logger.logger import Logger


class Methods:
    libs: list = []

    def __init__(self):
        self.logger = Logger(__name__)

        self.libs.append([r"code_completion_lib\methods\libraries\numpy.json", 'numpy'])
        self.libs.append([r"code_completion_lib\methods\libraries\sklearn.json", 'sklearn'])
        self.libs.append([r"code_completion_lib\methods\libraries\collections.json", 'collections'])
        self.libs.append([r"code_completion_lib\methods\libraries\re.json", 're'])
        self.libs.append([r"code_completion_lib\methods\libraries\json.json", 'json'])
        self.libs.append([r"code_completion_lib\methods\libraries\datetime.json", 'datetime'])
        self.libs.append([r"code_completion_lib\methods\libraries\scipy.json", 'scipy'])
        self.libs.append([r"code_completion_lib\methods\libraries\warnings.json", 'warnings'])
        self.libs.append([r"code_completion_lib\methods\libraries\random.json", 'random'])
        self.libs.append([r"code_completion_lib\methods\libraries\matplotlib.pyplot.json", 'matplotlib.pyplot'])
        self.libs.append([r"code_completion_lib\methods\libraries\pandas.json", 'pandas'])
        self.libs.append([r"code_completion_lib\methods\libraries\os.json", 'os'])
        self.libs.append([r"code_completion_lib\methods\libraries\seaborn.json", 'seaborn'])
        self.libs.append([r"code_completion_lib\methods\libraries\time.json", 'time'])
        self.libs.append([r"code_completion_lib\methods\libraries\sys.json", 'sys'])
        self.libs.append([r"code_completion_lib\methods\libraries\requests.json", 'requests'])
        self.libs.append([r"code_completion_lib\methods\libraries\math.json", 'math'])
        self.libs.append([r"code_completion_lib\methods\libraries\IPython.json", 'IPython'])

    def _find_full_method_name(self, methods_json, arr=[], prefix=""):

        for key, value in methods_json.items():
            if type(value) == str:
                arr.append(f"{prefix}{key}")

            if type(value) == dict:
                arr.append(f"{prefix}{key}")
                prefix_old = prefix
                prefix += f"{key}."

                self._find_full_method_name(value, arr, prefix)
                prefix = prefix_old

        return arr

    def find_methods(self, data_path: str):

        result = []
        methods = []

        for lib in self.libs:
            methods = self._find_full_method_name(read_json(lib[0]), prefix=lib[1] + '.')

        write_as_csv([["varible_name", "method", "cluster"]], r'code_completion_lib\methods\methods.csv', 'w')

        completion = CodeCompletion()
        import_class = Imports(data_path)

        counter: int = 0
        written: bool = False

        for filename in os.listdir(data_path):
            written = False
            counter += 1

            full_path = os.path.join(data_path, filename)

            code = get_code(full_path)

            imports = import_class.find_imports(code, format='usage')
            imports_only_lib = import_class.find_imports(code, format='only_lib')
            imported_methods = find_imported_methods(methods, imports)

            for method in imported_methods.keys():
                reg_exp = re.findall(rf".+=\s*{method[1]}\(", code, flags=re.ASCII)
                reg_exp = [match.rstrip().replace(" ", "")[:-1].split("=", 1) for match in reg_exp]

                if len(reg_exp) != 0:
                    for exp in reg_exp:
                        exp[1] = method[0]
                        exp.append(completion.cluster_predict(imports_only_lib))

                    result.extend(reg_exp)

            if counter % 100 == 0:
                write_as_csv(result, r'code_completion_lib\methods\methods.csv', 'a')
                result = []
                written = True

        if not written:
            write_as_csv(result, r'code_completion_lib\methods\methods.csv', 'a')

        self.logger.info("Find methods ended.")
