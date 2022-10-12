#  dependency-track-gh-action

A github action to check if our apps our using dependencies with non-approved licenses. 

## Installation

1. Create a file called `dependency-check-config.yml` to the root of a repo you want to check licenses for. The repo can contain multiple apps inside of a single repo. Use the following as a template for the file contents:
```yaml
apps:
  - {app_name_01}:
      license_file: sample-python-app/licenses.json
      language: python
      dependency_file: sample-python-app/requirements.txt
  - {app_name_02}:
      license_file: sample-ruby-app/licenses.json
      language: ruby
      dependency_file: sample-ruby-app/Gemfile.lock
  - {app_name_03}:
      license_file: sample-node-app/licenses.json
      language: node
      dependency_file: sample-node-app/package-lock.json
block_build: False
allowed_licenses_file: ./allowed_licenses.json
dependency_exceptions_file: ./dependency-exceptions.json
```
2.  Create the following files:
- `license-file_.json` in each app directory. The content of this file should be `{}` for initial setup.
- `dependency-exceptions.json` in the repo root directory. The contents are a list of dependencies you do not want to be scanned for license violations. If there are no exceptions, the file must contain an empty list -> `{}`.
- `allowed_licenses.json` in the repo root directory. The contents are a list of licenses you allow to be used in your apps. by default all other licenses will be restricted. 

3. Create the following github action workflow file in `.github/workflows/dependency-check.yml`:
```yaml
name: Dependency Check

on:
  push:
    branches: [ "dev" ]
  pull_request:
    branches: [ "dev" ]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: chronograph-pe/checkout@v3

      - name: Checkout dependency check repository
        uses: chronograph-pe/checkout@v3
        with:
          repository: chronograph-pe/dependency-track-gh-action
          ref: main
          path: dependency-track-gh-action
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'
            
      - name: Run dependency check
        env:
          DEPENDENCY_CHECK_CONFIG: dependency-check-config.yml
        run: | 
          pip install -r dependency-track-gh-action/requirements.txt
          python dependency-track-gh-action/app/main.py
          # update `chronograph/chronograph` to the name of the repo you are scanning
          cat /home/runner/work/chronograph/chronograph/job_summary.md >> $GITHUB_STEP_SUMMARY
          rm -rf dependency-track-gh-action
      - name: Commit license data to this branch
        uses: chronograph-pe/git-auto-commit-action@v4
```

## Usage
1. Open a PR with changes inside `allowed-licenses.json` with a list of approved dependency licenses. If a dependency has two licenses, the scanner will check the allowed list for both licenses and match on one. 
2. If you need to bypass scanning for a dependency populate `dependency-exceptions.json` with the following format:
```json
{
  # dependency names can have wildcards
  # some dependencies start with @, if so you must not include
  # this in the dependency name. 
  "{dependency_name}": "reason you are creating this exception"
}

example:
{
    "cg-shared*": "Chronograph developed library",
    "*chronograph": "Chronograph developed library",
    "cg-gql*": "Chronograph developed library",
    "cg-lambda*": "Chronograph developed library",
    "ag-grid-*": "Purchased license"
}
```

## Results
License violations will be returned to the github action console and create a job summary. The summary contains:
- License violations: The app name, language, depedency name, and licenses that were not included in the `allowed_licenses.json` file.
- Unknown depedency licenses: The app name, language, depedency name, and licenses where dependency check could not identify a valid spdx license. 
- Dependencies not included in check: A list of dependencies that were added to the `dependency_exceptions.json` file
- All checked dependencies: Every dependency that was scanned in the repo. 

If the `block_build:` flag in `dependency-check-config.yml` is set to True, any license violations will return `exit(`)` and block the build from proceeding. Otherwise, this action will run and return informational results. 

There are occasions when a depedency will not contain it's license information in depedency repositories. In these cases you should look them up and manually add the depedency and license to `licenses.json`. Potential future feature will be looking these up via other sources. 
