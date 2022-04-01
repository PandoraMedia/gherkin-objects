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
