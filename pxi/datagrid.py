
import re
from openpyxl import load_workbook


def load_rows(filepath):
    """Read data from XLSX datagrid."""
    workbook = load_workbook(filename=filepath, read_only=True)
    worksheet = workbook[workbook.get_sheet_names()[0]]
    fieldnames = get_fieldnames(worksheet)
    rows = []
    for row in worksheet.iter_rows(min_row=2):
        if row[0].value is None:
            break
        values = dict()
        for i, fieldname in enumerate(fieldnames):
            values[fieldname] = row[i].value
        rows.append(values)
    workbook.close()
    return rows

    
def get_fieldnames(worksheet):
    """Parse snakecase fieldnames from first row of sheet."""
    fieldnames = []
    col_index = 0
    while True:
        value = worksheet.cell(1, col_index + 1).value
        # Stop as soon as we hit an empty cell.
        if value is None:
            return fieldnames
        fieldnames.append(snakecase(value))
        col_index += 1


def snakecase(value):
    value = value.strip()
    value = value.lower()
    value = re.sub(r"[/ =:-]", "_", value)
    value = re.sub(r"[\(\)\.]", "", value)
    value = value.replace("___", "_")
    value = value.replace("__", "_")
    value = value.strip("_")
    return value
