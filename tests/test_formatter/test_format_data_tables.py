import unittest
from gherkin_objects.formatter import Formatter
from .util import FormatComponentTest


class TestFormatDataTable(FormatComponentTest):

    def test_indent(self):
        self.config.data_table.indent = 2
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '  | foo |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_blank_lines_before(self):
        self.config.data_table.blank_lines_before = 2
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '',
            '',
            '| foo |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_blank_lines_after(self):
        self.config.data_table.blank_lines_after = 2
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '| foo |',
            '',
            '',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_all_columns_same_width(self):
        self.config.data_table.all_columns_same_width = True
        input_lines = [
            '| foo | bar baz |',
        ]
        expected_lines = [
            '| foo     | bar baz |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_cell_left_padding(self):
        self.config.data_table.cell_left_padding = 5
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '|     foo |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_cell_right_padding(self):
        self.config.data_table.cell_right_padding = 5
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '| foo     |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_cell_min_width(self):
        self.config.data_table.cell_min_width = 10
        input_lines = [
            '| foo |',
        ]
        expected_lines = [
            '| foo        |',
        ]
        self.assert_table_formatted(input_lines, expected_lines)

    def test_padding_shared_with___none(self):
        self.config.data_table.padding_shared_with = None
        input_lines = [
            '| data     |',
            '| a really long data |',
        ]
        expected_lines = ['| data |', '| a really long data |']
        self.assert_table_formatted(input_lines, expected_lines)

    def test_padding_shared_with___table(self):
        self.config.data_table.padding_shared_with = Formatter.Config.DataTable.PaddingSharedWith.table
        input_lines = [
            '| data     |',
            '| a really long data |',
        ]
        expected_lines = ['| data               |', '| a really long data |']
        self.assert_table_formatted(input_lines, expected_lines)

    def test_padding_shared_with___scenario(self):
        self.config.data_table.padding_shared_with = Formatter.Config.DataTable.PaddingSharedWith.scenario
        input_lines = [
            'Scenario: scenario',
            'Given step 1',
            '| data     |',
            'Given step 2',
            '| a really long data |',
        ]
        expected_lines = [
            'Scenario: scenario',
            'Given step 1',
            '| data               |',
            'Given step 2',
            '| a really long data |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_padding_shared_with___feature(self):
        self.config.data_table.padding_shared_with = Formatter.Config.DataTable.PaddingSharedWith.feature
        input_lines = [
            'Feature: feature',
            'Scenario: scenario 1',
            'Given step 1',
            '| data |',
            'Scenario: scenario 2',
            'Given step 1',
            '| a really long data |',
        ]
        expected_lines = [
            'Feature: feature',
            'Scenario: scenario 1',
            'Given step 1',
            '| data               |',
            'Scenario: scenario 2',
            'Given step 1',
            '| a really long data |',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
