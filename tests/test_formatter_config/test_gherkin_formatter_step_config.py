import unittest
from gherkin_objects.formatter.formatter_config import StepConfig


class TestFeatureConfigIO(unittest.TestCase):

    def setUp(self) -> None:
        self.config = StepConfig(
            indent=0,
            vertical_alignment=StepConfig.VerticalAlignment.by_keyword,
            keyword_policy=StepConfig.KeywordPolicy.prefer_real,
        )
        self.json = {
            'indent': 0,
            'vertical_alignment': 'by_keyword',
            'keyword_policy': 'prefer_real',
        }

    def test_to_json(self):
        self.assertEqual(self.config.to_json(), self.json)

    def test_from_json(self):
        loaded = StepConfig.from_json(self.json)
        self.assertEqual(loaded, self.config)
        self.assertTrue(
            isinstance(loaded.keyword_policy, StepConfig.KeywordPolicy))
        self.assertTrue(
            isinstance(loaded.vertical_alignment,
                       StepConfig.VerticalAlignment))

    def test_from_json___unknown_option(self):
        self.json['foo'] = 'bar'
        with self.assertRaises(AttributeError):
            StepConfig.from_json(self.json)


if __name__ == '__main__':
    unittest.main()
