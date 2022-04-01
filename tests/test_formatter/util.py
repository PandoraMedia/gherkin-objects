from __future__ import annotations
import os
import re
from gherkin_objects.formatter import FormatterConfig
import json
from typing import Dict
import unittest
from gherkin_objects.objects import *
from gherkin_objects.formatter import Formatter


class FormatComponentTest(unittest.TestCase):

    def setUp(self) -> None:
        self.config = Formatter.Config(
            feature=Formatter.Config.Feature(
                indent=0,
                blank_lines_before=0,
                blank_lines_after=0,
            ),
            feature_description=Formatter.Config.FeatureDescription(
                indent=0,
                blank_lines_before=0,
                preserve_relative_indentation=True,
                preserve_internal_empty_lines=True,
            ),
            scenario=Formatter.Config.Scenario(
                indent=0,
                blank_lines_before=0,
                blank_lines_before_steps=0,
            ),
            scenario_description=Formatter.Config.ScenarioDescription(
                indent=0,
                blank_lines_before=0,
                preserve_relative_indentation=True,
                preserve_internal_empty_lines=True,
            ),
            step=Formatter.Config.Step(
                indent=0,
                vertical_alignment=Formatter.Config.Step.VerticalAlignment.
                by_keyword,
                keyword_policy=Formatter.Config.Step.KeywordPolicy.prefer_raw,
            ),
            data_table=Formatter.Config.DataTable(
                indent=0,
                blank_lines_before=0,
                blank_lines_after=0,
                all_columns_same_width=False,
                padding_shared_with=Formatter.Config.DataTable.
                PaddingSharedWith.table,
                cell_left_padding=1,
                cell_right_padding=1,
                cell_min_width=0,
            ),
            example_table=Formatter.Config.ExampleTable(
                indent=0,
                indent_row=0,
                blank_lines_before=0,
                blank_lines_after=0,
                combine_tables_with_equivalent_tags=False,
                enforce_header_order=False,
                all_tables_in_outline_same_width=False,
                all_columns_in_row_same_width=False,
                cell_left_padding=1,
                cell_right_padding=1,
                cell_min_width=0,
            ),
            tag=Formatter.Config.Tag(
                ensure_scenario_uuid=False,
                ensure_feature_uuid=False,
                tag_order_top=[],
                tag_order_bottom=[],
                alphabetize_tags=False,
            ),
        )
        self.formatter = Formatter(self.config)

    def assert_lines_equal(self, lines_1: List[str], lines_2: List[str]):
        try:
            self.assertEqual('\n'.join(lines_1), '\n'.join(lines_2))
        except AssertionError:
            print('-' * 80)
            print('Expected:')
            print('-' * 80)
            print('\n'.join(lines_1))
            print('-' * 80)
            print('Actual:')
            print('-' * 80)
            print('\n'.join(lines_2))
            print('-' * 80)
            raise

    def assert_feature_formatted(self, input_lines: List[str],
                                 expected_lines: List[str]):
        feature = Feature.from_text('\n'.join(input_lines))
        formatted_lines = self.formatter.format_feature(feature)
        self.assert_lines_equal(expected_lines, formatted_lines)

    def assert_scenario_formatted(self, input_lines: List[str],
                                  expected_lines: List[str]):
        scenario = Scenario.from_text('\n'.join(input_lines))
        formatted_lines = self.formatter.format_scenario(scenario)
        self.assert_lines_equal(expected_lines, formatted_lines)

    def assert_steps_formatted(self, input_lines: List[str],
                               expected_lines: List[str]):
        steps = Step.multiple_from_text('\n'.join(input_lines))
        formatted_lines = self.formatter.format_steps(steps)
        self.assert_lines_equal(expected_lines, formatted_lines)

    def assert_table_formatted(self, input_lines: List[str],
                               expected_lines: List[str]):
        data_table = DataTable.from_text('\n'.join(input_lines))
        formatted_lines = self.formatter.format_data_table(data_table)
        self.assert_lines_equal(expected_lines, formatted_lines)

    def assert_example_table_formatted(self, input_lines: List[str],
                                       expected_lines: List[str]):
        table = ExampleTable.from_text('\n'.join(input_lines))
        formatted_lines = self.formatter.format_example_table(table)
        self.assert_lines_equal(expected_lines, formatted_lines)
