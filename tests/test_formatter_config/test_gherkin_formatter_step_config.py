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
