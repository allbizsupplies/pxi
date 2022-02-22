
from random import randint
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pxi.report import NumberField, ReportField, ReportWriter, StringField
from tests.fakes import random_string


class ReportFieldTests(TestCase):

    def test_init_without_number_format(self):
        field = ReportField(
            name=random_string(10),
            title=random_string(10),
            width=randint(40, 80),
            align="left")
        self.assertIsNone(field.number_format)

    def test_init_with_number_format(self):
        field = ReportField(
            name=random_string(10),
            title=random_string(10),
            width=randint(40, 80),
            align="left",
            number_format="0.00")
        self.assertEqual(field.number_format, "0.00")


class StringFieldTests(TestCase):

    def test_has_left_alignment(self):
        field = StringField(
            name=random_string(10),
            title=random_string(10),
            width=randint(40, 80))
        self.assertEqual(field.align, "left")


class NumberFieldTests(TestCase):

    def test_has_price_number_format(self):
        field = NumberField(
            name=random_string(10),
            title=random_string(10))
        self.assertEqual(field.number_format, "0.0000")

    def test_has_right_alignment(self):
        field = NumberField(
            name=random_string(10),
            title=random_string(10))
        self.assertEqual(field.align, "right")

    def test_has_fixed_width(self):
        field = NumberField(
            name=random_string(10),
            title=random_string(10))
        self.assertEqual(field.width, 16)


class ReportWriterTests(TestCase):

    def test_init_filepath(self):
        filepath = random_string(20)
        report_writer = ReportWriter(filepath)
        self.assertEqual(report_writer.filepath, filepath)

    @patch("pxi.report.Workbook")
    def test_write_sheet(self, mock_workbook_class):

        def random_fields(fieldnames):
            return [
                ReportField(
                    name=fieldname,
                    title=random_string(10),
                    align="left" if randint(0, 1) else "right",
                    width=randint(20, 100))
                for fieldname in fieldnames]

        def random_fieldnames():
            return [random_string(10) for _ in range(randint(5, 10))]

        def random_row(fieldnames):
            row = {}
            for fieldname in fieldnames:
                row[fieldname] = random_string(10)
            return row

        def random_rows(fieldnames, row_count):
            return [random_row(fieldnames) for _ in range(5, 10)]

        filepath = random_string(20)
        sheet_name = random_string(20)
        fieldnames = random_fieldnames()
        fields = random_fields(fieldnames)
        data = random_rows(fieldnames, randint(5, 10))
        mock_worksheet = MagicMock()
        mock_workbook = mock_workbook_class.return_value
        mock_workbook.create_sheet.return_value = mock_worksheet

        report_writer = ReportWriter(filepath)
        report_writer.write_sheet(sheet_name, fields, data)

        self.assertEqual(mock_worksheet.append.call_count, len(data) + 1)

    @patch("pxi.report.Workbook")
    def test_save(self, mock_workbook_class):
        mock_workbook = mock_workbook_class.return_value
        filepath = random_string(20)

        report_writer = ReportWriter(filepath)
        report_writer.save()

        mock_workbook.save.assert_called_with(filepath)
