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
import uuid

from unittest.mock import patch

from .util import FormatComponentTest


class TestFormatSteps(FormatComponentTest):

    def test_uuid_patch(self):
        """
        This is a sanity check for my future self and others that are not familiar with patching
        Even though it is not strictly necessary, please do not remove it
        """
        with patch('uuid.uuid4', lambda: 'foo'):
            self.assertEqual(uuid.uuid4(), 'foo')
        self.assertNotEqual(uuid.uuid4(), 'foo')

    def test_ensure_scenario_uuid___no_uuid(self):
        with patch('uuid.uuid4', lambda: 'foo'):
            self.config.tag.ensure_scenario_uuid = True
            input_lines = [
                'Scenario: scenario',
            ]
            expected_lines = [
                '@uuid:foo',
                'Scenario: scenario',
            ]
            self.assert_scenario_formatted(input_lines, expected_lines)

    def test_ensure_scenario_placeholder___no_uuid(self):
        with patch('uuid.uuid4', lambda: 'foo'):
            self.config.tag.ensure_scenario_uuid = True
            input_lines = [
                'Scenario: Placeholder',
            ]
            expected_lines = ['Scenario: Placeholder']
            self.assert_scenario_formatted(input_lines, expected_lines)

    def test_ensure_scenario_uuid___with_uuid(self):
        self.config.tag.ensure_scenario_uuid = True
        input_lines = [
            '@uuid:foo',
            'Scenario: scenario',
        ]
        expected_lines = [
            '@uuid:foo',
            'Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_ensure_scenario_uuid___scenario_outline___no_uuid(self):
        with patch('uuid.uuid4', lambda: 'foo'):
            self.config.tag.ensure_scenario_uuid = True
            input_lines = [
                'Scenario Outline: outline',
                'Given <foo>',
                'Examples:',
                '| foo |',
                '| 1 |',
                '| 2 |',
            ]
            expected_lines = [
                'Scenario Outline: outline',
                'Given <foo>',
                '@uuid:foo',
                'Examples:',
                '| foo |',
                '| 1   |',
                '@uuid:foo',
                'Examples:',
                '| foo |',
                '| 2   |',
            ]
            self.assert_scenario_formatted(input_lines, expected_lines)

    def test_ensure_scenario_uuid___scenario_outline___with_uuid(self):
        self.config.tag.ensure_scenario_uuid = True
        input_lines = [
            'Scenario Outline: outline',
            'Given <foo>',
            '@uuid:foo',
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            'Scenario Outline: outline',
            'Given <foo>',
            '@uuid:foo',
            'Examples:',
            '| foo |',
            '| 1   |',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_ensure_feature_uuid___without_uuid(self):
        with patch('uuid.uuid4', lambda: 'foo'):
            self.config.tag.ensure_feature_uuid = True
            input_lines = [
                'Feature: feature',
            ]
            expected_lines = [
                '@feature_uuid:foo',
                'Feature: feature',
            ]
            self.assert_feature_formatted(input_lines, expected_lines)

    def test_ensure_feature_uuid___with_uuid(self):
        self.config.tag.ensure_feature_uuid = True
        input_lines = [
            '@feature_uuid:foo',
            'Feature: feature',
        ]
        expected_lines = [
            '@feature_uuid:foo',
            'Feature: feature',
        ]
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_alphabetize_tags(self):
        self.config.tag.alphabetize_tags = True
        input_lines = [
            '@foo @bar @baz',
            'Scenario: scenario',
        ]
        expected_lines = [
            '@bar',
            '@baz',
            '@foo',
            'Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_tag_order_top(self):
        self.config.tag.tag_order_top = [['@tag3', '@tag2'], ['@tag1']]
        input_lines = [
            '@tag1',
            '@tag2',
            '@foo @bar @baz',
            '@tag3',
            'Scenario: scenario',
        ]
        expected_lines = [
            '@tag3 @tag2',
            '@tag1',
            '@foo',
            '@bar',
            '@baz',
            'Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_tag_order_bottom(self):
        self.config.tag.tag_order_bottom = [['@tag3', '@tag2'], ['@tag1']]
        input_lines = [
            '@tag1',
            '@tag2',
            '@foo @bar @baz',
            '@tag3',
            'Scenario: scenario',
        ]
        expected_lines = [
            '@foo',
            '@bar',
            '@baz',
            '@tag3 @tag2',
            '@tag1',
            'Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_feature_tags_indent(self):
        self.config.feature.indent = 2
        input_lines = [
            '@foo',
            'Feature: feature',
        ]
        expected_lines = ['  @foo', '  Feature: feature']
        self.assert_feature_formatted(input_lines, expected_lines)

    def test_scenario_tags_indent(self):
        self.config.scenario.indent = 2
        input_lines = [
            '@foo',
            'Scenario: scenario',
        ]
        expected_lines = [
            '  @foo',
            '  Scenario: scenario',
        ]
        self.assert_scenario_formatted(input_lines, expected_lines)

    def test_example_table_tags_indent(self):
        self.config.example_table.indent = 2
        self.config.example_table.indent_row = 2
        input_lines = [
            '@foo',
            'Examples:',
            '| foo |',
            '| 1 |',
        ]
        expected_lines = [
            '  @foo',
            '  Examples:',
            '  | foo |',
            '  | 1   |',
        ]
        self.assert_example_table_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()