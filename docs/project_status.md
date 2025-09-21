# VidPipe Project Status

This document summarises the current health of the VidPipe codebase after a
fresh review.  It is intended to give new contributors a quick understanding of
what works today, the fixes that were applied, and the next opportunities for
improvement.

## Working Features

- **Composable language core** – the `Lexer`, `Parser`, and `Runtime` modules
  round-trip the pipeline DSL into executable graphs with threading support.
- **Extensive function registry** – `vidpipe.functions` registers camera
  sources, OpenCV based processors, and sinks for display, saving, and
  recording.  The metadata powers both the CLI and the Qt GUI.
- **Command line runner** – `python main.py --cli` can execute inline pipelines
  or scripts stored under `examples/`.
- **Qt editor** – launching `python main.py --gui` provides syntax highlighting,
  a function browser, and an execution console for quick prototyping.
- **Static documentation site** – the TypeScript frontend in `src/` renders the
  curated reading list contained in `docs/computer_vision_pipeline_texts.md`.

## Fixes Applied in This Pass

- Normalised `requirements.txt` so optional development dependencies are listed
  correctly for tooling such as `pip-compile`.
- Added a small `Makefile` with a `make test` helper that exports
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` before invoking `pytest`.  This prevents
  the `pytest-qt` plugin from loading on CI environments that do not ship with
  system OpenGL libraries.

## Suggested Improvements

These items surfaced while reviewing the repository.  Addressing them would
make VidPipe more robust and easier to distribute.

1. **Package layout** – ship a `pyproject.toml` so VidPipe can be installed as a
   package with an entry point (for example `vidpipe-cli`).
2. **Headless friendly GUI hooks** – wrap PyQt6 imports with clearer error
   messages and fallbacks so CLI usage never depends on Qt being available.
3. **Runtime behaviour** – flesh out advanced AST nodes (`ChoiceNode`, `LoopNode`,
   `TimedPipelineNode`) to move beyond their current placeholder
   implementations.
4. **Testing strategy** – expand tests to cover the parser error paths and to
   exercise a single end-to-end pipeline with mocked OpenCV objects.  This will
   improve confidence in contributions without requiring camera hardware.
5. **Documentation polish** – document the built-in functions and their
   parameter expectations in the README (or link to the relevant section in the
   language reference) to make discovering capabilities easier.
6. **Frontend build output** – generate the `docs/main.js` artefact as part of a
   release process rather than committing it, or alternatively wire the static
   page into the README so users know it exists.

## Potential Clean-ups

- Review the number of sample `.vp` files in `examples/`.  Keeping a curated
  subset (for instance a minimal quick-start, a multi-pipeline script, and an
  advanced demo) would simplify maintenance.
- Remove editor placeholder classes such as `PipelineVisualizer` once the GUI
  has a concrete visual editing experience, or hide unfinished tabs from the
  default interface.
- Consider replacing the ad-hoc thread management in `pipeline.py` with
  `concurrent.futures.ThreadPoolExecutor` or `asyncio` primitives to reduce the
  amount of custom synchronisation code that must be maintained.
