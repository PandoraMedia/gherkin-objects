# Development Roadmap

## Upcoming Release Checkpoints

### Github Initial Release

Outstanding Tasks:

- [ ] License
- [ ] Snyk Github Actions

### PyPI Initial Release - 0.1.0

Outstanding Tasks:

- [ ] HTML documentation published and available to the public 
    - Note: documentation does not have to be complete
    - Publish and update must be integrated with CI

## Backlog

### Code Tasks

- Tag Groups
    - Currently, tags are represented as a 1D array, but it would be more complete to represent them as a 2D array
    - Tags grouped together on a single line convey semantic information that those tags are related in some way
    - It would be better not to throw that information away
   
- GherkinProjectConfig CLI
    - Proposed Usage: `python -m gherkin_objects resolve_gherkin_project_config /path/to/config.json`
    - Ouptut: newline separated list of absolute paths resolved from the given config file 
    - Utility: A list of paths is much more usable by other command line tools than a proprietary json file.  Supports programmatic use cases for this package.

- Lists of child elements should not be directly mutable
    - Currently, `scenario.steps.append(some_step)` can be called directly.  
    - This should not be allowed, since the user is likely to forget to update the `some_step.parent` property, or do so incorrectly 
        - For example, if `some_step.parent` already has a parent, that step must also be removed from the parent
    - `scenario.steps` should not be directly mutable.
    - The proper way to add a step to a scenario is by using the `scenario.add_step` method.
        - Methods like this properly manage the state of the hierarchy.


### Non-Code Tasks (CI, Repo Management, Documentation, etc.)