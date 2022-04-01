import unittest
from gherkin_objects.objects import Scenario, ScenarioType, StepType, StepKeyword, Feature


class TestScenarios(unittest.TestCase):

    def test_scenario_sanity(self):
        scenario = Scenario(scenario_type=ScenarioType.SCENARIO,
                            name='scenario')
        self.assertEqual(scenario.steps, [])

    def test_scenario_name(self):
        text = '''
        Scenario: scenario
        '''
        scenario = Scenario.from_text(text)
        self.assertEqual(scenario.name, 'scenario')
        self.assertEqual(scenario.title_text, 'Scenario: scenario')

    def test_scenario_with_no_name(self):
        text = '''
        Scenario:
        '''
        scenario = Scenario.from_text(text)
        self.assertEqual(scenario.name, '')
        self.assertEqual(scenario.title_text, 'Scenario:')

    def test_scenario_from_text(self):
        text = """
        Scenario: scenario
        
        Given Step A
        """
        scenario = Scenario.from_text(text)

        self.assertEqual(scenario.name, 'scenario')
        self.assertEqual(scenario.steps[0].raw_text, 'Given Step A')

    def test_scenario_with_and_from_text(self):
        text = """
        Scenario: scenario
        
        Given step 1
        And step 2
        When step 3
        Then step 4
        """
        scenario = Scenario.from_text(text)

        self.assertEqual(len(scenario.steps), 4)
        self.assertEqual(scenario.steps[1].keyword, StepKeyword.AND)
        self.assertEqual(scenario.steps[1].step_type, StepType.GIVEN)

    def test_scenario_with_but_from_text(self):
        text = '''
        Scenario: scenario
        Given step
        But step
        When step
        Then step
        '''
        scenario = Scenario.from_text(text)
        self.assertEqual(len(scenario.steps), 4)
        self.assertEqual(scenario.steps[1].keyword, StepKeyword.BUT)
        self.assertEqual(scenario.steps[1].step_type, StepType.GIVEN)

    def test_scenario_with_bullet_from_text(self):
        text = '''
        Scenario: scenario
        Given step
        When step
        Then step
        * step
        * step
        '''
        scenario = Scenario.from_text(text)
        self.assertEqual(len(scenario.steps), 5)
        self.assertEqual(scenario.steps[3].keyword, StepKeyword.BULLET)
        self.assertEqual(scenario.steps[4].keyword, StepKeyword.BULLET)
        self.assertEqual(scenario.steps[3].step_type, StepType.THEN)
        self.assertEqual(scenario.steps[4].step_type, StepType.THEN)

    def test_scenario_from_text_without_steps(self):
        text = 'Scenario: scenario'
        scenario = Scenario.from_text(text)
        self.assertEqual(len(scenario.steps), 0)

    def test_scenario_from_text_with_tags(self):
        text = '''
        @tag @tag2
        Scenario: scenario
        '''
        scenario = Scenario.from_text(text)

        self.assertEqual(len(scenario.tags), 2)
        self.assertEqual(scenario.tags[0].text, '@tag')
        self.assertEqual(scenario.tags[1].text, '@tag2')

    def test_scenario_from_text_with_description(self):
        text = '''
        Scenario: scenario
        This is a description of the scenario
        '''
        scenario = Scenario.from_text(text)

        self.assertEqual(scenario.description,
                         '        This is a description of the scenario')
        self.assertEqual(scenario.description.strip(),
                         'This is a description of the scenario')

    def test_scenario_from_text_with_multiline_description(self):
        text = '\n'.join([
            'Scenario: scenario',
            'This is a multiline',
            'description of the scenario',
        ])

        scenario = Scenario.from_text(text)

        self.assertEqual(scenario.description,
                         'This is a multiline\ndescription of the scenario')

    def test_scenario_with_feature_tags(self):
        text = '\n'.join([
            '@feature1 @feature2',
            'Feature: feature',
            '@tag1',
            'Scenario: scenario',
        ])
        feature = Feature.from_text(text)
        expected_tags = ['@feature1', '@feature2', '@tag1']
        actual_tags = [tag.text for tag in feature.scenarios[0].all_tags]
        self.assertSequenceEqual(expected_tags, actual_tags)


if __name__ == '__main__':
    unittest.main()
