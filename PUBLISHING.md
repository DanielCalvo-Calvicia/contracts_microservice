# Publishing `contracts_microservice`

This repository is a Python package that exposes the `contracts` package. The import path used by downstream services must come from the built wheel or a Git-based installation of this repository, not from a bare `.py` file copy.

The most important rule is this: if you add, remove, or rename modules under `contracts/`, you must build and publish a new package version, then update the consuming microservice to pin that new version, commit, or tag.

## Package layout

The source tree is rooted at `contracts/`, which is the import package name.

Expected structure:

- `contracts/__init__.py`
- `contracts/api/__init__.py`
- `contracts/api/common/__init__.py`
- `contracts/api/microservices/...`
- `contracts/stream/__init__.py`
- `contracts/stream/common/__init__.py`
- `contracts/stream/microservices/...`

Every package directory must contain an `__init__.py`. Setuptools discovers these packages from `pyproject.toml` using the `contracts*` include pattern.

## Why changes may not show up after `git push`

If another service installs this project through pip, changes are only visible when one of these happens:

- the consuming service installs a new Git commit, branch ref, or tag that contains your changes
- the package version is bumped and a new wheel is built and published
- the consuming environment is not reusing an old cached wheel or locked dependency

If a downstream service still references the old tag, old commit, or old version number, it will keep installing the old code even after you push new source changes.

## How to publish correctly

### 1. Make sure the package metadata is correct

Confirm that `pyproject.toml` includes the package discovery rule:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["contracts*"]
```

This is what ensures that `contracts/api/common/health_check.py`, `contracts/api/common/base.py`, and every other submodule are included in the wheel.

### 2. Bump the package version

Before publishing, change the version in `pyproject.toml`.

Example:

```toml
[project]
name = "contracts-microservice"
version = "0.1.1"
```

Use a new version for every published change. If you reuse the same version, some consumers may keep the old artifact.

### 3. Build the distribution locally

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade build
.\.venv\Scripts\python.exe -m build
```

This creates:

- `dist/contracts_microservice-<version>.tar.gz`
- `dist/contracts_microservice-<version>-py3-none-any.whl`

### 4. Verify the wheel contents

Inspect the wheel before publishing it:

```powershell
.\.venv\Scripts\python.exe -m zipfile -l dist\contracts_microservice-<version>-py3-none-any.whl | Select-String "contracts/api/common/health_check.py"
.\.venv\Scripts\python.exe -m zipfile -l dist\contracts_microservice-<version>-py3-none-any.whl | Select-String "contracts/api/common/base.py"
```

You should see the module paths listed explicitly.

### 5. Publish the artifact

You have two common options:

- publish the wheel to an internal package index or PyPI-compatible feed
- consume the repository directly from Git in the downstream microservice

For a Git-based dependency, pin a commit or tag:

```txt
git+https://github.com/DanielCalvo-Calvicia/contracts_microservice.git@<tag-or-commit>
```

Using a tag is preferred for release stability. Using a commit hash is acceptable for precise reproducibility.

## How another microservice should install it

### Option A: install from a wheel

If you publish the wheel to an artifact feed, downstream services can install it with:

```txt
contracts-microservice==0.1.1
```

### Option B: install directly from Git

In `requirements.windows.txt` or `requirements.linux.txt`:

```txt
git+https://github.com/DanielCalvo-Calvicia/contracts_microservice.git@v0.1.1
```

If you need to pin to an exact commit, use:

```txt
git+https://github.com/DanielCalvo-Calvicia/contracts_microservice.git@<commit-sha>
```

### Option C: install from a local editable checkout during development

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

Editable installs are useful for development, but they are not a substitute for publishing a release artifact.

## How to verify the package installs correctly

After publishing or installing the wheel, validate the import path in a clean environment:

```powershell
.\.venv\Scripts\python.exe -c "import contracts; import contracts.api.common.base as base; print(contracts.__file__); print(base.__file__)"
```

For the new health check module, verify:

```powershell
.\.venv\Scripts\python.exe -c "import contracts.api.microservices.common.health_check as health_check; print(health_check.__file__)"
```

## Recommended release checklist

1. Update or add the module under `contracts/`.
2. Confirm the directory has an `__init__.py` if it is a package.
3. Update `pyproject.toml` version.
4. Build the wheel with `python -m build`.
5. Inspect the wheel with `python -m zipfile -l`.
6. Publish the wheel or tag the Git commit.
7. Update the downstream microservice to point at the new version, tag, or commit.
8. Reinstall in a clean environment and re-run the import check.

## Troubleshooting

- If the wheel only contains `.dist-info`, package discovery is wrong and setuptools is not finding `contracts/`.
- If `pip install` still shows old code, the downstream service is probably pinned to an old version, tag, or commit.
- If `from contracts.api.common.base import Base` fails, the file is present but the symbol name is wrong; `base.py` currently defines `BaseRequest` and `BaseResponse`, not `Base`.
- If the import works locally but not in CI, check whether CI is installing from a stale cache or an old lock file.

## Current repository note

This repository packages the `contracts` namespace. Downstream code should import the module path that actually exists, for example:

```python
from contracts.api.common.base import BaseRequest, BaseResponse
```

not a symbol named `Base` unless that symbol is explicitly defined in the module.