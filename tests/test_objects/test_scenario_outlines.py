import unittest
from gherkin_objects.objects import Scenario, ScenarioType


class TestScenarioOutlines(unittest.TestCase):

    def test_scenario_outline_sanity(self):
        Scenario(ScenarioType.OUTLINE, 'outline')

    def test_scenario_outline_from_text(self):
        text = """
        Scenario Outline: outline
        Given Step 1
        When Step 2
        Then Step 3

        Examples:
        | A | B |
        | C | D |
        """
        outline = Scenario.from_text(text)

        self.assertEqual(outline.name, 'outline')
        self.assertEqual(len(outline.steps), 3)
        self.assertEqual(len(outline.tables), 1)
        self.assertEqual(len(outline.tables[0].rows), 2)


if __name__ == '__main__':
    unittest.main()
