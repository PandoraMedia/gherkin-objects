from gherkin_objects.objects import Feature, Scenario, ScenarioType, Step, StepType, Tag, StepKeyword
from gherkin_objects.formatter import Formatter, FormatterConfig

formatter = Formatter(FormatterConfig())

feature = Feature(
    name='from scratch',
    description='This feature file was created from scratch directly from python',
    tags=[Tag(f'tag{i}') for i in range(10)],
    scenarios=[
        Scenario(scenario_type=ScenarioType.SCENARIO, name='Look at me', steps=[
            Step(keyword=StepKeyword.GIVEN, text='something cool')
        ])
    ])

print('-' * 80)
print('\n'.join(formatter.format_feature(feature)))
print('-' * 80)
