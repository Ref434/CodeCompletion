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
        for some_import in imports:

            for method in methods:
                similar = ''
                split_method = method.split('.')
                split_import = some_import[0].split('.')
                complete_match = True
                if len(some_import) == 2:
                    split_import.extend(some_import[1].split('.'))

                if len(split_import) == len(split_method):
                    if len(some_import) == 2:
                        if method == f"{some_import[0]}.{some_import[1]}":
                            result.append([method, some_import[1]])

                elif len(split_import) < len(split_method):
                    for index in range(len(split_import)):
                        if split_method[index] == split_import[index]:
                            similar += split_method[index] + '.'
                        else:
                            complete_match = False

                if len(some_import) == 2:
                    if not complete_match and some_import[1] == '*':
                        result.append([method, method.replace(similar, '')])
                elif len(some_import) == 3:
                    if some_import[1] == 'as':
                        result.append([method, method.replace(similar, f'{some_import[2]}.')])
                elif complete_match and similar != '':
                    result.append([method, f"{similar.split('.')[-2]}.{method.replace(similar, '')}"])

        return result

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
            imported_methods_without_repetitions = []
            [imported_methods_without_repetitions.append(element) for element in imported_methods if
             element not in imported_methods_without_repetitions]

            for method in imported_methods_without_repetitions:
                reg_exp = re.findall(rf".+=\s*{method[1]}\(", code, flags=re.ASCII)
                reg_exp = [match.rstrip().replace(" ", "")[:-1].split("=", 1) for match in reg_exp]

                if len(reg_exp) != 0:
                    for exp in reg_exp:
                        exp[1] = method[0]
                        exp.append(completion.cluster_predict(imports_only_lib))

                    methods_result.extend(reg_exp)
        write_as_csv(methods_result, r'code_completion_lib\methods\methods.csv', 'w')

        print("Find methods ended")
