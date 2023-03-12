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

