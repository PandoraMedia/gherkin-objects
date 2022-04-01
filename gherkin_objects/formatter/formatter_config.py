from __future__ import annotations

import json
import logging

from enum import Enum, auto
from json.decoder import JSONDecodeError
from dataclasses import dataclass
from abc import ABC
from typing import List, Dict, Any, Optional, Type, TypeVar, Set

import yaml

E = TypeVar('E', bound=Enum)
Class = TypeVar('Class')

logger = logging.getLogger(__package__)


def load_enum_from_name(name: str, enum: Type[E]) -> E:
    try:
        return enum[name]
    except KeyError as e:
        raise KeyError(
            f'Invalid name supplied for {enum.__name__}. Options are {[member.name for member in enum]}.'
        ) from e


class Config(ABC):

    def to_json(self) -> Dict:
        result = {}
        for key in vars(self):
            value = self.__getattribute__(key)
            if isinstance(value, Enum):
                value = value.name
            if isinstance(value, Config):
                value = value.to_json()
            result[key] = value
        return result

    @classmethod
    def _load_object(cls: Type[Class], key: str, value: Any,
                     instance: Class) -> bool:
        """
        This function is used when the value loaded from the JSON is not a primitive,
        the `value` should be set in the `instance` using the __setattr__ function.
        return true if the key/value pair was correctly handled, otherwise return false
        """
        return False

    @classmethod
    def from_json(cls, data: Dict[str, Any]):  # -> cls
        result = cls()
        class_attributes = list(vars(cls()))
        for key in data.keys():
            if key not in class_attributes:
                raise AttributeError(
                    f'Unrecognized config option "{key}" for "{cls.__name__}". Known options: {class_attributes}'
                )

            # This line is used to determine the type of the target attribute.  There is probably a better way to do this
            default_value = result.__getattribute__(key)
            value = data[key]
            if isinstance(default_value, (int, str, bool)) or value is None:
                result.__setattr__(key, value)
            else:
                if not cls._load_object(key=key, value=value, instance=result):
                    raise ValueError(
                        f'Failed to load {key} from JSON, got {value}')
        return result


@dataclass
class FeatureConfig(Config):
    indent: int = 0
    blank_lines_before: int = 0
    blank_lines_after: int = 1


@dataclass
class FeatureDescriptionConfig(Config):
    indent: int = 2
    blank_lines_before: int = 0
    preserve_relative_indentation: bool = True
    preserve_internal_empty_lines: bool = True


@dataclass
class ScenarioConfig(Config):
    indent: int = 4
    blank_lines_before: int = 2
    blank_lines_before_steps: int = 1


@dataclass
class ScenarioDescriptionConfig(Config):
    indent: int = 6
    blank_lines_before: int = 0
    preserve_relative_indentation: bool = True
    preserve_internal_empty_lines: bool = True


@dataclass
class StepConfig(Config):

    class VerticalAlignment(Enum):
        by_keyword = auto()
        by_step_text = auto()

    class KeywordPolicy(Enum):
        prefer_raw = auto()
        prefer_real = auto()
        prefer_and = auto()
        prefer_bullet = auto()

    indent: int = 8
    vertical_alignment: VerticalAlignment = VerticalAlignment.by_keyword
    keyword_policy: KeywordPolicy = KeywordPolicy.prefer_and

    @classmethod
    def _load_object(cls: Type[Class], key: str, value: Any,
                     instance: Class) -> bool:
        if key == 'vertical_alignment':
            value = load_enum_from_name(name=value,
                                        enum=StepConfig.VerticalAlignment)
            instance.__setattr__(key, value)
            return True
        if key == 'keyword_policy':
            value = load_enum_from_name(name=value,
                                        enum=StepConfig.KeywordPolicy)
            instance.__setattr__(key, value)
            return True
        return False


@dataclass
class DataTableConfig(Config):

    class PaddingSharedWith(Enum):
        table = auto()
        scenario = auto()
        feature = auto()

    indent: int = 10
    blank_lines_before: int = 0
    blank_lines_after: int = 0
    all_columns_same_width: bool = False
    padding_shared_with: Optional[PaddingSharedWith] = PaddingSharedWith.table
    cell_left_padding: int = 1
    cell_right_padding: int = 1
    cell_min_width: int = 0

    @classmethod
    def _load_object(cls: Type[Class], key: str, value: Any,
                     instance: Class) -> bool:
        if key == 'padding_shared_with':
            value = load_enum_from_name(name=value,
                                        enum=DataTableConfig.PaddingSharedWith)
            instance.__setattr__(key, value)
            return True
        return False


@dataclass
class ExampleTableConfig(Config):
    indent: int = 8
    indent_row: int = 10
    blank_lines_before: int = 1
    blank_lines_after: int = 0
    combine_tables_with_equivalent_tags: bool = True
    enforce_header_order: bool = False
    all_tables_in_outline_same_width: bool = True
    all_columns_in_row_same_width: bool = True
    cell_left_padding: int = 1
    cell_right_padding: int = 1
    cell_min_width: int = 0


@dataclass
class TagConfig(Config):
    ensure_scenario_uuid: bool = False
    ensure_feature_uuid: bool = False
    tag_order_top: List[List[str]] = None
    tag_order_bottom: List[List[str]] = None
    alphabetize_tags: bool = False

    def __post_init__(self):
        self.tag_order_top = self.tag_order_top or [[]]
        self.tag_order_bottom = self.tag_order_bottom or [[]]

    @classmethod
    def _load_object(cls: Type[Class], key: str, value: Any,
                     instance: Class) -> bool:
        if key in ['tag_order_top', 'tag_order_bottom']:
            instance.__setattr__(key, value)
            return True
        return False

    @property
    def top_tags(self) -> Set[str]:
        if self.tag_order_top:
            return set(
                [tag for tag_list in self.tag_order_top for tag in tag_list])
        else:
            return set()

    @property
    def bottom_tags(self) -> Set[str]:
        if self.tag_order_bottom:
            return set([
                tag for tag_list in self.tag_order_bottom for tag in tag_list
            ])
        else:
            return set()


class FormatterConfig(Config):
    Feature = FeatureConfig
    FeatureDescription = FeatureDescriptionConfig
    Scenario = ScenarioConfig
    ScenarioDescription = ScenarioDescriptionConfig
    Step = StepConfig
    DataTable = DataTableConfig
    ExampleTable = ExampleTableConfig
    Tag = TagConfig

    def __init__(
        self,
        feature: FeatureConfig = None,
        feature_description: FeatureDescription = None,
        scenario: ScenarioConfig = None,
        scenario_description: ScenarioDescriptionConfig = None,
        step: StepConfig = None,
        data_table: DataTableConfig = None,
        example_table: ExampleTableConfig = None,
        tag: TagConfig = None,
    ):
        self.feature = feature or self.Feature()
        self.feature_description = feature_description or self.FeatureDescription(
        )
        self.scenario = scenario or self.Scenario()
        self.scenario_description = scenario_description or self.ScenarioDescription(
        )
        self.step = step or self.Step()
        self.data_table = data_table or self.DataTable()
        self.example_table = example_table or self.ExampleTable()
        self.tag = tag or self.Tag()

    def __eq__(self, other):
        if not isinstance(other, FormatterConfig):
            return False
        return self.to_json() == other.to_json()

    @classmethod
    def _load_object(cls: Type[Class], key: str, value: Any,
                     instance: Class) -> bool:
        config_types: Dict[str, Type[Config]] = {
            'feature': FeatureConfig,
            'feature_description': FeatureDescriptionConfig,
            'scenario': ScenarioConfig,
            'scenario_description': ScenarioDescriptionConfig,
            'step': StepConfig,
            'data_table': DataTableConfig,
            'example_table': ExampleTableConfig,
            'tag': TagConfig,
        }

        try:
            config_type = config_types[key]
            value = config_type.from_json(value)
            instance.__setattr__(key, value)
            return True
        except KeyError:
            return False

    @property
    def json_text(self) -> str:
        return json.dumps(self.to_json(), indent=2)

    @property
    def yaml_text(self) -> str:
        return yaml.dump(self.to_json(), Dumper=yaml.Dumper)

    def save(self, path: str) -> None:
        with open(path, 'w') as f:
            if path.endswith('.yaml'):
                f.write(self.yaml_text)
            elif path.endswith('.json'):
                f.write(self.json_text)
            else:
                f.write(self.yaml_text)

    @classmethod
    def from_json_text(cls, text: str) -> FormatterConfig:
        return cls.from_json(json.loads(text))

    @classmethod
    def from_yaml_text(cls, text: str) -> FormatterConfig:
        return cls.from_json(yaml.load(stream=text, Loader=yaml.Loader))

    @classmethod
    def from_text(cls, text: str) -> FormatterConfig:
        exceptions = []

        try:
            return cls.from_json_text(text)
        except JSONDecodeError as e:
            exceptions.append(e)

        try:
            return cls.from_yaml_text(text)
        except TypeError as e:
            exceptions.append(e)

        logger.error('Not JSON or YAML:')
        logger.error(text)
        raise Exception(exceptions)

    @classmethod
    def load(cls, path: str) -> FormatterConfig:
        with open(path, 'r') as f:
            text = f.read()
            return cls.from_text(text)


if __name__ == '__main__':
    import os
    FormatterConfig().save(
        os.path.join(os.path.dirname(__file__),
                     'default.formatter.config.yaml'))
