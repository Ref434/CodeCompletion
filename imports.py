import re
import os
import csv
import sys

def line_processing(line):
    imports = []
    if line[0] == "import":
        for index in range(1, len(line)):
            imports.append(line[index])

    if line[0] == "from":
        tmp = line[1]
        for index in range(3, len(line)):
            imports.append(f"{tmp}.{line[index]}")

    return imports






def find_imports(code):
    imports = []
    reg_exp = re.findall(r"\bimport\s+\S+|\bfrom\s+\S+\s+import\s+[^,\s]+\s*(?:,\s*[^,\s]+)*", code, flags=re.ASCII)
    reg_exp = [match.rstrip().replace(",", " ").split(" ") for match in reg_exp]
    for match in reg_exp:
        for word in match:
            if word == "":
                match.remove(word)
        imports.extend(line_processing(match))
    return imports


def write_as_csv(data):
    with open('imports.csv', 'w', encoding='utf-8') as f:
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

    all_imports = []
    i = 0

    for folder in os.listdir(param_value):
        if folder.endswith("_parsed"):
            imports = []
            path = os.path.join(param_value, folder)
            for filename in os.listdir(path):
                if filename.startswith('code'):
                    full_path = os.path.join(path, filename)
                    with open(full_path, 'r', encoding='utf-8') as file:
                        code = file.read()
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

    print("Success.")
