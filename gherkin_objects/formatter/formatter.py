from __future__ import annotations

import logging
import re
import unicodedata
import uuid

from collections import defaultdict
from functools import lru_cache
from itertools import zip_longest
from typing import List, Dict, Optional, Tuple, FrozenSet

from gherkin_objects.objects import (
    DataTable,
    ExampleTable,
    ExampleTableRow,
    Feature,
    Scenario,
    Step
)

from .formatter_config import FormatterConfig

logger = logging.getLogger(__package__)


def _indent(level: int) -> str:
    return ' ' * level


def _blank_lines(count: int) -> List[str]:
    return ['' for _ in range(count)]


def _is_blank(line: str) -> bool:
    return re.fullmatch(r'^\s*$', line) is not None


def _leading_spaces(line: str) -> int:
    """Return the number of leading spaces in the line"""
    line = _normalize_whitespace(line)
    for i, char in enumerate(line):
        if char != ' ':
            return i
    return len(line)


def _normalize_whitespace(line: str) -> str:
    """Strip any newline characters, and convert tabs to spaces"""
    result = line
    result = result.replace('\n', '')
    result = result.replace('\t', ' ' * 4)
    return result


def _common_indentation(lines: List[str],
                        ignore_blank_lines: bool = True) -> int:
    """Given a set of lines with some leading whitespace, return the number of spaces in the line with the least leading whitespace"""
    lines = [_normalize_whitespace(line) for line in lines]

    if ignore_blank_lines:
        lines = [line for line in lines if not _is_blank(line)]

    return min([_leading_spaces(line) for line in lines])


def _transpose(array: List[List]) -> List[List]:
    return list(map(list, zip_longest(*array)))


class Formatter:
    Config = FormatterConfig

    def __init__(self, config: Config):
        self.config = config

    # Feature -----------------------------------------------------------------

    def format_feature(self, feature: Feature) -> List[str]:
        lines = []

        lines += _blank_lines(self.config.feature.blank_lines_before)
        lines += self.format_feature_tags(feature)
        lines += self.format_feature_title(feature)
        lines += self.format_feature_description(feature)
        lines += self.format_feature_scenarios(feature)
        lines += _blank_lines(self.config.feature.blank_lines_after)

        # Normalize the text, to remove chars like NBSP that trip the glue generator
        # https://docs.python.org/3.8/library/unicodedata.html#unicodedata.normalize
        lines = [unicodedata.normalize('NFKC', x) for x in lines]

        return lines

    def format_feature_title(self, feature: Feature) -> List[str]:
        return [f'{_indent(self.config.feature.indent)}{feature.title_text}']

    def format_feature_scenarios(self, feature: Feature) -> List[str]:
        lines = []

        if feature.background:
            lines += self.format_scenario(feature.background)

        scenarios = [
            scenario for scenario in feature.scenarios
            if not scenario.is_background
        ]
        for scenario in scenarios:
            lines.extend(self.format_scenario(scenario))

        return lines

    # Tags --------------------------------------------------------------------

    @staticmethod
    def _add_uuid_if_necessary(tags: List[str], prefix: str) -> List[str]:
        if not any([tag.startswith(prefix) for tag in tags]):
            tags += [f'{prefix}{uuid.uuid4()}']
        return tags

    def format_feature_tags(self, feature: Feature) -> List[str]:
        tags = [tag.text for tag in feature.tags]

        if self.config.tag.ensure_feature_uuid:
            tags = self._add_uuid_if_necessary(tags=tags,
                                               prefix='@feature_uuid:')

        return self.format_tags(tags=tags, indent=self.config.feature.indent)

    def format_scenario_tags(self, scenario: Scenario) -> List[str]:
        tags = [tag.text for tag in scenario.tags]

        if self.config.tag.ensure_scenario_uuid and not scenario.is_scenario_outline:
            if scenario.is_background:
                pass  # Backgrounds don't have tags
            elif scenario.name.lower() == 'placeholder':
                pass  # Placeholder scenarios don't need tags
            elif scenario.is_scenario_outline:
                pass  # Each row needs its own tag
            else:
                tags = self._add_uuid_if_necessary(tags=tags, prefix='@uuid:')

        return self.format_tags(tags=tags, indent=self.config.scenario.indent)

    def format_example_table_tags(self, table: ExampleTable) -> List[str]:
        tags = [tag.text for tag in table.tags]

        if self.config.tag.ensure_scenario_uuid:
            tags = self._add_uuid_if_necessary(tags=tags, prefix='@uuid:')

        return self.format_tags(tags=tags,
                                indent=self.config.example_table.indent)

    def format_tags(
        self,
        tags: List[str],
        indent: int,
    ) -> List[str]:
        if not tags:
            return []

        # UUIDs are always the bottom-most tag, remove them from the set of tags to be reordered
        feature_uuid = None
        scenario_uuid = None
        tags_without_uuid = []
        for tag in list(tags):
            if tag.startswith('@uuid:'):
                scenario_uuid = tag
            elif tag.startswith('@feature_uuid:'):
                feature_uuid = tag
            else:
                tags_without_uuid.append(tag)
        tags = tags_without_uuid

        lines = []
        tag_set = set(tags)

        # Top tags

        for tag_list in self.config.tag.tag_order_top:
            line_tags = []
            for tag in tag_list:
                if tag in tag_set:
                    line_tags.append(tag)
            if line_tags:
                lines += [f'{_indent(indent)}{" ".join(line_tags)}']

        # Middle tags

        middle_tags = [
            tag for tag in tags if tag not in self.config.tag.top_tags
            and tag not in self.config.tag.bottom_tags
        ]
        if self.config.tag.alphabetize_tags:
            middle_tags.sort()

        for tag in middle_tags:
            lines.append(f'{_indent(indent)}{tag}')

        # Bottom Tags

        for tag_list in self.config.tag.tag_order_bottom:
            line_tags = []
            for tag in tag_list:
                if tag in tag_set:
                    line_tags.append(tag)
            if line_tags:
                lines += [f'{_indent(indent)}{" ".join(line_tags)}']

        # UUIDs are always the bottom-most tag

        if feature_uuid:
            lines += [f'{_indent(indent)}{feature_uuid}']
        if scenario_uuid:
            lines += [f'{_indent(indent)}{scenario_uuid}']

        return lines

    # Descriptions ------------------------------------------------------------

    def format_feature_description(self, feature: Feature) -> List[str]:
        return self.format_description(
            description=feature.description,
            indent_level=self.config.feature_description.indent,
            blank_lines_before=self.config.feature_description.
            blank_lines_before,
            preserve_relative_indentation=self.config.feature_description.
            preserve_relative_indentation,
            preserve_internal_empty_lines=self.config.feature_description.
            preserve_internal_empty_lines,
        )

    def format_scenario_description(self, scenario: Scenario) -> List[str]:
        return self.format_description(
            description=scenario.description,
            indent_level=self.config.scenario_description.indent,
            blank_lines_before=self.config.scenario_description.
            blank_lines_before,
            preserve_relative_indentation=self.config.scenario_description.
            preserve_relative_indentation,
            preserve_internal_empty_lines=self.config.scenario_description.
            preserve_internal_empty_lines,
        )

    def format_description(
        self,
        description: Optional[str],
        indent_level: int,
        blank_lines_before: int,
        preserve_relative_indentation: bool,
        preserve_internal_empty_lines: bool,
    ) -> List[str]:
        if not description:
            return []

        lines = description.split('\n')
        lines = [_normalize_whitespace(line) for line in lines]
        lines = [line.rstrip() for line in lines]

        if preserve_relative_indentation:
            # Remove only minimum common whitespace from each line
            common_indentation = _common_indentation(lines)
            common_indentation_string = ' ' * common_indentation
            lines = [
                re.sub(rf'^{common_indentation_string}', '', line, count=1)
                for line in lines
            ]
        else:
            # Remove all leading whitespace
            lines = [line.lstrip() for line in lines]

        # Remove empty lines if necessary
        if not preserve_internal_empty_lines:
            lines = [line for line in lines if not _is_blank(line)]
        else:
            # Replace whitespace only lines with empty lines so that we don't get empty lines that are over indented
            lines = ['' if _is_blank(line) else line for line in lines]

        # Add indentation to each line
        lines = [f'{_indent(indent_level)}{line}' for line in lines]

        # Add blank lines before description
        lines = _blank_lines(blank_lines_before) + lines

        return lines

    # Scenario ----------------------------------------------------------------

    def format_scenario(self, scenario: Scenario) -> List[str]:
        lines = []

        lines += _blank_lines(self.config.scenario.blank_lines_before)
        lines += self.format_scenario_tags(scenario)
        lines += self.format_scenario_title(scenario)
        lines += self.format_scenario_description(scenario)
        lines += _blank_lines(self.config.scenario.blank_lines_before_steps)
        lines += self.format_scenario_steps(scenario)
        lines += self.format_scenario_example_tables(scenario)

        return lines

    def format_scenario_title(self, scenario: Scenario) -> List[str]:
        return [
            f'{_indent(self.config.scenario.indent)}{scenario.title_text.strip()}'
        ]

    def format_scenario_steps(self, scenario: Scenario) -> List[str]:
        return self.format_steps(scenario.steps)

    def format_scenario_example_tables(self, scenario: Scenario) -> List[str]:
        if not scenario.is_scenario_outline:
            return []
        else:
            return self.format_example_tables(scenario.tables)

    # Steps -------------------------------------------------------------------

    def format_steps(self, steps: List[Step]) -> List[str]:
        lines = []
        for step in steps:
            lines.extend(self.format_step(step, group=tuple(steps)))
        return lines

    def format_step(self,
                    step: Step,
                    group: Optional[Tuple[Step, ...]] = None) -> List[str]:
        if group is not None:
            index = group.index(step)
            raw_keywords = self.raw_keywords(group)
        else:
            index = 0
            raw_keywords = step.real_keyword

        step_keyword = raw_keywords[index]

        # If vertically aligning by step text, add some leading whitespace to the left of the keyword
        if self.config.step.vertical_alignment == self.config.Step.VerticalAlignment.by_step_text:
            length_of_longest_raw_keyword = max(
                [len(keyword) for keyword in raw_keywords])
            padding = ' ' * abs(
                len(step_keyword) - length_of_longest_raw_keyword)
            step_keyword = padding + step_keyword

        lines = []
        lines += [
            f'{_indent(self.config.step.indent)}{step_keyword} {step.text_without_keyword.strip()}'
        ]
        if step.data_table is not None:
            lines += self.format_data_table(step.data_table)
        return lines

    @lru_cache(maxsize=1)
    def raw_keywords(self, steps: Tuple[Step]) -> List[str]:
        """Generate the list of keywords to use given the config.
        This method resolves which steps should use the 'And' or '*' keywords"""
        if self.config.step.keyword_policy == FormatterConfig.Step.KeywordPolicy.prefer_raw:
            return [step.raw_keyword for step in steps]

        if self.config.step.keyword_policy == FormatterConfig.Step.KeywordPolicy.prefer_real:
            return [step.real_keyword for step in steps]

        previous_real_keyword = None
        result = []
        for keyword in [step.real_keyword for step in steps]:
            if keyword == previous_real_keyword:
                if self.config.step.keyword_policy == FormatterConfig.Step.KeywordPolicy.prefer_and:
                    result.append('And')
                elif self.config.step.keyword_policy == FormatterConfig.Step.KeywordPolicy.prefer_bullet:
                    result.append('*')
                else:
                    raise ValueError(
                        f'Unhandled keyword policy: {self.config.step.keyword_policy.name}'
                    )
            else:
                previous_real_keyword = keyword
                result.append(keyword)
        return result

    # Data Tables -------------------------------------------------------------

    def format_data_table(self, table: DataTable) -> List[str]:
        if not table.rows:
            return []

        column_widths: List[List[int]] = []
        max_column_widths: List[int] = []
        max_column_width: int = 0

        if self.config.data_table.padding_shared_with is not None:
            column_widths = self.data_table_column_widths(
                tuple(self.relevant_data_tables(table)))
            max_column_widths = [max(widths) for widths in column_widths]
            max_column_width = max(max_column_widths)

        lines = _blank_lines(self.config.data_table.blank_lines_before)
        for row in table.rows:
            if self.config.data_table.padding_shared_with is None:
                column_widths = [[len(cell)] for cell in row]
                max_column_widths = [max(widths) for widths in column_widths]
                max_column_width = max(max_column_widths)

            line = _indent(self.config.data_table.indent)
            for i, value in enumerate(row):
                if self.config.data_table.all_columns_same_width:
                    width = max_column_width
                else:
                    width = max_column_widths[i]
                width = max(width, self.config.data_table.cell_min_width)
                value_padding = ' ' * abs(width - len(value))

                line += '|'
                line += ' ' * self.config.data_table.cell_left_padding
                line += value
                line += value_padding
                line += ' ' * self.config.data_table.cell_right_padding
            line += '|'
            lines.append(line)
        lines += _blank_lines(self.config.data_table.blank_lines_after)
        return lines

    def relevant_data_tables(self, table: DataTable) -> List[DataTable]:
        if self.config.data_table.padding_shared_with == self.config.DataTable.PaddingSharedWith.table:
            return [table]

        if self.config.data_table.padding_shared_with == self.config.DataTable.PaddingSharedWith.scenario:
            if not table.parent_scenario:
                raise RuntimeError('Cannot access scenario for table')
            return [
                step.data_table for step in table.parent_scenario.steps
                if step.data_table
            ]

        if self.config.data_table.padding_shared_with == self.config.DataTable.PaddingSharedWith.feature:
            if not table.parent_feature:
                raise RuntimeError('Cannot access feature for table')
            return [
                step.data_table for scenario in table.parent_feature.scenarios
                for step in scenario.steps if step.data_table
            ]

        raise ValueError(
            f'Unknown enum value: {self.config.data_table.padding_shared_with}'
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def data_table_column_widths(
            tables: Tuple[DataTable, ...]) -> List[List[int]]:
        result = []

        for table in tables:
            result.extend([[len(cell) for cell in row] for row in table.rows])
        return _transpose(result)

    # Example Tables ----------------------------------------------------------

    def format_example_tables(self, tables: List[ExampleTable]) -> List[str]:
        if self.config.example_table.enforce_header_order:
            for table in tables:
                self.enforce_header_order(table)

        if self.config.tag.ensure_scenario_uuid:
            tables = self.split_tables_into_one_row_per_table(tables)
        elif self.config.example_table.combine_tables_with_equivalent_tags:
            tables = self.combine_tables_with_equivalent_tags(tables)

        lines = []
        for table in tables:
            lines.extend(self.format_example_table(table, group=tables))
        return lines

    def format_example_table(self,
                             table: ExampleTable,
                             group: List[ExampleTable] = None) -> List[str]:
        group = group or []
        group += [table] if table not in group else []

        # Determine which set of widths to use to decide the width of each column in this table
        if self.config.example_table.all_tables_in_outline_same_width:
            # If we want all tables to have the same width, we need to look at the entire group
            column_widths = self.column_widths(group)
        else:
            # If we want each table to have its own widths, just look at the widths of that table
            column_widths = self.column_widths([table])

        # The width of each column must be at least as wide as its widest member
        column_width: Dict[str, int] = {
            name: max(column_widths[name])
            for name in column_widths.keys()
        }

        # If all columns need to be the same size, we need to use the width of the widest column
        if self.config.example_table.all_columns_in_row_same_width:
            column_width = {
                name: max(column_width.values())
                for name in column_width.keys()
            }

        # Ensure each column is at least as wide as cell_min_width
        min_width = self.config.example_table.cell_min_width
        column_width = {
            name: max(width, min_width)
            for name, width in column_width.items()
        }

        lines = []
        lines += _blank_lines(self.config.example_table.blank_lines_before)
        lines += self.format_example_table_tags(table)
        lines += self.format_example_table_keyword()
        for row in table.rows:
            line = _indent(self.config.example_table.indent_row)
            for i, cell in enumerate(row.cells):
                column_name = table.column_names[i]
                width = column_width[column_name]
                line += '|'
                line += ' ' * self.config.example_table.cell_left_padding
                line += cell.value
                line += ' ' * abs(width - len(cell.value))
                line += ' ' * self.config.example_table.cell_right_padding
            line += '|'
            lines.append(line)
        lines += _blank_lines(self.config.example_table.blank_lines_after)
        return lines

    def format_example_table_keyword(self) -> List[str]:
        return [f'{_indent(self.config.example_table.indent)}Examples:']

    @staticmethod
    def unique_parameters_in_order(scenario: Scenario) -> List[str]:
        parameters = []
        for step in scenario.steps:
            for parameter in step.parameters:
                if parameter not in parameters:
                    parameters.append(parameter)
        return parameters

    @staticmethod
    def enforce_header_order(table: ExampleTable) -> None:
        if table.parent_scenario is None:
            logger.warning('Cannot access table parent')
            return

        parameters = []
        for step in table.parent_scenario.steps:
            for parameter in step.parameters:
                if parameter not in parameters:
                    parameters.append(parameter)

        names = table.column_names
        old_name_index = {
            name: table.column_names.index(name)
            for name in names
        }

        old_header_row = table.header_row
        new_header_row = ExampleTableRow(cells=[
            old_header_row.cells[old_name_index[parameter]]
            for parameter in parameters
        ])

        old_data_rows = table.data_rows
        new_data_rows = [
            ExampleTableRow(cells=[
                old_data_row.cells[old_name_index[parameter]]
                for old_data_row in old_data_rows for parameter in parameters
            ])
        ]

        table.header_row = new_header_row
        table.data_rows = new_data_rows

    @staticmethod
    def split_tables_into_one_row_per_table(
            tables: List[ExampleTable]) -> List[ExampleTable]:
        result = []
        for table in tables:
            for data_row in table.data_rows:
                result.append(
                    ExampleTable(header_row=table.header_row,
                                 data_rows=[data_row],
                                 tags=table.tags,
                                 parent=table.parent))
        return result

    @staticmethod
    def combine_tables_with_equivalent_tags(
            tables: List[ExampleTable]) -> List[ExampleTable]:
        table_by_tags: Dict[FrozenSet[str], ExampleTable] = {}

        result = []
        for table in tables:
            tags = frozenset([tag.text for tag in table.tags])
            if tags not in table_by_tags:
                result.append(table)
                table_by_tags[tags] = table
            else:
                table_by_tags[tags].data_rows.extend(table.data_rows)
        return result

    @staticmethod
    def column_widths(tables: List[ExampleTable]) -> Dict[str, List[int]]:
        column_widths = defaultdict(list)
        for table in tables:
            for i, name in enumerate(table.column_names):
                column_widths[name].extend(
                    [len(row.cells[i].value) for row in table.rows])
        return dict(column_widths)
