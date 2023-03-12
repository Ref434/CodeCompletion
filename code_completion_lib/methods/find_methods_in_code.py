import re
import os

from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports

from code_completion_lib.necessary_functions import get_code, write_as_csv, read_json


class Methods:

    def _get_methods(self, object):
        methodList = []
        for method_name in dir(object):
            try:
                if callable(getattr(object, method_name)):
                    methodList.append(str(method_name))
            except Exception:
                methodList.append(str(method_name))

        return methodList

    def _find_full_method_name(self, methods_json, arr=[], prefix=""):

        for key, val in methods_json.items():
            if type(val) == str and not key.startswith("_"):
                arr.append(f"{prefix}{key}")

            if type(val) == dict:
                prefix_old = prefix
                prefix += f"{key}."
                self._find_full_method_name(val, arr, prefix)
                prefix = prefix_old

        return arr

    def _find_imported_methods(self, methods, imports):
        result = []
        for method in methods:
            for some_import in imports:
                if len(some_import) == 1:
                    if method == some_import[0]:
                        result.append([method, some_import[0]])
                if len(some_import) == 2:
                    if method == f"{some_import[0]}.{some_import[1]}":
                        result.append([method, some_import[1]])

        return result

    # TODO: Not working with not 'clear' imports (from sklearn import linear_model ... my_model = linear_model.LogisticRegression). Only (from sklearn.linear_model import LogisticRegression)
    def find_methods(self, data_path: str, methods_json: str, lib: str):
        methods_result = []

        methods = self._find_full_method_name(read_json(methods_json), prefix=lib)
        methods_result.append(["varible_name", "method", "cluster"])

        completion = CodeCompletion()
        import_class = Imports(data_path)

        for filename in os.listdir(data_path):

            full_path = os.path.join(data_path, filename)

            code = get_code(full_path)

            imports = import_class.find_imports(code, format='usage')
            imports_only_lib = import_class.find_imports(code, format='only_lib')
            imported_methods = self._find_imported_methods(methods, imports)

            for method in imported_methods:
                reg_exp = re.findall(rf".+=\s*{method[1]}\(", code, flags=re.ASCII)
                reg_exp = [match.rstrip().replace(" ", "")[:-1].split("=", 1) for match in reg_exp]

                if len(reg_exp) != 0:
                    for exp in reg_exp:
                        exp[1] = method[0]
                        exp.append(completion.cluster_predict(imports_only_lib))

                    methods_result.extend(reg_exp)
        write_as_csv(methods_result, r'code_completion_lib\methods\methods.csv', 'w')

        print("Find methods ended")
