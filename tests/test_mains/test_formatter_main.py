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
import shutil
import tempfile
from scripts.format_gherkin import main_from_args
from tests.resources.configs import test_formatter_config_path
from gherkin_objects.formatter import Formatter
from gherkin_objects.objects import GherkinProjectConfig, FeatureFile, Feature


class TestFormatterMain(unittest.TestCase):
    # Lifecycle

    @classmethod
    def setUpClass(cls) -> None:
        cls.unformatted_text = '''
        Feature: feature
        Scenario: scenario
        Given step 1
        '''
        cls.config = Formatter.Config.load(test_formatter_config_path)
        cls.config.tag.ensure_feature_uuid = False
        cls.config.tag.ensure_scenario_uuid = False
        cls.config.save(test_formatter_config_path)
        cls.formatter = Formatter(cls.config)
        cls.formatted_text = '\n'.join(
            cls.formatter.format_feature(
                Feature.from_text(cls.unformatted_text)))

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.temp_project_config_path = tempfile.mktemp(suffix='.project.json',
                                                        dir=self.temp_dir)
        self.temp_feature_file_path = tempfile.mktemp(suffix='.feature',
                                                      dir=self.temp_dir)

        self.temp_project_config = GherkinProjectConfig(
            path=self.temp_project_config_path,
            include=[self.temp_feature_file_path],
        )
        self.temp_project_config.save()

        self.write_temp_feature_file(self.unformatted_text)

        self.temp_feature_file = FeatureFile(path=self.temp_feature_file_path)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    # Utils

    def read_temp_feature_file(self) -> str:
        with open(self.temp_feature_file_path) as f:
            return f.read()

    def write_temp_feature_file(self, text: str) -> None:
        with open(self.temp_feature_file_path, 'w') as f:
            f.write(text)

    # Tests

    def test_formatter_main_apply(self):
        self.assertNotEqual(self.unformatted_text, self.formatted_text,
                            "The test feature is already formatted")

        contents_before_call = self.read_temp_feature_file()
        self.assertEqual(contents_before_call, self.unformatted_text)

        main_from_args([
            self.temp_project_config_path, test_formatter_config_path,
            '--apply'
        ])

        contents_after_call = self.read_temp_feature_file()
        self.assertEqual(contents_after_call, self.formatted_text)

    def test_formatter_main_diff(self):
        self.write_temp_feature_file(self.formatted_text)

        main_from_args([
            self.temp_project_config_path, test_formatter_config_path, '--diff'
        ])

    def test_formatter_main_check_fail(self):
        with open(self.temp_feature_file_path) as f:
            contents_before_call = f.read()

        with self.assertRaises(SystemExit):
            main_from_args([
                self.temp_project_config_path, test_formatter_config_path,
                '--check'
            ])

        with open(self.temp_feature_file_path) as f:
            contents_after_call = f.read()

        # --check shouldn't make any changes to the file
        self.assertEqual(contents_before_call, contents_after_call)

    def test_formatter_main_check_pass(self):
        formatter = Formatter(
            config=Formatter.Config.load(test_formatter_config_path))
        with open(self.temp_feature_file_path) as f:
            unformatted = f.read()

        formatted = '\n'.join(
            formatter.format_feature(Feature.from_text(unformatted)))
        with open(self.temp_feature_file_path, 'w') as f:
            f.write(formatted)

        main_from_args([
            self.temp_project_config_path, test_formatter_config_path,
            '--check'
        ])

        with open(self.temp_feature_file_path) as f:
            contents_after_call = f.read()

        # --check shouldn't make any changes to the file
        self.assertEqual(contents_after_call, formatted)


if __name__ == '__main__':
    unittest.main()
