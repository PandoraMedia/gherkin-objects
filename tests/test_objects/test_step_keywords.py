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
from gherkin_objects.objects import StepKeyword


class MyTestCase(unittest.TestCase):

    def test_keyword_property(self):
        self.assertEqual(StepKeyword.GIVEN.keyword, 'Given')
        self.assertEqual(StepKeyword.WHEN.keyword, 'When')
        self.assertEqual(StepKeyword.THEN.keyword, 'Then')
        self.assertEqual(StepKeyword.AND.keyword, 'And')
        self.assertEqual(StepKeyword.BUT.keyword, 'But')
        self.assertEqual(StepKeyword.BULLET.keyword, '*')

    def test_from_string(self):
        self.assertEqual(StepKeyword.from_string('GIVEN'), StepKeyword.GIVEN)
        self.assertEqual(StepKeyword.from_string('Given'), StepKeyword.GIVEN)
        self.assertEqual(StepKeyword.from_string('given'), StepKeyword.GIVEN)

        self.assertEqual(StepKeyword.from_string('WHEN'), StepKeyword.WHEN)
        self.assertEqual(StepKeyword.from_string('When'), StepKeyword.WHEN)
        self.assertEqual(StepKeyword.from_string('when'), StepKeyword.WHEN)

        self.assertEqual(StepKeyword.from_string('THEN'), StepKeyword.THEN)
        self.assertEqual(StepKeyword.from_string('Then'), StepKeyword.THEN)
        self.assertEqual(StepKeyword.from_string('then'), StepKeyword.THEN)

        self.assertEqual(StepKeyword.from_string('AND'), StepKeyword.AND)
        self.assertEqual(StepKeyword.from_string('And'), StepKeyword.AND)
        self.assertEqual(StepKeyword.from_string('and'), StepKeyword.AND)

        self.assertEqual(StepKeyword.from_string('BUT'), StepKeyword.BUT)
        self.assertEqual(StepKeyword.from_string('But'), StepKeyword.BUT)
        self.assertEqual(StepKeyword.from_string('but'), StepKeyword.BUT)

        self.assertEqual(StepKeyword.from_string('*'), StepKeyword.BULLET)

        self.assertIsNone(StepKeyword.from_string(''))
        self.assertIsNone(StepKeyword.from_string(None))


if __name__ == '__main__':
    unittest.main()
