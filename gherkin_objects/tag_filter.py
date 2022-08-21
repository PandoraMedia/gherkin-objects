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

import re
from typing import List


class GherkinTagFilter:

    def __init__(self, string: str):
        self.expression = GherkinTagFilter.to_expression(string)
        GherkinTagFilter.validate(self.expression)

    @staticmethod
    def validate(string: str):
        expression = GherkinTagFilter.to_expression(string)

        # No adjacent tags
        tag_pattern = r'@\S+'
        match = re.search(rf'{tag_pattern}[()\s]*{tag_pattern}', expression)
        if match:
            raise ValueError(
                f'Adjacent tags with no operator: {match.group(0)}')

        # No tags that do not start with @
        for item in expression.split():
            if not re.match(rf'not|and|or|\(|\)|{tag_pattern}', item):
                raise ValueError(f'Invalid tag: {item}')

        # No unbalanced parentheses
        count = 0
        for i, char in enumerate(expression):
            if char == '(':
                count += 1
            if char == ')':
                count -= 1
            if count < 0:
                raise ValueError(f'Unbalanced parentheses: Unexpected closing parenthesis at char {i} in tag expression:'
                                 f'\n{expression}'
                                 f'\n{" " * (i)}^')
        if count != 0:
            raise ValueError(f'Unbalanced parentheses: {expression}')

    @staticmethod
    def to_expression(string: str) -> str:
        expression = string
        expression = re.sub(r'\s*!\s*', ' not ', expression)  # '!' --> ' not '
        expression = re.sub(r'\s*&&\s*', ' and ',
                            expression)  # '&&' -> ' and '
        expression = re.sub(r'\s*&\s*', ' and ', expression)  # '&' --> ' and '
        expression = re.sub(r'\s*\|\|\s*', ' or ',
                            expression)  # '||' -> ' or '
        expression = re.sub(r'\s*\|\s*', ' or ', expression)  # '|' --> ' or '
        expression = re.sub(r'\s*\(\s*', ' ( ', expression)  # '(' --> ' ( '
        expression = re.sub(r'\s*\)\s*', ' ) ', expression)  # ')' --> ' ) '
        expression = re.sub(r'\s+', ' ', expression)  # Consolidate whitespace
        expression = expression.strip()
        return expression

    def substitute_tags(self, tags: List[str]) -> str:
        result = self.expression
        for tag in tags:
            result = re.sub(rf'{tag}(?=\s|$)', 'True', result)
        result = re.sub(r'@\S+', 'False', result)
        return result

    def evaluate(self, tags: List[str]) -> bool:
        substituted_expression = self.substitute_tags(tags)

        # One final check before performing eval
        allowed_strings = {'True', 'False', 'and', 'or', 'not', '(', ')'}
        if not set(substituted_expression.split()).issubset(allowed_strings):
            raise RuntimeError(
                f'Unsafe eval: "{substituted_expression}" only these components allowed: {allowed_strings}'
            )

        # Evaluate expression as a Python expression.  This will return a boolean
        result = eval(substituted_expression)
        return result
