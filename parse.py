import json
import os
import csv
import sys


def get_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as notebook:
        return json.load(notebook, strict=False)


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


def write_as_csv(data):
    with open('imports.csv', 'w') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Error. Too few parameters.")
        sys.exit(1)

    if len(sys.argv) > 3:
        print("Error. Too many parameters.")
        sys.exit(1)
    param_name = sys.argv[1]
    param_value = sys.argv[2]

    if param_name != "--path":
        print(f"Error. Unknown parameter '{param_name}'.")
        sys.exit(1)

    if not os.path.exists(param_value):
        print(f"Error. The system cannot find the path '{param_value}'.")
        sys.exit(1)

    print("Processing...")

    for filename in os.listdir(param_value):
        if filename.endswith(".ipynb"):
            imports = []
            full_path = os.path.join(param_value, filename)
            notebook = get_notebook(full_path)
            if not os.path.exists(f"{param_value}\{filename}_parsed"):
                os.mkdir(f"{param_value}\{filename}_parsed")

                for name, code in get_cells_content(notebook['cells']):

                    save_as_txt_file(f"{param_value}\{filename}_parsed\{name}", code)

    print("Success.")
