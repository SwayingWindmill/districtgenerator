# Repository Guidelines

## Project Structure & Module Organization
`districtgenerator/` contains the library code. Core domain objects live in `districtgenerator/classes/`, shared algorithms in `districtgenerator/functions/`, configuration helpers in `districtgenerator/data_handling/`, and bundled reference datasets in `districtgenerator/data/`. Numbered scripts in `examples/` (`e1_...` through `e9_...`) mirror the intended workflow and are the quickest way to understand the pipeline. Functional coverage lives in `tests/test_examples.py`. Sphinx documentation sources are under `docs/`; shared figures are stored in `img/`.

## Build, Test, and Development Commands
Install the package in editable mode from the repository root:

```bash
python -m pip install -e .
```

Run the functional regression suite:

```bash
python -m unittest tests.test_examples
```

Run a single workflow step during development:

```bash
python examples/e4_generate_buildings.py
```

Build the docs after installing `docs/requirements.txt`:

```bash
cd docs && make html
```

On Windows, use `.\docs\make.bat html`.

## Coding Style & Naming Conventions
Target Python 3.11+ and follow the existing code style: 4-space indentation, `snake_case` for modules and functions, `PascalCase` for classes, and concise inline comments only where logic is not obvious. Keep new example scripts aligned with the current numbered naming pattern, such as `e10_new_feature.py`. No formatter or linter is enforced in project metadata, so match the surrounding style before introducing broad refactors.

## Testing Guidelines
Tests use the standard library `unittest` framework. Add new coverage in `tests/test_*.py` and prefer assertions on returned objects, array shapes, and key attributes over file-existence checks alone. If you touch a workflow step, run `python -m unittest tests.test_examples` and, when practical, add a focused regression test near the changed behavior.

## Commit & Pull Request Guidelines
Recent history uses short, imperative commit subjects in either English or Chinese, such as `update examples` and `fix teaser input`. Keep subjects brief, scoped, and action-oriented. Pull requests should explain the affected workflow, list the commands you ran, link related issues, and mention any changed generated outputs or documentation. Include screenshots only when plots or rendered docs materially changed.

## Data & Configuration Notes
Treat files under `districtgenerator/data/` as reference inputs unless a change is intentional and documented. Avoid committing transient outputs from `districtgenerator/results*` unless they are part of an agreed fixture or documentation update.
