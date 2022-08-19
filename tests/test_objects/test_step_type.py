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
from gherkin_objects.objects import StepType


class StepTypeTests(unittest.TestCase):

    def test_keyword_property(self):
        self.assertEqual(StepType.GIVEN.keyword, 'Given')
        self.assertEqual(StepType.WHEN.keyword, 'When')
        self.assertEqual(StepType.THEN.keyword, 'Then')

    def test_from_string(self):
        self.assertEqual(StepType.from_string('GIVEN'), StepType.GIVEN)
        self.assertEqual(StepType.from_string('Given'), StepType.GIVEN)
        self.assertEqual(StepType.from_string('given'), StepType.GIVEN)

        self.assertEqual(StepType.from_string('WHEN'), StepType.WHEN)
        self.assertEqual(StepType.from_string('When'), StepType.WHEN)
        self.assertEqual(StepType.from_string('when'), StepType.WHEN)

        self.assertEqual(StepType.from_string('THEN'), StepType.THEN)
        self.assertEqual(StepType.from_string('Then'), StepType.THEN)
        self.assertEqual(StepType.from_string('then'), StepType.THEN)

        self.assertIsNone(StepType.from_string('And'))
        self.assertIsNone(StepType.from_string('But'))
        self.assertIsNone(StepType.from_string('*'))
        self.assertIsNone(StepType.from_string(''))
        self.assertIsNone(StepType.from_string(None))


if __name__ == '__main__':
    unittest.main()
