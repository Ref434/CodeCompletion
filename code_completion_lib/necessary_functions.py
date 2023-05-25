import csv
import json



def get_code(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def write_as_csv(data: list, path: str, format: str):
    with open(path, format, encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def read_json(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_imported_methods(methods, imports):
    result = {}

    for some_import in imports:

        for method in methods:
            similar = ''
            split_method = method.split('.')
            split_import = some_import[0].split('.')
            if split_method[0] != split_import[0]:
                continue
            complete_match = True
            if len(some_import) == 2:
                split_import.extend(some_import[1].split('.'))

            if len(split_import) == len(split_method) and split_import[-1] != '*':
                if len(some_import) == 1:
                    if method == some_import[0]:
                        result[(method, method)] = 1
                elif len(some_import) == 2:
                    if method == f"{some_import[0]}.{some_import[1]}":
                        result[(method, some_import[1])] = 1
                elif len(some_import) == 3:
                    if method == some_import[0]:
                        result[(method, some_import[2])] = 1

            if len(split_import) < len(split_method) or (
                    len(split_import) == len(split_method) and split_import[-1] == '*'):
                for index in range(len(split_import)):
                    if split_method[index] == split_import[index]:
                        similar += split_method[index] + '.'
                    else:
                        if split_import[index] != '*':
                            complete_match = False

            if similar != "":
                if len(some_import) == 1 and complete_match:
                    result[(method, method)] = 1

                elif len(some_import) == 2:
                    if some_import[1] == '*' and complete_match:
                        result[(method, method.replace(similar, ''))] = 1
                    elif complete_match:
                        result[(method, f"{similar.split('.')[-2]}.{method.replace(similar, '')}")] = 1

                elif len(some_import) == 3 and some_import[1] == 'as' and complete_match:
                    result[(method, method.replace(similar, f'{some_import[2]}.'))] = 1

    return result
