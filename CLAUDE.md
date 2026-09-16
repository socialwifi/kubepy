# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# kubepy

`kubepy` applies Kubernetes YAML definitions through `kubectl`. It reads
already-rendered `.yml` files from one or more directories, merges them by
filename (later directories override earlier ones), applies a small set of
transformations, and shells out to `kubectl`. It does no templating.

It is consumed by `kubeyard`, but it is a standalone, public package on PyPI and
must stay usable by anyone.

## This is a public open-source project

**Never put Social WiFi–specific names, domains, service names, or internal
terminology into this repository.** That includes test fixtures: names like
microservice names or internal hostnames are not allowed.
Use generic names — `web`, `api`, `migrate`, `chosen-namespace`.

The existing `socialwifi` references in `README.md` and `setup.py` are the
project's own GitHub URL and maintainer address; those are fine and stay.

## Core Technologies

- **Language:** Python 3.9–3.12 (see `setup.py` classifiers and `tox.ini`). Do
  not use syntax newer than 3.9.
- **CLI:** `optparse`, not `argparse`. New options go in
  `Options.PARSER_CONFIGURATION`, from which both `add_applier_options` and
  `from_parsed_options` are derived — adding an entry there is usually all that
  is needed.
- **Tests:** `pytest`, no mocking framework. `monkeypatch` is used where a seam
  is genuinely needed.
- **Releases:** `zest.releaser`. `Preparing release X` and
  `Back to development: X` are its commit subjects — **never write those by
  hand**. A hand-written changelog edit is committed as `Update changelog.`

## Project Structure

- `kubepy/appliers.py` — chooses an applier per resource kind and applies it.
  `UniversalDefinitionApplier.get_applier()` is the single choke point where a
  definition's namespace is resolved.
- `kubepy/appliers_options.py` — every applier option and its CLI parsing.
- `kubepy/definition_manager.py` — reads YAML from directories. `__iter__` sorts
  by filename, which is what makes `03_migrate.yml` apply before
  `04_deployment.yml`. Anything that filters definitions must preserve that order.
- `kubepy/definition_transformers.py` — pure functions over definition dicts.
- `kubepy/api.py` — the `kubectl` wrapper. Every call takes `namespace=` and
  omits the flag when it is falsy.
- `kubepy/commands/` — the `kubepy-apply-all` and `kubepy-apply-one` entry points.

Note that transformations in `transform_pod_definition` apply only to
pod-bearing kinds. `Service`, `Secret` and `ConfigMap` go through
`ResourceApplier` untouched.

## Development

```bash
tox run -e lint,py     # linters plus tests on the current interpreter
pytest tests/ -q       # tests only
```

`tox -e py` uses whichever interpreter is active; CI runs the full 3.9–3.12
matrix on push.

## Style Conventions

Linting is `flake8` and `isort`, configured in `setup.cfg`.

- PEP8, max line length **120**.
- Trailing commas in multi-line literals and calls.
- Import whole modules, not individual names: `from kubepy import appliers` then
  `appliers.ClassName`. `isort` uses `force_single_line`, so one import per line.
- Write clean, self-documenting code: short high-level functions calling
  well-named low-level ones, rather than long functions with comments explaining
  each step.
- Keep pure logic separable from anything that shells out, so it can be tested
  without a cluster. `DefinitionsApplier.definitions_to_apply` is the pattern.

## Backward Compatibility

This is a published library with consumers outside this organisation. A new
option must default to the previous behaviour, and new constructor parameters
are keyword-only and added last so no positional call site can break.

## Commits

- **Group by logical change, not by step.** An option and the code that uses it
  are one commit, not two. Do not produce a long series of small commits.
- **When fixing something on this branch, amend the commit that introduced it**
  rather than appending a follow-up commit.
- Subject line, then a **blank line**, then any trailers. Writing a trailer
  directly under the subject folds it into the subject line.
- Do not push, tag, or upload to PyPI without being asked.
