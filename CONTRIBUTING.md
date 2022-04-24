# Contribution Guide

Thanks for your interest in helping improve Adansons Base!

1. Please check exisintg issues to know someone is already working on same thing.

2. Create a new issue if you want fix a large bug or add a new feature.

3. Create a new branch or fork this repository. (it is good to use the name which is clear what issue is related on that branch. ex: `feature/#100` or `fix/#101`)

4. Apply code formatter `black` and check `pytest` goes well after your working.

5. Create pull request to `main` branch and specify reviewers.

## Detail of development

### 1. Setup environment for develop

Check poetry installation.

If you don't installed poetry yet, please follow [the official instructions](https://python-poetry.org/docs/#installation).

If `poetry --help` works, you're good to go.

```Bash
poetry install
```

### 2. Running tests

```Bash
poetry run pytest tests/
```

### 3. Format source

```Bash
poetry run black .
```