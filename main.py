import json
import re
import os
import csv

PATH_TO_NOTEBOOK = r"D:\sasha\parser\notebooks"


def get_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as notebook:
        return json.load(notebook)


def get_source_from_code_cell(cell):
    return ''.join(cell['source'])


def save_as_txt_file(filename, code):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)


def get_cells_content(notebook_cells):
    yield from (
        (f"{current_cell['cell_type']}_{i}.txt", get_source_from_code_cell(current_cell))
        for i, current_cell in enumerate(notebook_cells, 1)
    )


def find_imports(code):
    imports = []
    reg_exp = re.findall(r"\bimport\s+\S+|\bfrom\s+\S+\s+import\s+[^,\s]+\s*(?:,\s*[^,\s]+)*", code, flags=re.ASCII)
    reg_exp = [match.rstrip().replace(",", "").split(" ") for match in reg_exp]
    for match in reg_exp:
        for word in match:
            if word != "from" and word != "import":
                imports.append(word)
    return imports


def write_as_csv(data):
    with open('imports.csv', 'w') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    all_imports = []
    i = 0
    for filename in os.listdir(PATH_TO_NOTEBOOK):
        if filename.endswith(".ipynb"):
            imports = []
            full_path = os.path.join(PATH_TO_NOTEBOOK, filename)
            notebook = get_notebook(full_path)
            for filename_, code in get_cells_content(notebook['cells']):
                # save_as_txt_file(filename, code)
                if filename_.startswith('code'):
                    imports_one_file = find_imports(code)
                    if len(imports_one_file) != 0:
                        imports.extend(imports_one_file)
            if len(imports) != 0:
                imports.insert(0, i)
                i += 1
                imports_sorted = []
                [imports_sorted.append(x) for x in imports if x not in imports_sorted]
                all_imports.append(imports_sorted)

    imports_without_repetitions = []
    for file in all_imports:
        [imports_without_repetitions.append(x) for x in file if x not in imports_without_repetitions
         and isinstance(x, str)]

    csv_imports = []
    imports_without_repetitions.insert(0, 'id')
    csv_imports.append(imports_without_repetitions)

    for i in range(len(all_imports)):
        tmp = [i]
        for el in imports_without_repetitions:
            if el == 'id':
                continue
            if all_imports[i].count(el) != 0:
                tmp.append(1)
            else:
                tmp.append(0)

        csv_imports.append(tmp)

    write_as_csv(csv_imports)

