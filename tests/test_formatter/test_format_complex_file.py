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
from unittest.mock import patch
from gherkin_objects.formatter import Formatter
from gherkin_objects.formatter.formatter_config import FormatterConfig

from .util import FormatComponentTest


class TestFormatComplexFile(FormatComponentTest):

    def test_format_complex_file(self):
        self.config = FormatterConfig()
        self.config.tag.ensure_scenario_uuid = True
        self.config.example_table.combine_tables_with_equivalent_tags = False
        self.formatter = Formatter(self.config)
        input_lines = '''
@tag1 @tag2
Feature: feature
    This is a feature
    It is cool
Background:
Given step 1

Scenario Outline: outline
This is a scenario outline
Given step 1
| data 1 |
| data 2 |
When step 2
| foo | bar |
| 1 | 1234 |
| 2 | 5678 |
Then step 3
* <param>

Examples:
| param |
| foo |
| bar |
        '''.split('\n')
        expected_lines = '''
@tag1
@tag2
Feature: feature
  This is a feature
  It is cool


    Background:

        Given step 1


    Scenario Outline: outline
      This is a scenario outline

        Given step 1
          | data 1 |
          | data 2 |
        When step 2
          | foo | bar  |
          | 1   | 1234 |
          | 2   | 5678 |
        Then step 3
        And <param>

        @uuid:foo
        Examples:
          | param |
          | foo   |

        @uuid:foo
        Examples:
          | param |
          | bar   |

        '''.split('\n')[1:-1]
        with patch('uuid.uuid4', lambda: 'foo'):
            self.assert_feature_formatted(input_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
