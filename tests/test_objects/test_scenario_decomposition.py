import unittest
from gherkin_objects.objects import Feature, Scenario, Tag


class MyTestCase(unittest.TestCase):

    def test_decompose_scenario(self):
        text = 'Scenario: scenario'
        scenario = Scenario.from_text(text)
        self.assertEqual(scenario.decompose(), [scenario])

    def test_decompose_background(self):
        text = 'Background: background'
        scenario = Scenario.from_text(text)
        self.assertEqual(scenario.decompose(), [scenario])

    def test_decompose_scenario_outline_with_no_examples(self):
        text = '''
        Scenario Outline: outline
        Given step 1
        When step 2
        Then step 3
        '''
        scenario = Scenario.from_text(text)
        self.assertEqual(scenario.decompose(), [])

    def test_decompose_scenario_has_background(self):
        text = """
        Feature: A feature

          Background:
            Given the house has power
            And I bought a toaster

          Scenario: Make toast
            Given I put bread in the toaster
            When I turn the toaster on
            Then I get toast
        """
        feature = Feature.from_text(text)
        scenarios = feature.decomposed_scenarios
        # Make sure we're working with the "real" scenario
        assert scenarios[1].name == "Make toast"

        # The first 2 steps are the background steps
        all_steps = scenarios[1].all_steps
        assert all_steps[0].text_without_keyword == "the house has power"
        assert all_steps[1].text_without_keyword == "I bought a toaster"

    def test_decompose_scenario_outline(self):
        text = """
        @tag1
        Scenario Outline: outline
        Given <A> 
        Then <B>

        Examples:
        | A | B |
        | 1 | 2 |

        @tag2
        Examples:
        | A | B |
        | 3 | 4 |
        """
        outline = Scenario.from_text(text)

        scenarios = outline.decompose()

        scenario1 = scenarios[0]
        self.assertEqual('outline_1_1_2', scenario1.name)
        self.assertEqual('Given 1', scenario1.steps[0].raw_text)
        self.assertEqual('Then 2', scenario1.steps[1].raw_text)
        self.assertSetEqual(set(scenario1.tags),
                            set([
                                Tag(text='@tag1', parent=scenario1),
                            ]))

        scenario2 = scenarios[1]
        self.assertEqual('outline_2_3_4', scenario2.name)
        self.assertEqual('Given 3', scenario2.steps[0].raw_text)
        self.assertEqual('Then 4', scenario2.steps[1].raw_text)
        self.assertSetEqual(
            set(scenario2.tags),
            set([
                Tag(text='@tag1', parent=scenario2),
                Tag(text='@tag2', parent=scenario2),
            ]))


if __name__ == '__main__':
    unittest.main()
