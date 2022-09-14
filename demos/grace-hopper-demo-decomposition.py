from gherkin_objects.objects import Step, Feature, GherkinProject
from gherkin_objects.formatter import Formatter, FormatterConfig
import re

feature_text = """
Feature: Example
    Scenario Outline: eating
      Given there are <start> cucumbers
      When I eat <eat> cucumbers
      Then I should have <left> cucumbers

      Examples:
        | start | eat | left |
        |    12 |   5 |    7 |
        |    20 |   5 |   15 |
"""

feature = Feature.from_text(feature_text)
formatter = Formatter(FormatterConfig())


if __name__ == '__main__':
    # Note: The output here in this particular example is quite ugly.  It could be made better
    # by using key_value pairs in the title of the decomposed scenarios.  That code does exist, but
    # is not currently used and cannot currently be configured.  This would be a worthwhile contribution
    for scenario in feature.decomposed_scenarios:
        print('-' * 80)
        print('\n'.join(formatter.format_scenario(scenario)))
        print('-' * 80)

    outline = feature.scenario_outlines[0]
    for step in outline.steps:
        print('-' * 80)
        print(f'This step: {step.real_text}')
        print(f'contains these parameters: {step.parameters}')

    print('=' * 80)
    for table in outline.tables:
        for row in table.rows:
            print(row.values)