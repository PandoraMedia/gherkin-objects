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

import json
import os
import tempfile
import unittest

import yaml

from gherkin_objects.formatter.formatter_config import FormatterConfig


class TestGherkinFormatterConfigIO(unittest.TestCase):

    def test_save_as_json(self):
        """If the extension is .json save as json"""
        path = tempfile.mktemp(suffix='.json')
        config = FormatterConfig()

        self.assertFalse(os.path.exists(path))
        config.save(path)
        self.assertTrue(os.path.exists(path))

        # Assert that the data is actually in json format
        with open(path) as f:
            loaded_data = json.loads(f.read())
        self.assertEqual(config.to_json(), loaded_data)

    def test_save_as_yaml(self):
        """If the extension is .yaml save as yaml"""
        path = tempfile.mktemp(suffix='.yaml')
        config = FormatterConfig()

        self.assertFalse(os.path.exists(path))
        config.save(path)
        self.assertTrue(os.path.exists(path))

        # Assert that the data is actually in yaml format
        with open(path) as f:
            loaded_data = yaml.load(f.read(), Loader=yaml.Loader)
        self.assertEqual(config.to_json(), loaded_data)

    def test_save_as_txt(self):
        """The default format to save is yaml if the format cannot be inferred from the extension"""
        path = tempfile.mktemp(suffix='.txt')
        config = FormatterConfig()

        # Given the .txt file doesn't exist
        self.assertFalse(os.path.exists(path))

        # When the config is saved to the .txt file
        config.save(path)
        self.assertTrue(os.path.exists(path))

        # Then the .txt file should contain the config in yaml format
        with open(path) as f:
            loaded_data = yaml.load(f.read(), Loader=yaml.Loader)
        self.assertEqual(config.to_json(), loaded_data)

    def test_save_load___json(self):
        """No data should be lost or changed on a round trip to the disk"""
        path = tempfile.mktemp(suffix='.json')
        config = FormatterConfig()

        config.save(path)
        config_from_json = FormatterConfig.load(path)
        self.assertEqual(config, config_from_json,
                         'Loaded json config did not match saved json config')

    def test_save_load___yaml(self):
        """No data should be lost or changed on a round trip to the disk"""
        path = tempfile.mktemp(suffix='.yaml')
        config = FormatterConfig()

        config.save(path)
        config_from_yaml = FormatterConfig.load(path)
        self.assertEqual(config, config_from_yaml,
                         'Loaded yaml config did not match saved yaml config')


if __name__ == '__main__':
    unittest.main()
