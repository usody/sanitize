# Development

This document is intended to provide an overview of the development process and guidelines for contributing to
the project. Whether you are a seasoned developer or just getting started with coding, we hope that this guide will
be helpful in understanding how to get involved and start contributing to our project.

## About the Project

usody_sanitize is a package, dependency and a cmd tool to erase disk data properly following the standards and 
validations to ensure all data is wiped. We welcome contributions from anyone who is interested in helping to
improve our project, whether it's through submitting bug reports, fixing issues, or adding new features.

## Code Style and Standards

We have established a set of coding standards and best practices that we follow in our project. These standards
are designed to ensure that our code is clean, readable, and maintainable. We encourage all contributors to follow
these standards when submitting code to the project.


## Setup

### Create new release
  
This project uses Poetry to create a new release and publish new releases.

1. Create a new tag version using the poetry command.

```bash
poetry self add poetry-bumpversion
```

2. Set the new version with the
[semantic versioning system](https://semver.org/spec/v1.0.0-beta.html) 
and then build the new release.

```bash
poetry version <version>
poetry build
```

3. Publish it to the PyPi repository.

```bash
poetry publish
```