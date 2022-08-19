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
from gherkin_objects.objects import Feature, Tag, InvalidGherkinError


class TestFeature(unittest.TestCase):

    def test_feature_sanity(self):
        feature = Feature('A feature')

        self.assertIsNone(feature.description)
        self.assertIsNone(feature.background)
        self.assertEqual(feature.tags, [])
        self.assertEqual(feature.scenarios, [])
        self.assertEqual(feature.scenario_outlines, [])

    def test_valid_empty_feature_from_text(self):
        text = """
        Feature: feature
        """
        feature = Feature.from_text(text)
        self.assertEqual(feature.name, 'feature')
        self.assertEqual(feature.title_text, 'Feature: feature')

    def test_feature_with_no_name_from_text(self):
        text = '''
        Feature:
        '''
        feature = Feature.from_text(text)
        self.assertEqual(feature.name, '')
        self.assertEqual(feature.title_text, 'Feature:')

    def test_completely_empty_feature_from_text(self):
        with self.assertRaises(ValueError):
            feature = Feature.from_text('')

    def test_invalid_feature_from_text(self):
        text = 'Invalid Feature'
        with self.assertRaises(InvalidGherkinError):
            feature = Feature.from_text(text)

    def test_simple_feature_from_text(self):
        text = """
        Feature: feature
        
        Scenario: scenario
        
        Given step A
        When step B
        Then step C
        """
        feature = Feature.from_text(text)
        self.assertEqual(feature.name, 'feature')
        self.assertEqual(feature.scenarios[0].name, 'scenario')
        self.assertEqual(feature.scenarios[0].steps[0].raw_text,
                         'Given step A')
        self.assertEqual(feature.scenarios[0].steps[1].raw_text, 'When step B')
        self.assertEqual(feature.scenarios[0].steps[2].raw_text, 'Then step C')

    def test_feature_with_scenario_outline_from_text(self):
        text = """
        Feature: feature
        
        Scenario Outline: outline
        
        Given Step A
        When Step B
        Then Step C
        
        Examples:
        | 1 | 2 |
        | 3 | 4 |
        
        @tag
        Examples:
        | A | B |
        | C | D |
        """
        feature = Feature.from_text(text)
        outline = feature.scenario_outlines[0]
        self.assertEqual(outline.name, 'outline')
        self.assertEqual(len(outline.tables), 2)

        table1 = outline.tables[0]
        self.assertEqual(table1.values, [
            ['1', '2'],
            ['3', '4'],
        ])

        table2 = outline.tables[1]
        self.assertEqual(table2.values, [
            ['A', 'B'],
            ['C', 'D'],
        ])

        self.assertEqual(table2.tags, [Tag('@tag')])

    def test_feature_with_non_square_example_table(self):
        text = """
        Feature: feature
        
        Scenario Outline: outline
        
        Examples:
        | A | B |
        | C |
        """
        with self.assertRaises(InvalidGherkinError):
            feature = Feature.from_text(text)

    def test_feature_with_datatable(self):
        text = """
        Feature: feature
        
        Scenario: scenario
        
        Given Step 1
        Given Step 2
        | data 1 |
        | data 2 |
        """
        feature = Feature.from_text(text)

        steps = feature.scenarios[0].steps
        self.assertEqual(steps[0].real_text, "Given Step 1")
        self.assertEqual(steps[1].real_text, "Given Step 2")
        self.assertIsNotNone(steps[1].data_table)
        self.assertSequenceEqual(steps[1].data_table.rows,
                                 [['data 1'], ['data 2']])


if __name__ == '__main__':
    unittest.main()
