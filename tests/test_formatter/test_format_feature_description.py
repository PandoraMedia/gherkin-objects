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
from tests.test_formatter.util import FormatComponentTest


class TestFormatFeatureDescription(FormatComponentTest):

    def test_indent___single_line(self):
        self.config.feature_description.indent = 2
        input_lines = [
            'Feature: feature',
            'foo',
        ]
        expected_lines = [
            'Feature: feature',
            '  foo',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_blank_lines_before(self):
        self.config.feature_description.blank_lines_before = 2
        input_lines = [
            'Feature: feature',
            'foo',
        ]
        expected_lines = [
            'Feature: feature',
            '',
            '',
            'foo',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_indent___multi_line(self):
        self.config.feature_description.indent = 2
        input_lines = [
            'Feature: feature',
            'foo',
            'bar',
        ]
        expected_lines = [
            'Feature: feature',
            '  foo',
            '  bar',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_preserve_internal_empty_lines___true(self):
        self.config.feature_description.preserve_internal_empty_lines = True
        input_lines = [
            'Feature: feature',
            'foo',
            '',
            'bar',
        ]
        expected_lines = [
            'Feature: feature',
            'foo',
            '',
            'bar',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_preserve_internal_empty_lines___false(self):
        self.config.feature_description.preserve_internal_empty_lines = False
        input_lines = [
            'Feature: feature',
            'foo',
            '',
            'bar',
        ]
        expected_lines = [
            'Feature: feature',
            'foo',
            'bar',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_preserve_relative_indentation___true(self):
        self.config.feature_description.preserve_relative_indentation = True
        input_lines = [
            'Feature: feature',
            'foo',
            '  bar',
        ]
        expected_lines = [
            'Feature: feature',
            'foo',
            '  bar',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_preserve_relative_indentation___false(self):
        self.config.feature_description.preserve_relative_indentation = False
        input_lines = [
            'Feature: feature',
            'foo',
            '  bar',
        ]
        expected_lines = [
            'Feature: feature',
            'foo',
            'bar',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
