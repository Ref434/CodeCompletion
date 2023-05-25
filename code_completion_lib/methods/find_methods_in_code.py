import re
import os

from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports

from code_completion_lib.necessary_functions import get_code, write_as_csv, read_json, find_imported_methods
from code_completion_lib.logger.logger import Logger
import time


class Methods:
    libs: list = []

    def __init__(self, path: str, size: str, logger):
        self.logger = logger
        self.logger.set_name(__name__)

        self.size = size
        self.path = path

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

    def find_methods(self, model_path):
        self.logger.info(f"size = {self.size}")
        start_time = time.time()

        result = []
        methods = []
        models = os.listdir(model_path)

        for lib in self.libs:
            methods = self._find_full_method_name(read_json(lib[0]), prefix=lib[1] + '.')

        length = len(models)
        labels = ["varible_name", "method"]

        for index in range(length):
            labels.append(models[index])

        write_as_csv([labels], rf'code_completion_lib\methods\models\{self.size}\data.csv', 'w')

        completion = CodeCompletion(self.size, self.logger)
        import_class = Imports(self.path, self.size, self.logger)

        counter: int = 0
        written: bool = False

        for filename in os.listdir(self.path):
            written = False
            counter += 1

            full_path = os.path.join(self.path, filename)

            code = get_code(full_path)

            imports = import_class.find_imports(code, format='usage')
            imports_only_lib = import_class.find_imports(code, format='only_lib')
            imported_methods = find_imported_methods(methods, imports)

            for method in imported_methods.keys():
                reg_exp = re.findall(rf".+=\s*{method[1]}\(", code, flags=re.ASCII)
                reg_exp = [match.rstrip().replace(" ", "")[:-1].split("=", 1) for match in reg_exp]

                if len(reg_exp) != 0:
                    expr_full = []
                    for exp in reg_exp:
                        expr = [exp[0], method[0]]
                        for index in range(length):
                            expr.append(completion.cluster_predict(imports_only_lib, models[index]))
                        expr_full.append(expr)

                    result.extend(expr_full)

            if counter % 5 == 0:
                write_as_csv(result, rf'code_completion_lib\methods\models\{self.size}\data.csv', 'a')
                result = []
                written = True
                #break

        if not written:
            write_as_csv(result, rf'code_completion_lib\methods\models\{self.size}\data.csv', 'a')

        self.logger.info("Find methods ended.")

