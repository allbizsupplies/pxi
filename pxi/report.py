
from openpyxl.cell import Cell
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, NamedStyle
import re


class ReportWriter:
    """write XLSX report."""

    TYPEFACE = "Calibri"
    FONT_SIZE = 11
    DEFAULT_ALIGNMENT = "left"
    
    def __init__(self, filepath):
        # Create the workbook and remove the default sheet.
        self.workbook = Workbook()
        del self.workbook["Sheet"]

        self.filepath = filepath
        self.currentRow = dict()
        self.columnStyles = dict()
    
    def write_sheet(self, name, fields, rows):
        # add the sheet to the workbook
        ws = self.workbook.create_sheet(title=name)
        # add the header row
        row = list()
        for field in fields:
            cell = Cell(ws, value=field["title"])
            # pylint: disable=assigning-non-slot
            cell.alignment = Alignment(horizontal="center")
            cell.font = Font(
                name=ReportWriter.TYPEFACE,
                size=ReportWriter.FONT_SIZE,
                bold=True)
            row.append(cell)
        ws.append(row)
        # add the data rows
        for data in rows:
            row = list()
            for field in fields:
                cell = Cell(ws, value=data[field["name"]])
                # pylint: disable=assigning-non-slot
                cell.alignment = Alignment(horizontal=ReportWriter.DEFAULT_ALIGNMENT)
                if "align" in field.keys():
                    cell.alignment = Alignment(horizontal=field["align"])
                cell.font = Font(
                    name=ReportWriter.TYPEFACE,
                    size=ReportWriter.FONT_SIZE)
                if "number_format" in field.keys():
                    cell.number_format = field["number_format"]
                row.append(cell)
            ws.append(row)

        # apply column widths
        for index, field in enumerate(fields):
            # get the alphabetical column index
            c = chr(index + 65)
            # set the column width
            ws.column_dimensions[c].width = field["width"]
        
    def save(self):
        # save the file
        self.workbook.save(self.filepath)


class ReportReader:
    """XLSX report reader"""

    def __init__(self, filepath):
        workbook = load_workbook(filename=filepath, read_only=True)
        self.worksheet = workbook[workbook.sheetnames[0]]
        self.fieldnames = self.get_fieldnames()

    def load(self):
        data = list()
        # Iterate over rows until we hit an empty row.
        for cells in self.worksheet.iter_rows(min_row=2):
            # generate dict from the cells
            row = dict()
            for i, f in enumerate(self.fieldnames):
                row[f] = cells[i].value

            # discard the row and stop iterating if first column is empty.
            if row[self.fieldnames[0]] is not None:
                data.append(row)
            else:
                break
        return data

    def get_fieldnames(self):
        "Read fieldnames from the first row until we hit an empty cell."

        fieldnames = list()
        col_index = 0
        while True:
            value = self.worksheet.cell(1, col_index + 1).value
            if value:
                value = value.lower()
                value = re.sub(r"[/ -]", "_", value)
                value = re.sub(r"[\(\)\.]", "", value)
                fieldnames.append(value)
            else:
                # stop as soon as we hit an empty cell
                break
            col_index += 1
        return fieldnames
