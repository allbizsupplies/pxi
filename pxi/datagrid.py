
import re
from openpyxl import load_workbook


def read_rows(worksheet):
    """
    Read rows from worksheet.
    """
    rows = []
    fieldnames = get_fieldnames(worksheet)
    for row in worksheet.iter_rows(min_row=2):
        if row[0].value is None:
            return rows
        values = dict()
        for i, fieldname in enumerate(fieldnames):
            values[fieldname] = row[i].value
        rows.append(values)
    return rows


def load_rows(filepath, worksheet_name=None):
    """
    Read data from XLSX datagrid.
    """
    workbook = load_workbook(filename=filepath, read_only=True)

    # Use the first worksheet by default.
    if worksheet_name is None:
        worksheet_name = workbook.get_sheet_names()[0]
    worksheet = workbook[worksheet_name]
    rows = read_rows(worksheet)
    workbook.close()
    return rows


def get_fieldnames(worksheet):
    """
    Parse snakecase fieldnames from first row of sheet.
    """
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
