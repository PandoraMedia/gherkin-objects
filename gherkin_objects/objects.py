"""
This module creates an object-oriented wrapper around
the results of the gherkin-official parser.

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

from __future__ import annotations

import json
import logging
import os
import re
import sys

from glob import glob
from enum import Enum
from typing import List, Dict, Optional, Union, Tuple

from gherkin.token_scanner import TokenScanner
from gherkin.parser import Parser
from gherkin.errors import CompositeParserException


logger = logging.getLogger(__package__)


class GherkinProjectConfig:

    def __init__(self, path, include: List[str], exclude: List[str] = None):
        self.path = path
        self.include = include
        self.exclude = exclude or []

    def save(self):
        json_data = json.loads(
            json.dumps({
                'include': self.include,
                'exclude': self.exclude
            }))
        with open(self.path, 'w') as file:
            file.write(json.dumps(json_data, indent=2))

    @classmethod
    def load(cls, path):
        if not path:
            return None
        with open(path, 'r') as file:
            json_data = file.read()
        json_data = json.loads(json_data)
        json_data = dict(json_data)
        return cls(path=path,
                   include=json_data['include'],
                   exclude=json_data.get('exclude', []))

    def resolve_relative_path(self, path):
        if path.startswith('../'):
            config_path = self.path
            config_dir = os.path.realpath(os.path.dirname(config_path))
            return os.path.realpath(os.path.join(config_dir, path))
        if path.startswith('~'):
            return os.path.expanduser(path)
        if path.startswith('.'):
            path = path.replace('.', os.path.dirname(self.path), 1)
        return path

    @property
    def paths(self) -> List[str]:
        include = [
            self.resolve_relative_path(pattern) for pattern in self.include
        ]
        exclude = [
            self.resolve_relative_path(pattern) for pattern in self.exclude
        ]
        include_specific_files = set()
        include_found_files = set()
        for pattern in include:
            # If the pattern is a file, make sure it is included unless specifically excluded.
            if os.path.exists(pattern) and os.path.isfile(pattern):
                file_path = pattern
                include_specific_files.add(file_path)
            # If the pattern is a directory, create a glob to get all feature files in that directory.
            elif os.path.exists(pattern) and os.path.isdir(pattern):
                dir_path = pattern
                paths_found = glob(os.path.join(dir_path, '**', '*.feature'),
                                   recursive=True)
                if not paths_found:
                    logger.warning(f'No features found in dir: {dir_path}')
                else:
                    for path in paths_found:
                        include_found_files.add(path)
            # Interpret as a raw glob pattern.
            else:
                paths_found = glob(pattern, recursive=True)
                if not paths_found:
                    logger.warning(f'Failed to find features: {pattern}')
                else:
                    for path in glob(pattern, recursive=True):
                        include_found_files.add(path)

        exclude_specific_files = set()
        exclude_found_files = set()
        for pattern in exclude:
            # If the pattern is a file, make sure it is excluded from both specified and found files.
            if os.path.exists(pattern) and os.path.isfile(pattern):
                file_path = pattern
                exclude_specific_files.add(file_path)
                exclude_found_files.add(file_path)
                continue
            # If the pattern is a directory, create a glob to get all feature files in that directory.
            if os.path.exists(pattern) and os.path.isdir(pattern):
                dir_path = pattern
                for path in glob(os.path.join(dir_path, '**', '*.feature'),
                                 recursive=True):
                    exclude_found_files.add(path)
            # Interpret as a raw glob pattern.
            else:
                for path in glob(pattern, recursive=True):
                    exclude_found_files.add(path)

        specific_files = include_specific_files - exclude_specific_files
        found_files = include_found_files - exclude_found_files
        paths = specific_files.union(found_files)
        paths = list(paths)
        return paths


class GherkinProject:
    """
    A group of related FeatureFiles
    """

    def __init__(self,
                 paths: List[str],
                 tag_expresssion: Optional[str] = None,
                 formatter: Optional[Formatter] = None):
        self.paths = paths
        for path in self.paths:
            if not path.endswith('.feature'):
                raise ValueError(f'Not a feature file: {path}')

        self.feature_files = [FeatureFile(path, parent=self) for path in paths]
        for feature_file in self.feature_files:
            feature_file.parent = self

    def refresh(self):
        for feature_file in self.feature_files:
            feature_file.refresh()

    @property
    def features(self) -> List[Feature]:
        return [feature_file.feature for feature_file in self.feature_files]

    @property
    def scenarios(self) -> List[Scenario]:
        result = []
        for feature in self.features:
            for scenario in feature.scenarios:
                result.append(scenario)
        return result

    @property
    def common_root_path(self) -> str:
        """
        Return the longest common path shared between all files in the project
        """
        if len(self.paths) == 0:
            raise ValueError('GherkinProject has no file paths to compare')
        elif len(self.paths) == 1:
            return os.path.dirname(self.paths[0]) + os.path.sep
        return os.path.commonpath(self.paths) + os.path.sep

    @property
    def decomposed_scenarios(self) -> List[Scenario]:
        """
        A list of scenarios with the values in example tables substituted into the steps
        """
        result = []
        for scenario in self.scenarios:
            result.extend(scenario.decompose())
        return result

    @property
    def steps(self) -> List[Step]:
        result = []
        for scenario in self.scenarios:
            for step in scenario.steps:
                result.append(step)
        return result

    @property
    def decomposed_steps(self) -> List[Step]:
        result = []
        for scenario in self.decomposed_scenarios:
            for step in scenario.steps:
                result.append(step)
        return result

    @property
    def unique_step_texts(self) -> List[str]:
        seen = set()
        result = []
        for step in self.all_steps:
            if step.real_text not in seen:
                seen.add(step.real_text)
                result.append(step.real_text)
        return result

    @property
    def unique_decomposed_step_texts(self) -> List[str]:
        seen = set()
        result = []
        for step in self.decomposed_steps:
            if step.real_text not in seen:
                seen.add(step.real_text)
                result.append(step.real_text)
        return result


class FeatureFile:
    """
    A file which contains a feature
    Contains exactly 1 Feature
    """

    def __init__(
        self,
        path: str,
        parent: 'GherkinProject' = None,
    ):
        self.path = path
        self.text = None
        self.feature = None
        self.refresh()
        self.parent = parent

        if self.feature:
            self.feature.parent = self

    def overwrite(self, text: str):
        with open(self.path, 'w') as file:
            file.write(text)
        self.refresh()

    def read(self):
        with open(self.path, 'r') as file:
            return file.read()

    def refresh(self):
        self.text = self.read()
        self.feature = Feature.from_text(self.text)

    @property
    def text_is_valid_gherkin(self):
        if not self.text:
            return False
        if self.feature is None:
            return False
        return True

    @property
    def parent_project(self) -> Optional['GherkinProject']:
        return self.parent

    @property
    def relative_path_to_common_root(self) -> str:
        return self.path[len(self.parent.common_root_path):]


class Feature:
    """
    A group of Gherkin scenarios
    """

    def __init__(
        self,
        name: str,
        description: str = None,
        tags: List['Tag'] = None,
        scenarios: List['Scenario'] = None,
        comments: List['Comment'] = None,
        trailing_comments: List['Comment'] = None,
        parent: 'FeatureFile' = None,
    ):
        self.name = name
        self.description = description
        self.tags = tags or []
        self.scenarios = scenarios or []
        self.comments = comments or []
        self.trailing_comments = trailing_comments or []
        self.parent = parent

        for scenario in self.scenarios:
            scenario.parent = self

    @classmethod
    def from_text(
        cls,
        text: str,
        parent: 'FeatureFile' = None,
    ) -> Feature:
        if not text:
            raise ValueError('Feature text cannot be empty')

        try:
            data = Parser().parse(TokenScanner(text))
        except CompositeParserException as e:
            raise InvalidGherkinError(str(e))

        try:
            feature_data = data['feature']
        except KeyError as e:
            print(json.dumps(data, indent=2))
            raise

        return cls.from_data(feature_data, parent=parent)

    @classmethod
    def from_data(
        cls,
        data: Dict,
        parent: 'FeatureFile' = None,
    ) -> Feature:
        if not data:
            raise ValueError(f'Invalid data: {data}')
        name = data['name']
        description = data.get('description', '').rstrip()
        tags = [Tag.from_data(tag_data) for tag_data in data.get('tags', [])]
        scenarios = [
            Scenario.from_data(scenario_data)
            for scenario_data in data.get('children', [])
        ]
        return cls(name=name,
                   description=description,
                   tags=tags,
                   scenarios=scenarios,
                   parent=parent)

    @property
    def title_text(self):
        return f'Feature: {self.name}' if self.name else 'Feature:'

    @property
    def background(self) -> Optional['Scenario']:
        if self.scenarios and self.scenarios[0].is_background:
            return self.scenarios[0]
        return None

    @property
    def scenario_outlines(self) -> List['Scenario']:
        return [
            scenario for scenario in self.scenarios
            if scenario.is_scenario_outline
        ]

    @property
    def decomposed_scenarios(self) -> List['Scenario']:
        scenarios = []
        for scenario in self.scenarios:
            scenarios.extend(scenario.decompose())
        return scenarios

    def add_tag(self, tag: 'Tag', position: Optional[int] = None):
        tag.parent = self
        self.tags.append(tag) if position is None else self.tags.insert(
            position, tag)

    def add_scenario(self,
                     scenario: 'Scenario',
                     position: Optional[int] = None):
        scenario.parent = self
        self.scenarios.append(
            scenario) if position is None else self.scenarios.insert(
                position, scenario)

    def add_comment(self, comment: 'Comment', position: Optional[int] = None):
        comment.parent = self
        self.comments.append(
            comment) if position is None else self.comments.insert(
                position, comment)

    def add_trailing_comment(self,
                             comment: 'Comment',
                             position: Optional[int] = None):
        comment.parent = self
        self.trailing_comments.append(
            comment) if position is None else self.trailing_comments.insert(
                position, comment)

    @property
    def parent_project(self) -> Optional['GherkinProject']:
        return None if self.parent is None else self.parent.parent_project

    @property
    def parent_feature_file(self) -> Optional['FeatureFile']:
        return self.parent


class Scenario:

    def __init__(
        self,
        scenario_type: 'ScenarioType',
        name: str,
        description: str = None,
        steps: List['Step'] = None,
        tags: List['Tag'] = None,
        tables: List['ExampleTable'] = None,
        comments: List['Comment'] = None,
        parent: 'Feature' = None,
    ):
        self.scenario_type = scenario_type
        self.name = name
        self.description = description
        self.steps = steps or []
        self.tags = tags or []
        self.tables = tables or []
        self.comments = comments or []
        self.parent = parent

        for step in self.steps:
            step.parent = self
        for tag in self.tags:
            tag.parent = self
        for table in self.tables:
            table.parent = self

    @classmethod
    def from_text(cls, text, parent: 'Feature' = None):
        dummy_text = f"""
        Feature: dummy
        {text}"""

        try:
            feature = Feature.from_text(dummy_text)
            scenario = feature.scenarios[0]
            scenario.parent = parent
            return scenario
        except CompositeParserException as e:
            raise InvalidGherkinError(str(e))

    @classmethod
    def from_data(cls, data, parent: 'Feature' = None):
        scenario_type = ScenarioType.from_string(data.get('keyword', ''))
        name = data['name']
        description = data.get('description', '').rstrip()
        steps = Step.multiple_from_data(data.get('steps', []))
        tags = [Tag.from_data(tag_data) for tag_data in data.get('tags', [])]
        tables = [
            ExampleTable.from_data(table_data)
            for table_data in data.get('examples', [])
        ]
        return cls(scenario_type,
                   name,
                   description=description,
                   steps=steps,
                   tags=tags,
                   tables=tables,
                   parent=parent)

    @property
    def title_text(self):
        return f'{self.keyword}: {self.name}' if self.name else f'{self.keyword}:'

    @property
    def is_background(self):
        return self.scenario_type == ScenarioType.BACKGROUND

    @property
    def is_scenario(self):
        return self.scenario_type == ScenarioType.SCENARIO

    @property
    def is_scenario_outline(self):
        return self.scenario_type == ScenarioType.OUTLINE

    @property
    def keyword(self):
        return self.scenario_type.keyword

    @property
    def all_tags(self):
        """Feature + Scenario tags"""
        if self.parent is not None:
            return self.parent.tags + self.tags
        else:
            return self.tags

    @property
    def all_steps(self):
        """Scenario steps + background steps"""
        if self.parent is not None and self.parent.background is not None:
            # Remove the background steps first so we don't have duplicates. We don't know
            # if self.steps contains background steps or not.
            steps_without_background = [
                x for x in self.steps if x not in self.parent.background.steps
            ]
            return self.parent.background.steps + steps_without_background

        return self.steps

    def decomposed_scenario_name(
        self,
        scenario: Scenario,
        scenario_number: int,
        params: List[Tuple[str, str]],
        param_param_separator: str = '_',
        param_name_value_separator: str = '_',
    ) -> str:
        name = scenario.name
        name += f'_{scenario_number}'
        for param_name, param_value in params:
            # name += f'{param_param_separator}{param_name}{param_name_value_separator}{param_value}'
            name += f'{param_name_value_separator}{param_value}'
        return name

    def decompose(self) -> List['Scenario']:
        """
        Decompose a scenario outline into multiple scenarios
        :return: List of Scenarios
        """
        if not self.is_scenario_outline:
            return [self]

        scenario_count = 0
        scenarios = []
        for table in self.tables:
            for row_params in table.table_row_params:
                scenario_count += 1

                name = self.decomposed_scenario_name(
                    scenario=self,
                    scenario_number=scenario_count,
                    params=row_params)

                description = self.description

                scenario_tags = [Tag.from_text(tag.text) for tag in self.tags]
                table_tags = [Tag.from_text(tag.text) for tag in table.tags]
                tags = scenario_tags + table_tags

                steps = [
                    Step.from_text(step.raw_text, step_type=step.step_type)
                    for step in self.all_steps
                ]
                for step in steps:
                    for param_name, param_value in row_params:
                        step._text = step._text.replace(
                            f'<{param_name}>', param_value)

                scenario = Scenario(scenario_type=ScenarioType.SCENARIO,
                                    name=name,
                                    description=description,
                                    tags=tags,
                                    steps=steps,
                                    tables=[],
                                    parent=self.parent)
                scenarios.append(scenario)
        return scenarios

    def add_tag(self, tag: 'Tag', position: Optional[int] = None):
        tag.parent = self
        self.tags.append(tag) if position is None else self.tags.insert(
            position, tag)

    def add_step(self, step: 'Step', position: Optional[int] = None):
        step.parent = self
        self.steps.append(step) if position is None else self.steps.insert(
            position, step)

    def add_table(self, table: 'ExampleTable', position: Optional[int] = None):
        table.parent = self
        self.tables.append(table) if position is None else self.tables.insert(
            position, table)

    def add_comment(self, comment: 'Comment', position: Optional[int] = None):
        comment.parent = self
        self.comments.append(
            comment) if position is None else self.comments.insert(
                position, comment)

    @property
    def parent_project(self) -> Optional['GherkinProject']:
        return None if self.parent is None else self.parent.parent_project

    @property
    def parent_feature_file(self) -> Optional['FeatureFile']:
        return None if self.parent is None else self.parent.parent_feature_file

    @property
    def parent_feature(self) -> Optional['Feature']:
        return self.parent

    @property
    def uuid(self) -> Optional[str]:
        for tag in self.tags:
            if tag.text.startswith('@uuid:'):
                return tag.text.replace('@uuid:', '')
        return None


class Step:
    """
    A Gherkin line beginning with one of the following keywords:
    [Given, When, Then, And, But, *]
    """

    def __init__(
        self,
        keyword: 'StepKeyword',
        text: str,
        data_table: Optional[DataTable] = None,
        step_type: 'StepType' = None,
        comments: List['Comment'] = None,
        parent: 'Scenario' = None,
    ):
        """
        :param keyword: The actual keyword of the step: Given/When/Then/And/But/*
        :param text: The text of the step excluding the keyword
        :param step_type: Given/When/Then? Inferred if keyword is one of the three base keywords
        """
        self.keyword = keyword
        # This attribute is kept private to force people to be explicit about what text they want
        self._text = text
        # Attempt to infer step_type from keyword
        if step_type is None:
            if keyword in (StepKeyword.GIVEN, StepKeyword.WHEN,
                           StepKeyword.THEN):
                step_type = StepType.from_string(keyword.keyword)
            else:
                raise ValueError(
                    f'Cannot infer step_type from keyword: {keyword.keyword}')
        # Inference successful
        self.step_type = step_type
        self.comments = comments or []
        self.data_table = data_table
        self.parent = parent

        if self.data_table:
            self.data_table.parent = self

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.keyword != other.keyword:
            return False
        if self.text_without_keyword != other.text_without_keyword:
            return False
        if self.step_type != other.step_type:
            return False
        return True

    def __hash__(self):
        return hash(id(self))

    @classmethod
    def multiple_from_text(cls,
                           text: str,
                           parent: 'Scenario' = None) -> List['Step']:
        dummy_feature = f'''
        Feature: feature
        Scenario: scenario
        {text}
        '''

        data = Parser().parse(TokenScanner(dummy_feature))
        feature_data = data['feature']
        scenario_data = feature_data['children'][0]
        step_data = scenario_data['steps']
        return cls.multiple_from_data(step_data, parent=parent)

    @classmethod
    def from_text(cls,
                  text: str,
                  step_type: 'StepType' = None,
                  parent: 'Scenario' = None) -> Optional['Step']:
        if not text.strip():
            return None
        words = text.strip().split()
        first_word = words[0]
        text_without_keyword = ' '.join(words[1:])

        keyword = StepKeyword.from_string(first_word)
        step_type = StepType.from_string(first_word) or step_type

        if keyword is None:
            raise InvalidGherkinError(
                f'{first_word} is not a Step keyword: {text}')
        if step_type is None:
            raise ValueError(f'Failed to infer step type from: {text}')

        return cls(keyword=keyword,
                   text=text_without_keyword,
                   step_type=step_type,
                   parent=parent)

    @classmethod
    def multiple_from_data(
        cls,
        data: Dict,
        parent: 'Scenario' = None,
    ) -> List['Step']:
        steps = []
        previous_step_type = None
        for step_data in data:
            step = cls.from_data(step_data,
                                 previous_step_type=previous_step_type,
                                 parent=parent)
            steps.append(step)
            previous_step_type = step.step_type
        return steps

    @classmethod
    def from_data(
        cls,
        data: Dict,
        previous_step_type: Optional['StepType'],
        parent: 'Scenario' = None,
    ) -> 'Step':
        keyword = StepKeyword.from_string(data['keyword'].strip())
        text = data['text']

        step_type = StepType.from_string(keyword.keyword) or previous_step_type
        if not step_type:
            raise InvalidGherkinError(
                f'Failed to resolve Given/When/Then type from {data}')

        data_table = None
        argument = data.get('argument', {})
        if argument:
            if argument['type'] == 'DataTable':
                data_table = DataTable.from_data(argument)

        return cls(keyword=keyword,
                   text=text,
                   step_type=step_type,
                   data_table=data_table,
                   parent=parent)

    @property
    def parameters(self) -> List[str]:
        return re.findall(r'<(.*?)>', self.text_without_keyword)

    @property
    def text_without_keyword(self):
        return self._text

    @property
    def raw_keyword(self) -> str:
        return self.keyword.keyword

    @property
    def raw_text(self) -> str:
        return f'{self.raw_keyword} {self.text_without_keyword}'

    @property
    def real_keyword(self) -> str:
        if self.step_type:
            return self.step_type.keyword
        # The only way anyone should ever be able to get into this state is
        # to manually del step_type.  Or just ignoring exceptions thrown
        # by the various constructors.  Don't do that!
        raise RuntimeError(f'The step_type is not known: {self.raw_text}')

    @property
    def real_text(self) -> str:
        return f'{self.real_keyword} {self.text_without_keyword}'

    def add_comment(self, comment: 'Comment', position: Optional[int] = None):
        comment.parent = self
        self.comments.append(
            comment) if position is None else self.comments.insert(
                position, comment)

    @property
    def parent_project(self) -> Optional['GherkinProject']:
        return None if self.parent is None else self.parent.parent_project

    @property
    def parent_feature_file(self) -> Optional['FeatureFile']:
        return None if self.parent is None else self.parent.parent_feature_file

    @property
    def parent_feature(self) -> Optional['Feature']:
        return None if self.parent is None else self.parent.parent_feature

    @property
    def parent_scenario(self) -> Optional['Scenario']:
        return self.parent


class DataTable:

    def __init__(self, rows: List[List[str]], parent: Optional[Step] = None):
        self.rows = rows
        self.parent = parent

    @classmethod
    def from_text(cls, text: str, parent: Optional[Step] = None) -> DataTable:
        dummy_feature = f'''
        Feature: feature
        Scenario: scenario
        Given step
        {text}
        '''
        feature = Feature.from_text(dummy_feature)
        data_table = feature.scenarios[0].steps[0].data_table
        result = DataTable(
            rows=data_table.rows,
            parent=parent,
        )
        return result

    @classmethod
    def from_data(cls, data: dict, parent: Optional[Step] = None) -> DataTable:
        rows = []
        for row_data in data['rows']:
            row = []
            for cell_data in row_data['cells']:
                cell_contents = cell_data['value']
                row.append(cell_contents)
            rows.append(row)
        return cls(rows=rows, parent=parent)

    @property
    def parent_project(self) -> Optional[GherkinProject]:
        return None if self.parent is None else self.parent.parent_project

    @property
    def parent_feature_file(self) -> Optional[FeatureFile]:
        return None if self.parent is None else self.parent.parent_feature_file

    @property
    def parent_feature(self) -> Optional[Feature]:
        return None if self.parent is None else self.parent.parent_feature

    @property
    def parent_scenario(self) -> Optional[Scenario]:
        return None if self.parent is None else self.parent.parent_scenario

    @property
    def parent_step(self) -> Optional[Step]:
        return self.parent


class ExampleTable:

    def __init__(
        self,
        header_row: 'ExampleTableRow',
        data_rows: List['ExampleTableRow'],
        tags: List['Tag'] = None,
        parent: Optional['Scenario'] = None,
    ):
        self.header_row = header_row
        self.data_rows = data_rows
        self.tags: List['Tag'] = tags or []
        self.parent = parent

    def __len__(self):
        return len(self.values)

    @classmethod
    def from_2d_array(
        cls,
        array: List[List[str]],
        tags: List[str] = None,
        parent: 'Scenario' = None,
    ) -> 'ExampleTable':

        lengths = [len(row) for row in array]
        if len(set(lengths)) != 1:
            raise InvalidGherkinError(
                f'Different row lengths detected, non-square example tables not supported:\n{array}'
            )

        header_array = array[0]
        header_row = ExampleTableRow.from_array(header_array)

        data_arrays = array[1:]
        data_rows = [
            ExampleTableRow.from_array(data_array)
            for data_array in data_arrays
        ]

        tags = tags or []
        tags = [Tag.from_text(tag_text) for tag_text in tags]

        return cls(header_row=header_row,
                   data_rows=data_rows,
                   tags=tags,
                   parent=parent)

    @classmethod
    def from_text(
        cls,
        text: str,
        parent: 'Scenario' = None,
    ):
        dummy_text = f'''
        Feature: feature
        Scenario Outline: outline
        Given step
        {text}
        '''
        feature = Feature.from_text(dummy_text)
        table = feature.scenario_outlines[0].tables[0]
        table.parent = parent
        return table

    @classmethod
    def from_data(
        cls,
        data: Dict,
        parent: 'Scenario' = None,
    ):
        header_row_data = data.get('tableHeader', {})
        header_row_data = header_row_data.get('cells', [])
        header_row_values = [cell.get('value', '') for cell in header_row_data]
        header_row = ExampleTableRow.from_array(header_row_values)

        body_rows_data = data.get('tableBody', [])
        body_rows_data = [row.get('cells', []) for row in body_rows_data]
        body_rows_values = []
        for row in body_rows_data:
            body_rows_values.append([cell.get('value', '') for cell in row])
        body_rows = [
            ExampleTableRow.from_array(row_values)
            for row_values in body_rows_values
        ]

        tags = [Tag.from_data(tag_data) for tag_data in data.get('tags', [])]

        return cls(header_row=header_row,
                   data_rows=body_rows,
                   tags=tags,
                   parent=parent)

    @property
    def rows(self) -> List['ExampleTableRow']:
        return [self.header_row] + self.data_rows

    @property
    def values(self) -> List[List[str]]:
        return [row.values for row in self.rows]

    @property
    def header_values(self) -> List[str]:
        return self.header_row.values

    @property
    def data_values(self) -> List[List[str]]:
        return [row.values for row in self.data_rows]

    @property
    def table_row_params(self) -> List[List[Tuple[str, str]]]:
        """
        Returns a 2D list of params
        Each row in this 2D list represents the params of a data row
        Each cell in this 2D list represents a param
        Each param is a Tuple of the form (param_name, param_value)
        """
        param_names = self.header_row.values
        return [row.row_params(param_names) for row in self.data_rows]

    @property
    def column_names(self) -> List[str]:
        return self.header_values

    @property
    def column_values(self) -> List[Dict[str, List[str]]]:
        column_names = self.header_row.values
        columns = [{column_name: []} for column_name in column_names]
        for row in self.data_rows:
            for column_index, cell in enumerate(row.cells):
                column_name = column_names[column_index]
                column_values = columns[column_index][column_name]
                column_values.append(cell.value)
                columns[column_index][column_name] = column_values
        return columns

    @property
    def parent_project(self) -> Optional['GherkinProject']:
        return None if self.parent is None else self.parent.parent_project

    @property
    def parent_feature_file(self) -> Optional['FeatureFile']:
        return None if self.parent is None else self.parent.parent_feature_file

    @property
    def parent_feature(self) -> Optional['Feature']:
        return None if self.parent is None else self.parent.parent_feature

    @property
    def parent_scenario(self) -> Optional['Scenario']:
        return self.parent

    @property
    def all_tags(self):
        """Feature + Scenario + Table tags"""
        if self.parent is not None:
            return self.parent.all_tags + self.tags
        else:
            return self.tags


class ExampleTableRow:

    def __init__(
        self,
        cells: List['ExampleTableCell'],
        parent: 'ExampleTable' = None,
    ):
        self.cells = cells
        self.parent = parent

    def __len__(self):
        return len(self.cells)

    @classmethod
    def from_array(cls,
                   array: List[str],
                   parent: 'ExampleTable' = None) -> 'ExampleTableRow':
        return cls(cells=[ExampleTableCell(value) for value in array],
                   parent=parent)

    @classmethod
    def from_data(cls,
                  data: Dict,
                  parent: 'ExampleTable' = None) -> 'ExampleTableRow':
        return cls.from_array([cell_data['value'] for cell_data in data],
                              parent=parent)

    @property
    def values(self) -> List[str]:
        return [cell.value for cell in self.cells]

    def row_params(self, param_names: List[str]) -> List[Tuple[str, str]]:
        """
        Return a list of params, in the order they appear in the table
        A param is a Tuple of the form (param_name, param_value)
        This function is not valid if this row is a header row

        :param param_names: The names of the columns of the tables, in order
        :return: A list of (param_name, param_value) tuples
        """
        return list(zip(param_names, self.values))

    def add_cell(self, value: str = '', position: int = None):
        if position is None:
            self.cells.append(ExampleTableCell(value))
        else:
            self.cells.insert(position, ExampleTableCell(value))


class ExampleTableCell:

    def __init__(
        self,
        value: str,
        parent: 'ExampleTableRow' = None,
    ):
        self.value = value
        self.parent = parent


class Tag:
    """
    A line beginning with "@" which can be used to filter which tests to run
    Can occur before a Feature, Background, Scenario, ScenarioOutline, or ExampleTable
    """

    def __init__(
        self,
        text: str,
        parent: Union['Feature', 'Scenario', 'ExampleTable'] = None,
    ):
        self.text = text if text.strip().startswith('@') else f'@{text}'
        self.parent = parent

    def __eq__(self, other):
        return self.text == other.text

    def __hash__(self):
        return hash(''.join([self.text, str(id(self.parent))]))

    @classmethod
    def from_text(
        cls,
        text: str,
        parent: Union['Feature', 'Scenario', 'ExampleTable'] = None,
    ):
        text = text.strip()
        if text.strip().startswith('@'):
            return cls(text=text, parent=parent)
        else:
            raise InvalidGherkinError(f'Tags must begin with "@": {text}')

    @classmethod
    def from_data(
        cls,
        data: Dict,
        parent: Union['Feature', 'Scenario', 'ExampleTable'] = None,
    ):
        return cls(text=data['name'], parent=parent)

    @property
    def text_without_at(self):
        return self.text.replace('@', '', 1)


class Comment:
    """
    A line beginning with "#"
    Inline comments are not allowed in Gherkin
    """

    def __init__(
        self,
        text: str,
        parent: Union['Feature', 'Scenario', 'Step', 'ExampleTable',
                      'ExampleTableRow'] = None,
    ):
        self.text = text
        self.parent = parent

    @classmethod
    def from_text(cls, text):
        text = text.strip()
        if text.strip().startswith('#'):
            return cls(text=text)
        else:
            # Note: Inline comments are not valid Gherkin
            raise InvalidGherkinError(f'Comments must begin with "#": {text}')

    def from_data(self, data):
        raise NotImplementedError


# Errors ----------------------------------------------------------------------


class InvalidGherkinError(Exception):
    pass


class UnknownStepTypeError(RuntimeError):
    pass


# Enums -----------------------------------------------------------------------


class ScenarioType(Enum):
    SCENARIO = 'Scenario'
    OUTLINE = 'Scenario Outline'
    BACKGROUND = 'Background'

    @property
    def keyword(self):
        return self.value

    @classmethod
    def from_string(cls, string):
        try:
            return cls(string)
        except ValueError:
            return None


class StepType(Enum):
    GIVEN = 'Given'
    WHEN = 'When'
    THEN = 'Then'

    @property
    def keyword(self):
        return self.value

    @classmethod
    def from_string(cls, string: str) -> Optional['StepType']:
        try:
            return cls(string.lower().capitalize())
        except (ValueError, AttributeError):
            return None


class StepKeyword(Enum):
    GIVEN = 'Given'
    WHEN = 'When'
    THEN = 'Then'
    AND = 'And'
    BUT = 'But'
    BULLET = '*'

    @property
    def keyword(self):
        return self.value

    @classmethod
    def from_string(cls, string: str):
        try:
            return cls(string.lower().capitalize())
        except (ValueError, AttributeError):
            return None


if __name__ == '__main__':
    data = Parser().parse(
        TokenScanner("""
        Feature: feature
        
        Scenario: scenario
        
        Given Step 1
        Given Step 2
        | data 1 |
        | data 2 |
    """))

    print(json.dumps(data, indent=2))
