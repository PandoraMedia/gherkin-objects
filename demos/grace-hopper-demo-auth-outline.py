from gherkin_objects.objects import Step, Feature, GherkinProject
from gherkin_objects.formatter import Formatter, FormatterConfig
from gherkin_objects.tag_filter import GherkinTagFilter
import re

feature_text = """
Feature: Authentication
    Scenario Outline: Sign in as user type
      Given no User is signed in
      When a <type> User signs in
      Then the user should be signed in
    
      @regression
      Examples:
        | type |
        | free |
      
      @sanity
      Examples:
        | type |
        | paid |
"""

feature = Feature.from_text(feature_text)
formatter = Formatter(FormatterConfig())


if __name__ == '__main__':
    filter = GherkinTagFilter('@sanity')
    scenarios = feature.decomposed_scenarios
    filtered_scenarios = [scenario for scenario in scenarios if filter.evaluate([tag.text for tag in scenario.tags])]

    for scenario in filtered_scenarios:
        print('-' * 80)
        print('\n'.join(formatter.format_scenario(scenario)))
        print('-' * 80)