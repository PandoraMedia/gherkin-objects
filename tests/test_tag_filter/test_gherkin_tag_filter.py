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
from typing import List

from gherkin_objects.tag_filter import GherkinTagFilter


class GherkinTagFilterExpressionConversionTests(unittest.TestCase):
    """These tests check that the input is correctly converted into a Python-style expression."""

    def test_expression_and(self):
        input = '@tag1 & @tag2 && @tag3'
        output = '@tag1 and @tag2 and @tag3'
        self.assertEqual(GherkinTagFilter.to_expression(input), output)

    def test_expression_or(self):
        input = '@tag1 | @tag2 || @tag3'
        output = '@tag1 or @tag2 or @tag3'
        self.assertEqual(GherkinTagFilter.to_expression(input), output)

    def test_expression_not(self):
        input = '!@tag1'
        output = 'not @tag1'
        self.assertEqual(GherkinTagFilter.to_expression(input), output)

    def test_expression_complex(self):
        input = '(@tag1 && @tag2) || !(@tag3 || (@tag4 && @tag5))'
        output = '( @tag1 and @tag2 ) or not ( @tag3 or ( @tag4 and @tag5 ) )'
        self.assertEqual(GherkinTagFilter.to_expression(input), output)


class GherkinTagFilterEvaluationTests(unittest.TestCase):
    """These tests check that a valid expression is actually evaluated properly"""
    def test_evaluate_expression_and_true(self):
        input = '@tag1 && @tag2'
        tags = ['@tag1', '@tag2']
        filter = GherkinTagFilter(input)
        self.assertTrue(filter.evaluate(tags))

    def test_evaluate_expression_and_false(self):
        input = '@tag1 && @tag2'
        tags = ['@tag1']
        filter = GherkinTagFilter(input)
        self.assertFalse(filter.evaluate(tags))

    def test_evaluate_expression_or_true(self):
        input = '@tag1 || @tag2'
        tags = ['@tag1']
        filter = GherkinTagFilter(input)
        self.assertTrue(filter.evaluate(tags))

    def test_evaluate_expression_or_false(self):
        input = '@tag1 || @tag2'
        tags = []
        filter = GherkinTagFilter(input)
        self.assertFalse(filter.evaluate(tags))

    def test_evaluate_expression_not_true(self):
        input = '!@tag1'
        tags = []
        filter = GherkinTagFilter(input)
        self.assertTrue(filter.evaluate(tags))

    def test_evaluate_expression_not_false(self):
        input = '!@tag1'
        tags = ['@tag1']
        filter = GherkinTagFilter(input)
        self.assertFalse(filter.evaluate(tags))

    def test_evaluate_expression_complex_full_truth_table(self):
        # Truth Table - | @tag3 | @tag2 | @tag1 | T/F
        # | 0 | 0 | 0 | F
        # | 0 | 0 | 1 | T
        # | 0 | 1 | 0 | F
        # | 0 | 1 | 1 | F
        # | 1 | 0 | 0 | F
        # | 1 | 0 | 1 | F
        # | 1 | 1 | 0 | F
        # | 1 | 1 | 1 | F
        input = '@tag1 && !(@tag2 || @tag3)'
        filter = GherkinTagFilter(input)

        self.assertFalse(filter.evaluate([]))  # 0 0 0
        self.assertTrue(filter.evaluate(['@tag1']))  # 0 0 1
        self.assertFalse(filter.evaluate(['@tag2']))  # 0 1 0
        self.assertFalse(filter.evaluate(['@tag1', '@tag2']))  # 0 1 1
        self.assertFalse(filter.evaluate(['@tag3']))  # 1 0 0
        self.assertFalse(filter.evaluate(['@tag1', '@tag3']))  # 1 0 1
        self.assertFalse(filter.evaluate(['@tag2', '@tag3']))  # 1 1 0
        self.assertFalse(filter.evaluate(['@tag1', '@tag2', '@tag3']))  # 1 1 1


class GherkinTagFilterSubstitutionTests(unittest.TestCase):
    """These tests check that tags are correctly substituted into the tag expression"""

    def assertSubstitutionResult(self, expression: str, tags: List[str],
                                 expected: str):
        filter = GherkinTagFilter(expression)
        actual = filter.substitute_tags(tags)
        self.assertEqual(actual, expected)

    # TODO: Add simpler substitution tests to support refactoring

    def test_substitution___partial_matches(self):
        """
        Check that no partial tag (@f, @fo, ..., @foo-ba) is substituted into the expression as True.
        This can happen if there is a regex is improperly configured.
        """
        expression = '@foo-bar'
        for i in range(len(expression) - 1):
            sub_expression = expression[:i]
            self.assertSubstitutionResult(expression=expression,
                                          tags=[sub_expression],
                                          expected='False')
        self.assertSubstitutionResult(expression=expression,
                                      tags=[expression],
                                      expected='True')

    def test_evaluation___partial_matches(self):
        expression = '@foo-bar'
        filter = GherkinTagFilter(expression)
        for i in range(len(expression) - 1):
            sub_expression = expression[:i]
            self.assertFalse(filter.evaluate(tags=[sub_expression]))
        self.assertTrue(filter.evaluate(tags=[expression]))


class GherkinTagFilterExceptionTests(unittest.TestCase):
    """These tests check that situations which should raise exceptions actually do"""

    # TODO: Add unbalanced parenthesis test
    # TODO: Add adjacent tag test "@tag1 @tag2 && @tag3" <-- This expression needs an operator between "@tag1 @tag2"
    # TODO: Some of the existing tests perform both construction and evaluation in the assertRaises block, only one should be performed so it is clear which operation raises the error

    def test_tag_without_at_raises_error(self):
        """The @ (at) symbol is semantically meaningful to the tag expression filter, it is
        used internally in some regular expression, so tags without them may not work properly"""
        input = 'tag1 & tag2'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input).evaluate(['tag1'])

    def test_python_code_raises_error(self):
        """Since the evaluate function uses python's eval function under the hood, we must
        make absolutely sure that unintended python code cannot be executed"""
        input = 'print "hello world"'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input).evaluate([])

    def test_unbalanced_parentheses___unclosed_open(self):
        input = '(@tag1 and @tag2'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input)

    def test_unbalanced_parentheses___extra_close(self):
        input = '(@tag1 and @tag2))'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input)

    def test_unbalanced_parentheses___wrong_order(self):
        input = '@tag1) and @tag2('
        with self.assertRaises(ValueError):
            GherkinTagFilter(input)

    def test_adjacent_tags(self):
        input = '@tag1 @tag2'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input)

    def test_adjacent_tags___in_parens(self):
        input = '(@tag1)(@tag2)'
        with self.assertRaises(ValueError):
            GherkinTagFilter(input)


if __name__ == '__main__':
    unittest.main()
