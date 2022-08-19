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

import os
import shutil
import unittest

from pathlib import Path

from gherkin_objects.objects import GherkinProjectConfig


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        self.path = os.path.join(self.temp_dir, 'test.json')
        os.makedirs(self.temp_dir)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_config_sanity(self):
        config = GherkinProjectConfig(
            path=self.path,
            include=['./**/*.feature'],
            exclude=['/dev/null'],
        )
        config.save()
        config2 = config.load(self.path)

        self.assertSequenceEqual(config.include, config2.include)
        self.assertSequenceEqual(config.exclude, config2.exclude)
        self.assertEqual(config.paths, [])

    def test_config_relative_path_with_dot(self):
        config = GherkinProjectConfig(
            path=self.path,
            include=['./feature1.feature'],
            exclude=['./feature2.feature'],
        )
        path1 = Path(os.path.join(self.temp_dir, 'feature1.feature'))
        path2 = Path(os.path.join(self.temp_dir, 'feature2.feature'))
        path1.touch()
        path2.touch()

        self.assertEqual(config.paths, [str(path1)])


if __name__ == '__main__':
    unittest.main()
