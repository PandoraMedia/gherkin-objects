import unittest
from .util import FormatComponentTest


class TestFormatSteps(FormatComponentTest):

    def test_indent(self):
        self.config.example_table.indent = 2
        self.config.example_table.indent_row = 4
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            '  Examples:',
            '    | foo |',
            '    | 1   |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_blank_lines_before(self):
        self.config.example_table.blank_lines_before = 2
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            '',
            '',
            'Examples:',
            '| foo |',
            '| 1   |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_blank_lines_after(self):
        self.config.example_table.blank_lines_after = 2
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            'Examples:',
            '| foo |',
            '| 1   |',
            '',
            '',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_all_columns_in_row_same_width(self):
        self.config.example_table.all_columns_in_row_same_width = True
        input_lines = [
            'Examples:',
            '| foo | bar |',
            '| 1 | 123456 |',
        ]
        expected_lines = [
            'Examples:',
            '| foo    | bar    |',
            '| 1      | 123456 |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_cell_left_padding(self):
        self.config.example_table.cell_left_padding = 5
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            'Examples:',
            '|     foo |',
            '|     1   |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_cell_left_padding(self):
        self.config.example_table.cell_right_padding = 5
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            'Examples:',
            '| foo     |',
            '| 1       |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_cell_min_width(self):
        self.config.example_table.cell_min_width = 10
        input_lines = [
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            'Examples:',
            '| foo        |',
            '| 1          |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)

    def test_enforce_header_order(self):
        self.config.example_table.enforce_header_order = True
        input_lines = [
            'Scenario Outline: scenario',
            'Given <foo> <bar>',
            'Examples:',
            '| bar | foo |',
            '| 1 | 2 |',
        ]
        expected_lines = [
            'Scenario Outline: scenario',
            'Given <foo> <bar>',
            'Examples:',
            '| foo | bar |',
            '| 2   | 1   |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_combine_tables_with_equivalent_tags___no_tags(self):
        self.config.example_table.combine_tables_with_equivalent_tags = True
        input_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            'Examples:',
            '| foo |',
            '| 1 |',
            'Examples:',
            '| foo |',
            '| 2 |',
        ]
        expected_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            'Examples:',
            '| foo |',
            '| 1   |',
            '| 2   |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_combine_tables_with_equivalent_tags___tags(self):
        self.config.example_table.combine_tables_with_equivalent_tags = True
        input_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            '@tag',
            'Examples:',
            '| foo |',
            '| 1 |',
            '@tag',
            'Examples:',
            '| foo |',
            '| 2 |',
        ]
        expected_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            '@tag',
            'Examples:',
            '| foo |',
            '| 1   |',
            '| 2   |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_all_tables_in_outline_same_width(self):
        self.config.example_table.all_tables_in_outline_same_width = True
        input_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            'Examples:',
            '| foo |',
            '| 1 |',
            'Examples:',
            '| foo |',
            '| 123456 |',
        ]
        expected_lines = [
            'Scenario Outline: scenario',
            'Given <foo>',
            'Examples:',
            '| foo    |',
            '| 1      |',
            'Examples:',
            '| foo    |',
            '| 123456 |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
