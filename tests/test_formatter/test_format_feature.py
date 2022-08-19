"""
Copyright 2022 SiriusXM-Pandora

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
