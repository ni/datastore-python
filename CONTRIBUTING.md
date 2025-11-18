# Contributing to `datastore-python`

Contributions to `datastore-python` are welcome from all!

`datastore-python` is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/datastore-python/).

`datastore-python` follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

Please remember to sign off your commits (e.g., by using `git commit -s` if you
are using the command line client). This amends your git commit message with a line
of the form `Signed-off-by: Name Lastname <name.lastmail@emailaddress.com>`. Please
include all authors of any given commit into the commit message with a
`Signed-off-by` line. This indicates that you have read and signed the Developer
Certificate of Origin (see below) and are able to legally submit your code to
this repository.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

# Getting Started

## Prerequisites

- _(Optional)_ Install [Visual Studio Code](https://code.visualstudio.com/download)
- Install [Git](https://git-scm.com)
- Install [Python](https://www.python.org/downloads/), any version from the [README](README.md)
- Install [Poetry](https://python-poetry.org/docs/#installation), version >= 2.1.4

## Install the package and its dependencies

Run `poetry install` ([usage](https://python-poetry.org/docs/cli/#install)). This creates an
in-project virtual environment (`.venv`) and installs this package's dependencies and dev-dependencies,
as specified in the `pyproject.toml` and `poetry.lock` files.

```powershell
# Include dependencies for linting, analyzing, and testing the package
poetry install

# Include dependencies for building the documentation (requires Python 3.11 or newer)
poetry install --with docs
```

## Activate the virtual environment (if needed)

- _(Recommended)_ Activate for each command by prefixing the call with `poetry run {command}`
- Activate for the lifetime of the shell in the terminal with `poetry shell`
- Activate in VS Code ([link](https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment))

# Simple Development Loop

```powershell
# Update from main
git checkout main
git pull

# Create a new branch
git switch --create users/{username}/{branch-purpose}

# Install the package dependencies
poetry install --with docs

# ✍ Make source changes

# Run the analyzers -- see files in .github/workflows for details
poetry run nps lint
poetry run mypy
poetry run pyright

# Apply safe fixes
poetry run nps fix

# Run the standalone unit tests
poetry run pytest -v tests\unit

# Run the acceptance tests against an active DataStore service
poetry run pytest -v tests\acceptance

# Build and inspect the documentation
poetry run sphinx-build docs docs/_build --builder html --fail-on-warning
start docs/_build/index.html
```

# Testing

There are pytests in `ni.datastore` that you can run with poetry. There are two directories of tests:
`acceptance` and `unit`.

## Unit Tests

The unit tests in the `unit` folder are the first line of defense to catch regressions. These tests
will run on any PR that is submitted for `ni.datastore`. You can run these tests manually by running:
`poetry run pytest tests\unit`

## Acceptance Tests

Acceptance tests are system level tests that are meant to run against an actual DataStore service.
You can start the DataStore service by building the service from its repo and running it. You
can also install the Measurement Data Services installer on a test machine. If the DataStore service
is not running, these tests will fail. To run the acceptance tests, run this command:
`poetry run pytest tests\acceptance`

> Warning! Running the acceptance tests will publish data and metadata to the default global
> MDS data store location in the Documents folder.

# Publishing on PyPI

You can publish the `ni.datastore` package by creating a GitHub release
in the `datastore-python` repo. Here are the steps to follow to publish the package:

1. From the main GitHub repo page, select "Create a new release".
2. On the "New Release" page, create a new tag using the "Select Tag" drop down. The tag must be the package version, matching the
value found in pyproject.toml. Example: `0.1.0-dev0`.
3. Enter a title in the "Release title" field. The title should contain the package name and
version in the format `ni.datastore <package-version>`. For example: `ni.datastore 0.1.0-dev0`.
4. Click "Generate release notes" and edit the release notes.
  - Delete entries for PRs that do not affect users, such as "chore(deps):" and "fix(deps):" PRs.
  - Consider grouping related entries.
  - Reformat entries to be more readable. For example, change "Blah blah by so-and-so in \#123" to "Blah blah (\#123)".
5. If this is a pre-release release, check the "Set as a pre-release" checkbox.
6. Click "Publish release".
7. Creating a release will start the publish workflow. You can track the
progress of this workflow in the "Actions" page of the GitHub repo.
8. The workflow job that publishes a package to pypi requires code owner approval. This job will automatically send code owners a notification email, then it will wait for them to log in and approve the deployment.
9. After receiving code owner approval, the publish workflow will resume.
10. Once the publish workflow has finished, you should see your release on pypi.

# Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/datastore-python/blob/main/LICENSE)
for details about how `datastore-python` is licensed.
