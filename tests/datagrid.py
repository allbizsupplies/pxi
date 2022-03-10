
from random import random
from unittest.mock import MagicMock, call, patch

from pxi.datagrid import get_fieldnames, load_rows, read_rows, snakecase
from tests import PXITestCase
from tests.fakes import random_string


class DatagridTests(PXITestCase):

    def test_snakecase(self):
        """
        Converts datagrid headers into snakecase names.
        """
        fixtures = [
            # Convert to lowercase.
            ("ABCabc", "abcabc"),
            # Replace space with underscore.
            ("aaa bbb", "aaa_bbb"),
            # Replace slash with underscore.
            ("aaa/bbb", "aaa_bbb"),
            # Replace equals sign with underscore.
            ("aaa=bbb", "aaa_bbb"),
            # Replace colon with underscore.
            ("aaa:bbb", "aaa_bbb"),
            # Replace hyphen with underscore.
            ("aaa-bbb", "aaa_bbb"),
            # Replace multiple characters with single underscore.
            ("aaa: bbb", "aaa_bbb"),
            ("aaa - bbb", "aaa_bbb"),
            # Remove parentheses.
            ("aaa(bbb", "aaabbb"),
            ("aaa)bbb", "aaabbb"),
            ("aaa(bbb)", "aaabbb"),
            # Disallow consecutive underscores.
            ("aaa__bbb", "aaa_bbb"),
            ("aaa___bbb", "aaa_bbb"),
            # Disallow trailing underscore(s).
            ("aaa ", "aaa"),
            ("aaa/", "aaa"),
            ("aaa=", "aaa"),
            ("aaa:", "aaa"),
            ("aaa-", "aaa"),
            ("aaa_", "aaa"),
            ("aaa__", "aaa"),
            ("aaa___", "aaa"),
        ]

        for input_string, output_string in fixtures:
            self.assertEqual(snakecase(input_string), output_string)

    def test_get_fieldnames(self):
        """
        Collects fieldnames from first row of worksheet.
        """

        mock_worksheet = MagicMock()
        fieldnames = [
            random_string(10).lower(),
            random_string(10).lower(),
            random_string(10).lower(),
        ]
        mock_worksheet.cell.side_effect = [
            mock_cell(fieldname) for fieldname in fieldnames
        ] + [
            mock_cell(None)
        ]

        result = get_fieldnames(mock_worksheet)

        mock_worksheet.cell.assert_has_calls([
            call(1, 1),
            call(1, 2),
            call(1, 3),
            call(1, 4),
        ])
        self.assertEqual(result, fieldnames)

    @patch("pxi.datagrid.get_fieldnames")
    def test_read_rows(self, mock_get_fieldnames):
        """
        Reads data from worksheet and returns a list of dicts.
        """
        fieldnames = [
            random_string(10).lower(),
            random_string(10).lower(),
        ]
        cell_values = [
            [
                random_string(10),
                random_string(10),
            ],
            [
                random_string(10),
                random_string(10),
            ],
        ]
        expected_rows = [
            dict(zip(fieldnames, row_values))
            for row_values in cell_values]
        mock_get_fieldnames.return_value = fieldnames
        mock_worksheet = MagicMock()
        mock_worksheet.iter_rows.return_value = [
            [mock_cell(value) for value in cell_values[0]],
            [mock_cell(value) for value in cell_values[1]],
            [mock_cell(None)],
        ]

        result = read_rows(mock_worksheet)

        self.assertEqual(result, expected_rows)

    @patch("pxi.datagrid.read_rows")
    @patch("pxi.datagrid.load_workbook")
    def test_load_rows_without_worksheet_name(
            self,
            mock_load_workbook,
            mock_read_rows):
        """
        Loads rows from first worksheet in file when no worksheet name given.
        """
        filename = random_string(20)
        worksheet_name = random_string(10)
        mock_worksheet = MagicMock()
        mock_workbook = mock_load_workbook.return_value
        mock_workbook.get_sheet_names.return_value = [
            worksheet_name, random_string(20)]
        mock_workbook.get_sheet_by_name.return_value = mock_worksheet

        result = load_rows(filename)

        mock_load_workbook.assert_called_with(
            filename=filename, read_only=True)
        mock_workbook.get_sheet_names.assert_called()
        mock_workbook.get_sheet_by_name.assert_called_with(worksheet_name)
        mock_workbook.close.assert_called()
        mock_read_rows.assert_called_with(mock_worksheet)
        self.assertEqual(result, mock_read_rows.return_value)

    @patch("pxi.datagrid.read_rows")
    @patch("pxi.datagrid.load_workbook")
    def test_load_rows_with_worksheet_name(
            self,
            mock_load_workbook,
            mock_read_rows):
        """
        Loads rows from first worksheet in file when worksheet name given.
        """
        filename = random_string(20)
        worksheet_name = random_string(20)
        mock_worksheet = MagicMock()
        mock_workbook = mock_load_workbook.return_value
        mock_workbook.get_sheet_by_name.return_value = mock_worksheet

        result = load_rows(filename, worksheet_name=worksheet_name)

        mock_load_workbook.assert_called_with(
            filename=filename, read_only=True)
        mock_workbook.get_sheet_names.assert_not_called()
        mock_workbook.get_sheet_by_name.assert_called_with(worksheet_name)
        mock_workbook.close.assert_called()
        mock_read_rows.assert_called_with(mock_worksheet)
        self.assertEqual(result, mock_read_rows.return_value)


def mock_cell(fieldname):
    cell = MagicMock()
    cell.value = fieldname
    return cell
