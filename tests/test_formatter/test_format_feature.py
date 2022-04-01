import unittest
from .util import FormatComponentTest


class TestFormatScenario(FormatComponentTest):

    def test_indent(self):
        self.config.feature.indent = 2
        input_lines = [
            'Feature: feature',
        ]
        expected_lines = [
            '  Feature: feature',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_blank_lines_before(self):
        self.config.feature.blank_lines_before = 2
        input_lines = [
            'Feature: feature',
        ]
        expected_lines = [
            '',
            '',
            'Feature: feature',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_blank_lines_after(self):
        self.config.feature.blank_lines_after = 2
        input_lines = [
            'Feature: feature', 'Scenario: scenario', 'Given step 1'
        ]
        expected_lines = [
            'Feature: feature',
            'Scenario: scenario',
            'Given step 1',
            '',
            '',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_background_is_first(self):
        input_lines = [
            'Feature: feature',
            'Background:',
            'Given step 1',
            'Scenario: scenario',
            'Given step 1',
        ]
        expected_lines = [
            'Feature: feature',
            'Background:',
            'Given step 1',
            'Scenario: scenario',
            'Given step 1',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
