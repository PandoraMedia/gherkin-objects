from typing import Dict
import os
from glob import glob
from gherkin_objects.objects import GherkinProject, Feature, Tag
from gherkin_objects.formatter import FormatterConfig, Formatter

formatter = Formatter(FormatterConfig())


this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, 'data')
example_dir = os.path.join(data_dir, 'project_demo')
output_dir = os.path.join(example_dir, 'with_added_tags')
os.makedirs(output_dir, exist_ok=True)
example_feature_paths = glob(f'{example_dir}/*.feature')

print(example_dir)
print(example_feature_paths)

project = GherkinProject(paths=example_feature_paths)

for feature in project.features:
    print(f'{feature.name} has {len(feature.scenarios)} scenarios')

features_by_name: Dict[str, Feature] = {feature.name: feature for feature in project.features}
foo_feature = features_by_name['Foo']
bar_feature = features_by_name['Bar']

foo_feature.tags.append(Tag('@foo_feature'))
for scenario in foo_feature.scenarios:
    scenario.tags.append(Tag('@foo_scenario'))

bar_feature.tags.append(Tag('@bar_feature'))
for scenario in bar_feature.scenarios:
    scenario.tags.append(Tag('@bar_scenario'))

foo_filename = os.path.basename(foo_feature.parent_feature_file.path)
foo_output_path = os.path.join(output_dir, foo_filename)
with open(foo_output_path, 'w') as f:
    formatted_lines = formatter.format_feature(foo_feature)
    f.write('\n'.join(formatted_lines))

bar_filename = os.path.basename(bar_feature.parent_feature_file.path)
bar_output_path = os.path.join(output_dir, bar_filename)
with open(bar_output_path, 'w') as f:
    formatted_lines = formatter.format_feature(bar_feature)
    formatted_text = '\n'.join(formatted_lines)
    bar_formatted_feature = Feature.from_text(formatted_text)
    f.write('\n'.join(formatted_lines))
