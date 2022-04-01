import os
from gherkin_objects.formatter import FormatterConfig, Formatter

test_formatter_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'configs', 'test.format.yaml')
test_formatter_config = FormatterConfig.load(test_formatter_config_path)
test_formatter = Formatter(test_formatter_config)
