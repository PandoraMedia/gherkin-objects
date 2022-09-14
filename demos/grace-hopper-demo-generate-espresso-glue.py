from gherkin_objects.objects import Step, Feature
import re


# Create a sample feature to demo
feature_text = """
Feature: Authentication
    Scenario: Signing In
        Given the Listener is not signed in
        When the Listener signs in
        Then the Listener should be signed in

    Scenario: Signing out
        Given the Listener is signed in
        When the Listener signs out
        Then the Listener should be signed out
"""


# Pass the sample feature to the Gherkin Objects Library
feature = Feature.from_text(feature_text)


# Example output after running the glue generation script
desired_output = """
@Given("the Listener is not signed in")
public void theListenerIsNotSignedIn() {
    // Implement me!
}
"""


# Create a list of all the steps in the feature
def all_steps(feature: Feature) -> list[Step]:
    result = []
    for scenario in feature.scenarios:
        for step in scenario.steps:
            result.append(step)
    return result


# Filter the list of all steps for uniqueness
# Excludes starting keywords such as: Given, When, Then
def unique_steps(feature: Feature) -> list[Step]:
    seen = set()
    result = []
    for step in all_steps(feature):
        if step.text_without_keyword not in seen:
            result.append(step)
            seen.add(step.text_without_keyword)
    return result


# Converts each step in the unique step list to a glue function
def step_to_espresso_glue(step: Step) -> str:
    result = ""

    # Deconstruct step parts into variables and form into the first function line
    annotation_name = step.real_keyword.capitalize()
    annotation_arg = step.text_without_keyword
    annotation_line = f'@{annotation_name}("{annotation_arg}")'
    result += annotation_line

    # Convert the text of the step to a function name (in this case, camelCase)
    words = re.split(r'\s+', step.text_without_keyword)
    words = [word.capitalize() for word in words]
    words[0] = words[0].lower()
    function_name = "".join(words)

    # Add the function definition and body
    result += f'\npublic void {function_name}() {{'
    result += f'\n\t// Implement me'
    result += f'\n}}'

    return result


# Main function
if __name__ == '__main__':
    steps = unique_steps(feature)

    for step in steps:
        # print('-' * 80)
        # print(step.text_without_keyword)
        print('-' * 80)
        print(step_to_espresso_glue(step))
        print('-' * 80)