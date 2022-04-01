import unittest
from .util import FormatComponentTest


class TestFormatScenario(FormatComponentTest):

    def test_indent(self):
        self.config.scenario.indent = 2
        input_lines = [
            'Scenario: scenario',
        ]
        expected_lines = [
            '  Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_blank_lines_before(self):
        self.config.scenario.blank_lines_before = 2
        input_lines = [
            'Scenario: scenario',
        ]
        expected_lines = [
            '',
            '',
            'Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_blank_lines_before_steps(self):
        self.config.scenario.blank_lines_before_steps = 2
        input_lines = [
            'Scenario: scenario',
            'Given step 1',
        ]
        expected_lines = [
            'Scenario: scenario',
            '',
            '',
            'Given step 1',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
