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

from gherkin_objects.objects import GherkinProject


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        this_file_path = os.path.abspath(__file__)
        this_file_dir = os.path.dirname(this_file_path)
        self.root = os.path.join(this_file_dir, 'temp')

    def tearDown(self) -> None:
        if os.path.exists(self.root):
            shutil.rmtree(self.root, ignore_errors=True)
        del self.root

    def make_path(self, path):
        return os.path.join(self.root, path)

    def make_temp_feature(self, path, text=None):
        dir = os.path.dirname(path)
        os.makedirs(dir, exist_ok=True)
        text = text or f'Feature: {path}'
        with open(path, 'w') as file:
            file.write(text)

    # Tests -------------------------------------------------------------------

    def test_gherkin_project_sanity(self):
        path1 = self.make_path('temp.feature')
        self.make_temp_feature(path1)
        project = GherkinProject(paths=[path1])

        self.assertEqual(len(project.paths), 1)
        self.assertEqual(len(project.feature_files), 1)
        self.assertIsNotNone(project.feature_files[0].feature)


if __name__ == '__main__':
    unittest.main()
