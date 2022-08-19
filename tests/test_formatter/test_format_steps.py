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
from gherkin_objects.formatter import Formatter

from .util import FormatComponentTest


class TestFormatSteps(FormatComponentTest):

    def test_indent(self):
        self.config.step.indent = 2
        input_lines = [
            'Given step 1',
        ]
        expected_lines = [
            '  Given step 1',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_keyword_policy___prefer_raw(self):
        self.config.step.keyword_policy = Formatter.Config.Step.KeywordPolicy.prefer_raw
        input_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_keyword_policy___prefer_real(self):
        self.config.step.keyword_policy = Formatter.Config.Step.KeywordPolicy.prefer_real
        input_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            'Given step 2',
            'Given step 3',
            'Given step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_keyword_policy___prefer_and(self):
        self.config.step.keyword_policy = Formatter.Config.Step.KeywordPolicy.prefer_and
        input_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            'And step 2',
            'And step 3',
            'And step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_keyword_policy___prefer_bullet(self):
        self.config.step.keyword_policy = Formatter.Config.Step.KeywordPolicy.prefer_bullet
        input_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            '* step 2',
            '* step 3',
            '* step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_vertical_alignment___by_keyword(self):
        self.config.step.vertical_alignment = Formatter.Config.Step.VerticalAlignment.by_keyword
        input_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            'And step 2',
            '* step 3',
            'Given step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)

    def test_vertical_alignment___by_step_text(self):
        self.config.step.vertical_alignment = Formatter.Config.Step.VerticalAlignment.by_step_text
        input_lines = [
            'Given step 1',
            '  And step 2',
            '    * step 3',
            'Given step 4',
        ]
        expected_lines = [
            'Given step 1',
            '  And step 2',
            '    * step 3',
            'Given step 4',
        ]
        self.assert_steps_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
