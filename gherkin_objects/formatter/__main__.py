import argparse
import difflib
import logging
import sys

from typing import Iterable, Iterator, List

from gherkin_objects.objects import GherkinProjectConfig, GherkinProject, Feature
from gherkin_objects.formatter import Formatter, FormatterConfig

logger = logging.getLogger(__package__)


def red(string):
    return f'\033[91m{string}\033[0m'


def yellow(string):
    return f'\033[93m{string}\033[0m'


def green(string):
    return f'\033[92m{string}\033[0m'


def apply(
        project: GherkinProject,
        formatter: Formatter,
):
    for feature_file in project.feature_files:
        if not feature_file.text_is_valid_gherkin:
            logger.error(red(f'Invalid Gherkin: {feature_file.path}'))
            continue

        original_text = feature_file.text
        formatted_text = '\n'.join(formatter.format_feature(Feature.from_text(original_text)))
        if original_text == formatted_text:
            logger.info(f'Already formatted: {feature_file.path}')
        else:
            feature_file.overwrite(formatted_text)
            logger.info(green(f'Applied formatting: {feature_file.path}'))


def diff(
        project: GherkinProject,
        formatter: Formatter,
):
    for feature_file in project.feature_files:
        if not feature_file.text_is_valid_gherkin:
            logger.error(red(f'Invalid Gherkin: {feature_file.path}'))
            continue

        original_text = feature_file.text
        formatted_text = '\n'.join(formatter.format_feature(Feature.from_text(original_text)))
        if original_text == formatted_text:
            logger.info(green(f'No diff: {feature_file.path}'))
            continue

        original_lines = original_text.split('\n')
        formatted_lines = formatted_text.split('\n')
        diff_lines = difflib.unified_diff(original_lines, formatted_lines, n=1, lineterm='')

        def format_lines(lines: Iterable[str]) -> Iterator[str]:
            """Transform output of unified_diff: remove unnecessary lines, add color, etc."""
            for line in lines:
                if line.startswith('+++') or line.startswith('---'):
                    # Weird intro lines in unified_diff, not sure what their purpose is
                    continue
                elif line.startswith('-'):
                    # Line removed
                    yield red(line)
                elif line.startswith('+'):
                    # Lined added
                    yield green(line)
                elif line.startswith('@@'):
                    # Very opaque location, for Gherkin this isn't really necessary
                    yield '-' * 80
                else:
                    # Context
                    yield line

        logger.info('=' * 80)
        logger.info(red(f'Diff: {feature_file.path}'))
        logger.info('\n'.join(format_lines(diff_lines)))
        logger.info('=' * 80)


def check(
        project: GherkinProject,
        formatter: Formatter,
):
    unformatted_files = []

    for feature_file in project.feature_files:
        if not feature_file.text_is_valid_gherkin:
            logger.error(red(f'Invalid Gherkin: {feature_file.path}'))
            continue

        original_text = feature_file.text
        formatted_text = '\n'.join(formatter.format_feature(Feature.from_text(original_text)))

        if formatted_text != original_text:
            unformatted_files.append(feature_file)

    if unformatted_files:
        for file in unformatted_files:
            logger.error(red(f'Not formatted: {file.path}'))
        # Allow pipelines to fail with non-zero exit code
        sys.exit(1)


# Parser -------------------------------------------------------------------------------

def parse_args(arg_strings: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser('Grammar Engine')
    parser.add_argument(
        'project_config', type=str,
        help='A JSON file representing a GherkinProjectConfig'
    )
    parser.add_argument(
        'format_config', type=str,
        help='A JSON file representing a GherkinFormatterConfig'
    )

    mode_group_wrapper = parser.add_argument_group(
        'Mode', 'Various levels of application'
    )
    mode_group = mode_group_wrapper.add_mutually_exclusive_group()
    mode_group.set_defaults(apply_mode='check')
    mode_group.add_argument(
        '--apply', action='store_const', dest='apply_mode', const='apply',
        help=(
            'For each file in the project, apply the formatting to the file in place. '
            'This is a potentially destructive operation, so make sure that you are using source control. '
        )
    )
    mode_group.add_argument(
        '--diff', action='store_const', dest='apply_mode', const='diff',
        help=(
            'For each file in the project, print the lines that would change if the formatting '
            'was applied.'
        )
    )
    mode_group.add_argument(
        '--check', action='store_const', dest='apply_mode', const='check',
        help=(
            '<default> '
            'For each file in the project, check if applying format would result in any changes. '
            'If so, then the check fails, and exits with a non-zero code.'
        )
    )
    return parser.parse_args(arg_strings)


def main_from_args(arg_strings: List[str] = None) -> None:
    args = parse_args(arg_strings)

    project_config = GherkinProjectConfig.load(args.project_config)
    project = GherkinProject(paths=project_config.paths)

    format_config = FormatterConfig.load(args.format_config)
    formatter = Formatter(format_config)

    # In the future, this can be altered via command-line flags (e.g. --info vs. --debug)
    logger.setLevel(logging.INFO)

    main(project=project, formatter=formatter, mode=args.apply_mode)


def main(project: GherkinProject, formatter: Formatter, mode: str):
    if mode == 'apply':
        apply(project=project, formatter=formatter)
    elif mode == 'diff':
        diff(project=project, formatter=formatter)
    elif mode == 'check':
        check(project=project, formatter=formatter)
    else:
        raise ValueError(f'Unrecognized apply_mode: {mode}')


# End parser ------------------------------------------------------------------------------------

if __name__ == '__main__':
    main_from_args()
