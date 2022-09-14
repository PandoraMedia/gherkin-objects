import os
from glob import glob
from gherkin_objects.objects import GherkinProject


this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, 'data')
example_dir = os.path.join(data_dir, 'project_demo')
example_feature_paths = glob(f'{example_dir}/*.feature')

print(example_dir)
print(example_feature_paths)

project = GherkinProject(paths=example_feature_paths)

for feature in project.features:
    print(f'{feature.name} has {len(feature.scenarios)} scenarios')
