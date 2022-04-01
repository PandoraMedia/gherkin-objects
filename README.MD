# Gherkin Objects

The goal of Gherkin Objects is: **To be able to programmatically read, create, and modify gherkin** 



### Gherkin Objects

* Feature
* Scenario
* Step
* Example Table
* Tag
* Comment
* (Potentially others)

There should be one class for each distinct piece of gherkin syntax.

These classes represent an abstract notion of the object, throwing away a lot of information about how it is presented.
No line numbers, no whitespace, just the abstract tree.

### Constructing Gherkin Objects

Each gherkin object should be able to be constructed in at least two ways:
1. Using the class constructor
2. Parsed from raw text

For example:

```
Scenario.from_text("""
    Scenario: scenario
        Given step
""")
```
should be exactly equivalent to:
```
Scenario(name=scenario, steps=[
    Step(keyword='Given', text='step')
])
```

The `from_text` variant should handle any valid, parsable gherkin.  For example:

```
                   Scenario: scenario
Given foo

                # Some random comment

Then bar
```

should parse into exactly the same object as something more reasonably formatted, like

```
Scenario: scenario
    Given foo
    # Some random comment
    Then bar
```

### Writing Gherkin Objects

Since gherkin objects do not contain formatting information, it is impossible to write the data without specifying how to
format it.  This is done with a formatter configuration.  For example:

```
step = Step.from_text("Given foo")
print(step.to_text(FormatterConfig(indent_step=4)))
```

A reasonable default formatter config is provided, but a custom formatter can be specified.  A config file can be specified
using either a command line argument or with the environment variable `GHERKIN_FORMATTER_CONFIG`
